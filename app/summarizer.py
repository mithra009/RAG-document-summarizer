from typing import List, Dict, Any
import asyncio
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Remove top-level import of transformers and torch
# from transformers import AutoTokenizer, AutoModelForCausalLM
# import torch

def clean_markdown_formatting(text: str) -> str:
    """
    Clean markdown formatting from text and convert to plain text
    
    Args:
        text: Text that may contain markdown formatting
        
    Returns:
        Cleaned plain text without markdown
    """
    if not text:
        return text
    
    # Remove markdown headers (# ## ### etc.)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # Remove bold formatting (**text** or __text__)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'__(.*?)__', r'\1', text)
    
    # Remove italic formatting (*text* or _text_)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'_(.*?)_', r'\1', text)
    
    # Remove code formatting (`text`)
    text = re.sub(r'`(.*?)`', r'\1', text)
    
    # Remove links [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    # Remove inline links [text] -> text
    text = re.sub(r'\[([^\]]+)\]', r'\1', text)
    
    # Remove strikethrough ~~text~~
    text = re.sub(r'~~(.*?)~~', r'\1', text)
    
    # Remove blockquotes (> text)
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    
    # Remove horizontal rules (---, ***, ___)
    text = re.sub(r'^[-*_]{3,}$', '', text, flags=re.MULTILINE)
    
    # Clean up extra whitespace
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Remove excessive line breaks
    text = re.sub(r' +', ' ', text)  # Remove multiple spaces
    text = re.sub(r'\n +', '\n', text)  # Remove leading spaces after line breaks
    
    # Clean up the text
    text = text.strip()
    
    return text

class DocumentSummarizer:
    def __init__(self, llm_model=None, chunk_size=1200, chunk_overlap=200):
        """
        Initialize the document summarizer (CPU-optimized version)
        
        Args:
            llm_model: Qwen2-0.5B model instance (CPU-friendly)
            chunk_size: Size of text chunks for processing (optimized for CPU)
            chunk_overlap: Overlap between chunks (reduced for memory efficiency)
        """
        self.llm_model = llm_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
        )
        self.tokenizer = None
        self.model = None
        # Initialize Qwen2-0.5B model if not provided (CPU-friendly)
        if self.llm_model is None:
            try:
                print("[INFO] Loading Qwen2-0.5B model (CPU-optimized)...")
                from transformers import AutoTokenizer, AutoModelForCausalLM
                import torch
                self.tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2-0.5B-Instruct")
                self.model = AutoModelForCausalLM.from_pretrained(
                    "Qwen/Qwen2-0.5B-Instruct",
                    torch_dtype=torch.float32,  # Use float32 for CPU
                    device_map="cpu",  # Force CPU usage
                    trust_remote_code=True,
                    low_cpu_mem_usage=True,  # Reduce memory usage
                    offload_folder="offload"  # Enable model offloading
                )
                print("[INFO] Qwen2-0.5B model loaded successfully on CPU!")
            except Exception as e:
                print(f"[WARNING] Failed to load Qwen2-0.5B model: {e}")
                print("[INFO] Falling back to simulated responses")
                self.tokenizer = None
                self.model = None
        
    def classify_document_size(self, text: str) -> Dict[str, Any]:
        """
        Classify document as small or large based on content length
        
        Args:
            text: Document text content
            
        Returns:
            Dict with classification info
        """
        words = len(text.split())
        pages_estimate = words // 500  # Rough estimate: 500 words per page
        is_large = pages_estimate > 15
        
        return {
            "is_large": is_large,
            "word_count": words,
            "page_estimate": pages_estimate,
            "classification": "Large Document" if is_large else "Small Document"
        }
    
    def create_chunks(self, text: str) -> List[Document]:
        """
        Create text chunks using RecursiveCharacterTextSplitter
        
        Args:
            text: Document text content
            
        Returns:
            List of Document chunks
        """
        chunks = self.text_splitter.split_text(text)
        return [Document(page_content=chunk, metadata={"chunk_id": i}) 
                for i, chunk in enumerate(chunks)]
    
    def _truncate_text_for_model(self, text: str, max_tokens: int = 4000) -> str:
        """
        Truncate text to fit within model context limits (increased limits for better summaries)
        
        Args:
            text: Text to truncate
            max_tokens: Maximum tokens allowed (increased from 2000)
            
        Returns:
            Truncated text
        """
        if self.tokenizer is None:
            # Fallback: simple character-based truncation with higher limit
            return text[:max_tokens * 4]  # Rough estimate: 4 chars per token
        
        # Tokenize the text
        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        
        if len(tokens) <= max_tokens:
            return text
        
        # Truncate to max_tokens and decode back
        truncated_tokens = tokens[:max_tokens]
        truncated_text = self.tokenizer.decode(truncated_tokens, skip_special_tokens=True)
        
        # Try to end at a sentence boundary
        last_period = truncated_text.rfind('.')
        if last_period > len(truncated_text) * 0.8:  # If period is in last 20%
            truncated_text = truncated_text[:last_period + 1]
        
        return truncated_text
    
    async def generate_chunk_summary(self, chunk: Document) -> str:
        import torch
        """
        Generate summary for a single chunk using Qwen2-0.5B (CPU-optimized)
        
        Args:
            chunk: Document chunk to summarize
            
        Returns:
            Summary text for the chunk
        """
        if self.model is None or self.tokenizer is None:
            # Fallback simulation for when model is not available
            return self._simulate_chunk_summary(chunk.page_content)
        
        try:
            # Truncate chunk content to prevent input overflow (increased limit)
            truncated_content = self._truncate_text_for_model(chunk.page_content, max_tokens=3000)
            
            # Enhanced prompt for better chunk summaries (CPU-optimized) - Plain text format without word limits
            prompt = f"""<|im_start|>system
You are an expert document summarizer. Create comprehensive summaries that capture key information from text chunks. Provide summaries in plain text format without markdown formatting.

Guidelines:
1. Identify main topics and key points
2. Extract important facts and concepts
3. Use clear, professional language
4. Include all relevant information
5. Write in plain text, not markdown
6. Avoid repetition but be thorough
7. Provide detailed summaries without artificial word limits

<|im_end|>
<|im_start|>user
Please summarize the following text chunk in plain text format (comprehensive):

{truncated_content}

Summary:
<|im_end|>
<|im_start|>assistant
"""
            
            # Generate response using Qwen2-0.5B with reduced tokens for faster processing
            inputs = self.tokenizer(prompt, return_tensors="pt")
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_new_tokens=500,  # Increased for more comprehensive summaries
                    temperature=0.3,     # Lower temperature for more focused output
                    top_p=0.8,           # Reduced for faster sampling
                    do_sample=True,
                    repetition_penalty=1.05,  # Reduced penalty for speed
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
            
            # Clean up the response and remove markdown formatting
            response = response.strip()
            if response.endswith('<|im_end|>'):
                response = response[:-10].strip()
            
            # Clean markdown formatting
            response = clean_markdown_formatting(response)
            
            return response if response else self._simulate_chunk_summary(chunk.page_content)
            
        except Exception as e:
            print(f"[WARNING] Error generating chunk summary with Qwen2-0.5B: {e}")
            return self._simulate_chunk_summary(chunk.page_content)
    
    def _simulate_chunk_summary(self, text: str) -> str:
        """
        Simulate chunk summary generation (fallback when LLM not available)
        
        Args:
            text: Text to summarize
            
        Returns:
            Simulated summary
        """
        # Create a balanced summary simulation
        words = text.split()
        if len(words) < 30:
            return text
        
        # Split into sentences and take key information
        sentences = text.split('. ')
        if len(sentences) <= 2:
            return text
        
        # For longer text, create a meaningful summary
        if len(sentences) > 4:
            # Take first sentence, middle sentence, and last sentence for context
            summary_sentences = [sentences[0]]  # Introduction
            middle_idx = len(sentences) // 2
            summary_sentences.append(sentences[middle_idx])  # Key point
            summary_sentences.append(sentences[-1])  # Conclusion
        else:
            # For shorter text, take first 2 sentences
            summary_sentences = sentences[:2]
        
        summary = '. '.join(summary_sentences)
        return summary + ('.' if not summary.endswith('.') else '')
    
    async def summarize_small_document(self, chunks: List[Document]) -> str:
        import torch
        """
        Summarize small documents (≤15 pages) by summarizing all chunks and combining
        
        Args:
            chunks: List of document chunks
            
        Returns:
            Combined document summary
        """
        print(f"Processing small document with {len(chunks)} chunks...")
        
        # Generate summaries for all chunks
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            print(f"Summarizing chunk {i+1}/{len(chunks)}...")
            summary = await self.generate_chunk_summary(chunk)
            chunk_summaries.append(summary)
        
        # Combine all chunk summaries
        combined_summary = " ".join(chunk_summaries)
        
        # Generate final summary from combined summaries
        final_summary = await self.generate_final_summary(combined_summary, "small")
        
        return final_summary
    
    async def summarize_large_document(self, chunks: List[Document]) -> str:
        import torch
        """
        Summarize large documents (>15 pages) using hierarchical summarization
        
        Args:
            chunks: List of document chunks
            
        Returns:
            Hierarchical document summary
        """
        print(f"Processing large document with {len(chunks)} chunks using hierarchical summarization...")
        
        # Step 1: Generate chunk-level summaries
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            print(f"Generating chunk summary {i+1}/{len(chunks)}...")
            summary = await self.generate_chunk_summary(chunk)
            chunk_summaries.append(summary)
        
        # Step 2: Group summaries into sections (for very large documents)
        if len(chunk_summaries) > 50:
            section_summaries = await self._create_section_summaries(chunk_summaries)
        else:
            section_summaries = chunk_summaries
        
        # Step 3: Generate section-level summaries
        section_level_summaries = []
        for i, section in enumerate(section_summaries):
            print(f"Generating section summary {i+1}/{len(section_summaries)}...")
            if isinstance(section, list):
                combined_section = " ".join(section)
            else:
                combined_section = section
            section_summary = await self.generate_chunk_summary(
                Document(page_content=combined_section, metadata={"section_id": i})
            )
            section_level_summaries.append(section_summary)
        
        # Step 4: Generate final hierarchical summary
        final_combined = " ".join(section_level_summaries)
        final_summary = await self.generate_final_summary(final_combined, "large")
        
        return final_summary
    
    async def _create_section_summaries(self, chunk_summaries: List[str]) -> List[List[str]]:
        """
        Group chunk summaries into sections for very large documents
        
        Args:
            chunk_summaries: List of chunk summaries
            
        Returns:
            List of section summaries (each section is a list of chunk summaries)
        """
        section_size = max(10, len(chunk_summaries) // 10)  # Create ~10 sections
        sections = []
        
        for i in range(0, len(chunk_summaries), section_size):
            section = chunk_summaries[i:i + section_size]
            sections.append(section)
        
        return sections
    
    async def generate_final_summary(self, combined_text: str, doc_type: str) -> str:
        import torch
        """
        Generate final summary from combined text using Qwen2-0.5B (CPU-optimized)
        
        Args:
            combined_text: Combined text to summarize
            doc_type: Type of document (small/large)
            
        Returns:
            Final document summary
        """
        if self.model is None or self.tokenizer is None:
            return self._simulate_final_summary(combined_text, doc_type)
        
        try:
            # Truncate combined text to prevent input overflow (increased limit)
            truncated_text = self._truncate_text_for_model(combined_text, max_tokens=4000)
            
            # Enhanced prompt for better final summaries (CPU-optimized) - Plain text format without word limits
            prompt = f"""<|im_start|>system
You are an expert document analyst. Create comprehensive, well-structured document summaries in plain text format without markdown formatting. Provide detailed summaries without artificial word limits.

Guidelines:
1. Organize with clear sections using simple text formatting
2. Cover major themes and important details thoroughly
3. Use clear, professional language
4. Highlight key insights and takeaways
5. Provide appropriate context for technical terms
6. Write in plain text, not markdown
7. Be comprehensive and detailed
8. Avoid repetition but include all important information

<|im_end|>
<|im_start|>user
Please create a comprehensive summary of this {doc_type} document in plain text format (detailed):

{truncated_text}

Provide a structured summary with these sections:
1. Document Overview
2. Key Themes
3. Important Findings
4. Key Points
5. Conclusions

<|im_end|>
<|im_start|>assistant
"""
            
            # Generate response using Qwen2-0.5B with reduced tokens for faster processing
            inputs = self.tokenizer(prompt, return_tensors="pt")
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_new_tokens=600,  # Increased for more comprehensive summaries
                    temperature=0.3,     # Lower temperature for focused output
                    top_p=0.8,           # Reduced for faster sampling
                    do_sample=True,
                    repetition_penalty=1.05,  # Reduced penalty for speed
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
            
            # Clean up the response and remove markdown formatting
            response = response.strip()
            if response.endswith('<|im_end|>'):
                response = response[:-10].strip()
            
            # Clean markdown formatting
            response = clean_markdown_formatting(response)
            
            return response if response else self._simulate_final_summary(combined_text, doc_type)
            
        except Exception as e:
            print(f"[WARNING] Error generating final summary with Qwen2-0.5B: {e}")
            return self._simulate_final_summary(combined_text, doc_type)
    
    def _simulate_final_summary(self, combined_text: str, doc_type: str) -> str:
        """
        Simulate final summary generation (fallback when LLM not available)
        
        Args:
            combined_text: Combined text to summarize
            doc_type: Type of document (small/large)
            
        Returns:
            Simulated final summary
        """
        # Create a balanced final summary
        sentences = combined_text.split('. ')
        
        if len(sentences) <= 3:
            return combined_text
        
        # For small documents, take key sentences for better context
        if doc_type == "small":
            if len(sentences) <= 5:
                summary_sentences = sentences
            else:
                # Take introduction, key point, and conclusion for small docs
                summary_sentences = [sentences[0]]  # Introduction
                middle_idx = len(sentences) // 2
                summary_sentences.append(sentences[middle_idx])  # Key point
                summary_sentences.append(sentences[-1])  # Conclusion
        else:
            # For large documents, create a comprehensive summary
            if len(sentences) <= 6:
                summary_sentences = sentences
            else:
                # Take introduction, 2 key points, and conclusion
                summary_sentences = [sentences[0]]  # Introduction
                # Take 2 key points from different parts
                quarter_idx = len(sentences) // 4
                three_quarter_idx = (3 * len(sentences)) // 4
                summary_sentences.append(sentences[quarter_idx])  # First key point
                summary_sentences.append(sentences[three_quarter_idx])  # Second key point
                summary_sentences.append(sentences[-1])  # Conclusion
        
        summary = '. '.join(summary_sentences)
        return summary + ('.' if not summary.endswith('.') else '')
    
    async def summarize_document(self, text: str) -> Dict[str, Any]:
        """
        Main method to summarize a document
        
        Args:
            text: Document text content
            
        Returns:
            Dict with summary results
        """
        # Classify document size
        classification = self.classify_document_size(text)
        
        # Create chunks
        chunks = self.create_chunks(text)
        
        # Generate summary based on document size
        if classification["is_large"]:
            summary = await self.summarize_large_document(chunks)
            processing_method = "Hierarchical Summarization"
        else:
            summary = await self.summarize_small_document(chunks)
            processing_method = "Chunk-wise Summarization"
        
        return {
            "summary": summary,
            "classification": classification["classification"],
            "word_count": classification["word_count"],
            "page_estimate": classification["page_estimate"],
            "chunk_count": len(chunks),
            "processing_method": processing_method
        }

async def summarize_text(text: str, llm_model=None) -> Dict[str, Any]:
    """
    Convenience function to summarize text
    
    Args:
        text: Text to summarize
        llm_model: Optional LLM model instance
        
    Returns:
        Dict with summary results
    """
    summarizer = DocumentSummarizer(llm_model=llm_model)
    return await summarizer.summarize_document(text) 