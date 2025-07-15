from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from typing import List, Optional
import os
from .document_loader import DocumentLoader
from .chunking import chunk_text
from .vector_store import add_to_vector_store, similarity_search
from .summarizer import DocumentSummarizer, clean_markdown_formatting

# Remove Qwen/transformers imports and model initialization

app = FastAPI(title="RAG Document Summarizer", version="1.0.0")

print("[INFO] RAG Application starting up...")

# Global exception handler to ensure all errors return JSON
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    print(f"[ERROR] Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": f"Internal server error: {str(exc)}"}
    )

# Remove Qwen2-0.5B model instance for queries (CPU-optimized)

def initialize_qwen_model():
    """Initialize Qwen2-0.5B model for query responses (CPU-optimized)"""
    # This function is no longer needed as Qwen model is removed.
    # Keeping it for now, but it will not initialize the model.
    print("[INFO] Qwen model is no longer available. Using simulated responses for queries.")
    return False

# Initialize model on startup (non-blocking)
@app.on_event("startup")
async def startup_event():
    print("[INFO] Starting RAG application...")
    # Initialize model in background to avoid blocking startup
    import asyncio
    asyncio.create_task(initialize_qwen_model_async())

async def initialize_qwen_model_async():
    """Initialize Qwen model asynchronously to avoid blocking startup"""
    try:
        initialize_qwen_model()
    except Exception as e:
        print(f"[WARNING] Model initialization failed: {e}")
        print("[INFO] Application will continue with simulated responses")

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "message": "RAG application is running"}

@app.get("/api")
async def api_root():
    """API root endpoint for health checks"""
    return {"status": "healthy", "message": "RAG application is running"}

@app.get("/ready")
async def ready_check():
    """Immediate health check for Hugging Face Spaces"""
    return {"ready": True, "status": "running"}

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Document Summarizer & Query Resolver</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        * { font-family: 'Inter', sans-serif; }
        body { background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%); color: #e0e0e0; }
        .glass-effect { background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(10px); }
        .toast { position: fixed; top: 1.5rem; right: 1.5rem; z-index: 9999; min-width: 220px; padding: 1rem 1.5rem; border-radius: 0.75rem; font-weight: 500; display: none; }
        .toast-success { background: #22c55e; color: #fff; }
        .toast-error { background: #ef4444; color: #fff; }
        .spinner { border: 4px solid #e0e0e0; border-top: 4px solid #89CFF0; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div id="toast" class="toast"></div>
    <div id="globalSpinner" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-50 hidden"><div class="spinner"></div></div>
    <header class="relative z-10 py-8"><div class="container mx-auto px-6"><div class="text-center"><h1 class="text-6xl font-bold mb-4">AI Document Summarizer</h1><p class="text-xl mb-6">Advanced Document Processing and Query Resolution</p></div></div></header>
    <main class="container mx-auto px-6 pb-16">
        <div class="glass-effect rounded-3xl p-10 mb-8">
            <h2 class="text-4xl font-bold mb-6 text-center">Document Upload</h2>
            <div id="fileUploadArea" class="file-upload-area rounded-2xl p-12 text-center cursor-pointer">
                <svg class="w-16 h-16 mx-auto text-[var(--pastel-blue)] mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
                <p class="text-2xl font-semibold mb-2">Drop your documents here</p>
                <p class="text-gray-400 mb-4">or click to browse</p>
                <div class="flex justify-center space-x-2 text-sm text-gray-500"><span>Supports: PDF, DOCX, PPTX, TXT</span><span>•</span><span>Max size: 100MB</span></div>
            </div>
            <input type="file" id="fileInput" multiple accept=".pdf,.docx,.pptx,.txt" class="hidden">
            <div id="processingStatus" class="mt-6 hidden"><div class="bg-gray-800 rounded-xl p-4"><div class="flex items-center justify-between mb-2"><span class="font-medium">Processing Document...</span><span id="processingPercentage" class="text-[var(--pastel-blue)] font-bold">0%</span></div><div class="w-full bg-gray-700 rounded-full h-2"><div id="progressBar" class="progress-bar h-2 rounded-full" style="width: 0%"></div></div><div id="processingSteps" class="mt-4 space-y-2"></div></div></div>
            <div id="fileList" class="mt-6 space-y-3"></div>
        </div>
        <div id="documentAnalysis" class="glass-effect rounded-3xl p-10 mb-8 hidden"><h2 class="text-4xl font-bold mb-6">Document Analysis</h2><div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8"><div class="chunk-card rounded-xl p-6"><h3 class="text-lg font-semibold mb-2">Document Type</h3><p id="documentType" class="text-gray-400">-</p></div><div class="chunk-card rounded-xl p-6"><h3 class="text-lg font-semibold mb-2">Page Count</h3><p id="pageCount" class="text-gray-400">-</p></div><div class="chunk-card rounded-xl p-6"><h3 class="text-lg font-semibold mb-2">Chunks Created</h3><p id="chunkCount" class="text-gray-400">-</p></div></div><div class="chunk-card rounded-xl p-6"><h3 class="text-xl font-semibold mb-4">Document Summary</h3><div id="documentSummary" class="text-gray-400 leading-relaxed"><div class="processing-animation">Generating summary...</div></div></div></div>
        <div class="glass-effect rounded-3xl p-10 mb-8"><h2 class="text-4xl font-bold mb-6">Query Resolver</h2><div class="mb-6"><div class="relative"><input type="text" id="queryInput" placeholder="Ask anything about your document..." class="w-full px-6 py-4 bg-gray-800 border border-gray-700 rounded-2xl text-white placeholder-gray-500 focus:outline-none focus:border-[var(--pastel-blue)]" disabled><button id="querySubmit" class="absolute right-2 top-2 px-6 py-2 bg-gray-800 hover:bg-[var(--pastel-blue)]/20 rounded-xl text-white font-medium transition-all duration-200 disabled:opacity-50" disabled>Ask</button></div></div><div id="queryHistory" class="space-y-4"></div></div>
    </main>
    <script>
    // Toast notification
    function showToast(message, type = 'success') {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.className = 'toast ' + (type === 'success' ? 'toast-success' : 'toast-error');
        toast.style.display = 'block';
        setTimeout(() => { toast.style.display = 'none'; }, 3500);
    }
    // Global spinner
    function showSpinner() { document.getElementById('globalSpinner').classList.remove('hidden'); }
    function hideSpinner() { document.getElementById('globalSpinner').classList.add('hidden'); }
    // File upload logic
    const fileUploadArea = document.getElementById('fileUploadArea');
    const fileInput = document.getElementById('fileInput');
    const processingStatus = document.getElementById('processingStatus');
    const progressBar = document.getElementById('progressBar');
    const processingPercentage = document.getElementById('processingPercentage');
    const processingSteps = document.getElementById('processingSteps');
    const fileList = document.getElementById('fileList');
    const documentAnalysis = document.getElementById('documentAnalysis');
    const documentType = document.getElementById('documentType');
    const pageCount = document.getElementById('pageCount');
    const chunkCount = document.getElementById('chunkCount');
    const documentSummary = document.getElementById('documentSummary');
    const queryInput = document.getElementById('queryInput');
    const querySubmit = document.getElementById('querySubmit');
    const queryHistory = document.getElementById('queryHistory');
    let currentFilename = '';
    // Drag and drop
    fileUploadArea.addEventListener('click', () => fileInput.click());
    fileUploadArea.addEventListener('dragover', e => { e.preventDefault(); fileUploadArea.classList.add('border-blue-400'); });
    fileUploadArea.addEventListener('dragleave', e => { e.preventDefault(); fileUploadArea.classList.remove('border-blue-400'); });
    fileUploadArea.addEventListener('drop', e => {
        e.preventDefault();
        fileUploadArea.classList.remove('border-blue-400');
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            handleFileUpload();
        }
    });
    fileInput.addEventListener('change', handleFileUpload);
    async function handleFileUpload() {
        if (!fileInput.files.length) return;
        showSpinner();
        processingStatus.classList.remove('hidden');
        progressBar.style.width = '0%';
        processingPercentage.textContent = '0%';
        processingSteps.innerHTML = '<div>Uploading file...</div>';
        fileList.innerHTML = '';
        documentAnalysis.classList.add('hidden');
        queryInput.disabled = true;
        querySubmit.disabled = true;
        try {
            const file = fileInput.files[0];
            const formData = new FormData();
            formData.append('file', file);
            const response = await fetch('/upload', { method: 'POST', body: formData });
            if (!response.ok) throw new Error('Upload failed');
            const data = await response.json();
            currentFilename = data.filename;
            progressBar.style.width = '100%';
            processingPercentage.textContent = '100%';
            processingSteps.innerHTML += '<div>Processing complete!</div>';
            setTimeout(() => { processingStatus.classList.add('hidden'); }, 1000);
            // Show analysis
            documentAnalysis.classList.remove('hidden');
            documentType.textContent = data.classification;
            pageCount.textContent = data.page_estimate;
            chunkCount.textContent = data.chunk_count;
            documentSummary.textContent = data.summary;
            queryInput.disabled = false;
            querySubmit.disabled = false;
            showToast('File uploaded and processed!', 'success');
        } catch (err) {
            showToast('Error: ' + (err.message || 'Failed to upload/process file'), 'error');
            processingStatus.classList.add('hidden');
        } finally {
            hideSpinner();
        }
    }
    // Query logic
    querySubmit.addEventListener('click', handleQuery);
    queryInput.addEventListener('keydown', e => { if (e.key === 'Enter') handleQuery(); });
    async function handleQuery() {
        const query = queryInput.value.trim();
        if (!query || !currentFilename) return;
        queryInput.disabled = true;
        querySubmit.disabled = true;
        showSpinner();
        const userBubble = document.createElement('div');
        userBubble.className = 'query-bubble p-4 mb-2';
        userBubble.textContent = query;
        queryHistory.appendChild(userBubble);
        const responseBubble = document.createElement('div');
        responseBubble.className = 'response-bubble p-4 mb-4';
        responseBubble.textContent = 'Thinking...';
        queryHistory.appendChild(responseBubble);
        try {
            const formData = new FormData();
            formData.append('filename', currentFilename);
            formData.append('query', query);
            const response = await fetch('/query', { method: 'POST', body: formData });
            if (!response.ok) throw new Error('Query failed');
            const data = await response.json();
            responseBubble.textContent = data.answer;
            showToast('Query answered!', 'success');
        } catch (err) {
            responseBubble.textContent = 'Error: ' + (err.message || 'Failed to get answer');
            showToast('Error: ' + (err.message || 'Failed to get answer'), 'error');
        } finally {
            queryInput.disabled = false;
            querySubmit.disabled = false;
            hideSpinner();
        }
    }
    </script>
</body>
</html>
"""

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document with improved error handling and logging"""
    try:
        print(f"[INFO] Received file: {file.filename}")
        upload_dir = "uploaded_docs"
        try:
            os.makedirs(upload_dir, exist_ok=True)
        except Exception as e:
            print(f"[ERROR] Failed to create upload directory: {e}")
            return JSONResponse(status_code=500, content={"error": f"Failed to create upload directory: {str(e)}"})

        file_location = os.path.join(upload_dir, file.filename)
        try:
            with open(file_location, "wb") as f:
                f.write(await file.read())
            print(f"[INFO] File saved to: {file_location}")
        except Exception as e:
            print(f"[ERROR] Failed to save file: {e}")
            return JSONResponse(status_code=500, content={"error": f"Failed to save file: {str(e)}"})

        try:
            loader = DocumentLoader(file_location)
            documents = loader.load()
            print(f"[INFO] Loaded {len(documents)} document(s) from file.")
            # Get real page/slide count
            page_count = loader.get_page_count() or 1
        except Exception as e:
            print(f"[ERROR] Document loading failed: {e}")
            return JSONResponse(status_code=400, content={"error": f"Document loading failed: {str(e)}"})

        try:
            text_content = " ".join([doc.page_content for doc in documents])
            print(f"[INFO] Extracted text content, length: {len(text_content)} characters.")
        except Exception as e:
            print(f"[ERROR] Failed to extract text: {e}")
            return JSONResponse(status_code=500, content={"error": f"Failed to extract text: {str(e)}"})

        try:
            summarizer = DocumentSummarizer()
            summary_result = await summarizer.summarize_document(text_content)
            print(f"[INFO] Document summarized. Classification: {summary_result.get('classification')}")
        except Exception as e:
            print(f"[ERROR] Summarization failed: {e}")
            return JSONResponse(status_code=500, content={"error": f"Summarization failed: {str(e)}"})

        try:
            chunks = chunk_text(text_content)
            print(f"[INFO] Created {len(chunks)} chunk(s) for vector store.")
        except Exception as e:
            print(f"[ERROR] Chunking failed: {e}")
            return JSONResponse(status_code=500, content={"error": f"Chunking failed: {str(e)}"})

        try:
            add_to_vector_store(chunks)
            print(f"[INFO] Chunks added to vector store.")
        except Exception as e:
            print(f"[ERROR] Vector store addition failed: {e}")
            return JSONResponse(status_code=500, content={"error": f"Vector store addition failed: {str(e)}"})

        # Store chunks for small document queries (in-memory, keyed by filename)
        if not hasattr(app.state, 'doc_chunks'):
            app.state.doc_chunks = {}
        app.state.doc_chunks[file.filename] = chunks

        return {
            "filename": file.filename,
            "summary": summary_result["summary"],
            "classification": summary_result["classification"],
            "chunk_count": summary_result["chunk_count"],
            "processing_method": summary_result["processing_method"],
            "page_estimate": page_count
        }

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Unexpected error processing document: {str(e)}"}
        )

@app.post("/summarize")
async def summarize_document(filename: str = Form(...)):
    """Generate summary for a specific document"""
    try:
        file_location = f"uploaded_docs/{filename}"
        if not os.path.exists(file_location):
            return JSONResponse(
                status_code=404,
                content={"error": "Document not found"}
            )
        
        # Load and process document
        loader = DocumentLoader(file_location)
        documents = loader.load()
        text_content = " ".join([doc.page_content for doc in documents])
        
        # Generate summary
        summarizer = DocumentSummarizer()
        summary_result = await summarizer.summarize_document(text_content)
        
        return {
            "filename": filename,
            "summary": summary_result["summary"],
            "classification": summary_result["classification"],
            "chunk_count": summary_result["chunk_count"],
            "processing_method": summary_result["processing_method"]
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error summarizing document: {str(e)}"}
        )

@app.post("/query")
async def query_document(filename: str = Form(...), query: str = Form(...)):
    """Query a document using RAG pipeline"""
    try:
        # Try to get all chunks for small documents
        chunks = None
        if hasattr(app.state, 'doc_chunks') and filename in app.state.doc_chunks:
            chunks = app.state.doc_chunks[filename]

        # If we have all chunks, check if the document is small
        is_small_doc = False
        if chunks is not None:
            # Heuristic: if number of chunks < 20, treat as small document
            is_small_doc = len(chunks) < 20

        if is_small_doc:
            # Use all chunks as context
            context_chunks = chunks
        else:
            # Use similarity search for large documents or if chunks not available
            search_results = similarity_search(query, top_k=5)
            context_chunks = search_results.get("documents", [[]])[0]

        context = " ".join(context_chunks)

        # Generate a more intelligent response based on the actual context
        if not context_chunks:
            answer = f"I couldn't find specific information in the document that directly answers your question: '{query}'. The document may not contain relevant content for this query."
        else:
            # Create a more contextual response based on the found chunks
            answer = generate_contextual_response(query, context_chunks)

        return {
            "filename": filename,
            "query": query,
            "answer": answer,
            "context_chunks": len(context_chunks)
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error processing query: {str(e)}"}
        )

def generate_contextual_response(query: str, context_chunks: List[str]) -> str:
    full_context = " ".join(context_chunks)
    # Remove any truncation logic here
    from app.summarizer import DocumentSummarizer
    summarizer = DocumentSummarizer()
    prompt = (
        "You are a helpful assistant that answers questions based on document content. Answer only to the point, with a short, concise, and accurate response. Do not add unnecessary details. Use plain text format without markdown.\n\nQuestion: "
        f"{query}\n\nContext: {full_context}\n\nShort Answer (to the point):"
    )
    return summarizer.call_mistral_api(prompt)

def generate_simulated_response(query: str, full_context: str) -> str:
    """Generate a simulated response when Qwen2-0.5B is not available"""
    
    # Analyze the query type and generate appropriate response
    query_lower = query.lower()
    
    if any(word in query_lower for word in ["key", "main", "important", "points", "summary"]):
        # Extract key points from the context
        sentences = full_context.split('. ')
        key_points = []
        for sentence in sentences[:min(5, len(sentences))]:  # Allow up to 5 key points
            if len(sentence.strip()) > 10:  # Include more meaningful sentences
                key_points.append(sentence.strip())
        
        if key_points:
            answer = f"Based on the document content, here are the key points:\n\n"
            for i, point in enumerate(key_points, 1):
                answer += f"{i}. {point}\n"
        else:
            answer = f"The document contains information about your query, but I couldn't extract specific key points from the available content."
    
    elif any(word in query_lower for word in ["explain", "what is", "how", "why"]):
        # Provide explanatory response with more content
        if len(full_context) > 300:
            # Take more content for explanations
            relevant_part = full_context[:1000] + "..." if len(full_context) > 1000 else full_context
            answer = f"Based on the document, here's what I found regarding your question '{query}':\n\n{relevant_part}"
        else:
            answer = f"The document provides the following information about your query: {full_context}"
    
    elif any(word in query_lower for word in ["conclusion", "result", "find", "found"]):
        # Look for conclusions or results
        sentences = full_context.split('. ')
        conclusion_sentences = []
        for sentence in sentences:
            if any(word in sentence.lower() for word in ["conclude", "result", "therefore", "thus", "finally", "overall"]):
                conclusion_sentences.append(sentence)
        
        if conclusion_sentences:
            answer = f"Based on the document analysis, here are the conclusions related to your query:\n\n"
            for sentence in conclusion_sentences[:3]:  # Allow up to 3 conclusions
                answer += f"• {sentence}\n"
        else:
            answer = f"The document contains relevant information about your query, but I couldn't identify specific conclusions from the available content."
    
    else:
        # General response with more content
        if len(full_context) > 300:
            # Take more sentences for general responses
            sentences = full_context.split('. ')
            summary_sentences = sentences[:min(8, len(sentences))]  # Increased from 4 to 8 sentences
            summary = '. '.join(summary_sentences)
            answer = f"Regarding your question '{query}', the document contains the following relevant information:\n\n{summary}"
        else:
            answer = f"The document provides this information related to your query: {full_context}"
    
    # Clean markdown formatting from the answer
    answer = clean_markdown_formatting(answer)
    return answer 