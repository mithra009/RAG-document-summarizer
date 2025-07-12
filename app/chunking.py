from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list:
    """
    Split text into chunks using RecursiveCharacterTextSplitter
    
    Args:
        text: Text to split into chunks
        chunk_size: Size of each chunk
        chunk_overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    try:
        if not text or not text.strip():
            print("[WARNING] Empty or None text provided for chunking")
            return []
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        
        chunks = text_splitter.split_text(text)
        print(f"[INFO] Created {len(chunks)} chunks from text")
        return chunks
    except Exception as e:
        print(f"[ERROR] Text chunking failed: {e}")
        # Return the original text as a single chunk as fallback
        return [text] if text else [] 