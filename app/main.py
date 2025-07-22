from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from typing import List, Optional
import os
from .document_loader import DocumentLoader
from .chunking import chunk_text
from .vector_store import add_to_vector_store, similarity_search
from .summarizer import DocumentSummarizer, clean_markdown_formatting
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()
import os
print("MISTRAL_API_KEY loaded:", os.getenv("MISTRAL_API_KEY"))

# Remove Qwen/transformers imports and model initialization

app = FastAPI(title="RAG Document Summarizer", version="1.0.0")

# Add CORS middleware to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to ["http://localhost:5173"] for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>Frontend not built yet.</h1>", status_code=404)

# Serve static files (frontend build)
STATIC_PATH = os.path.abspath("static")
STATIC_ASSETS_PATH = os.path.abspath("static/assets")
print("STATIC_PATH:", STATIC_PATH)
print("STATIC_ASSETS_PATH:", STATIC_ASSETS_PATH)

app.mount("/assets", StaticFiles(directory=STATIC_ASSETS_PATH), name="assets")
app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")

# (Catch-all route removed to ensure static files are served correctly)

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
            print(f"[DEBUG] Summary returned: {summary_result.get('summary')}")
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
    from app.summarizer import DocumentSummarizer
    summarizer = DocumentSummarizer()
    prompt = (
        "You are a helpful assistant. Answer the user's question based primarily on the context below. "
        "If the exact answer is not explicitly stated, infer a concise answer when reasonable, or otherwise respond that the information is unavailable. "
        "Keep the response clear and helpful, in plain sentences without markdown.\n\n"
        "Context:\n" + full_context + "\n\n"
        "Question: " + query + "\n\n"
        "Answer (concise, plain text):"
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