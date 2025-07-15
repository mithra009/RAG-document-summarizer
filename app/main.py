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
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf-lib/1.17.1/pdf-lib.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mammoth/1.5.0/mammoth.browser.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        :root {
            --pastel-blue: #89CFF0;
            --pastel-green: #A8E6CF;
            --pastel-purple: #D7A9E3;
            --pastel-pink: #F5B7B1;
        }
        
        * {
            font-family: 'Inter', sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
            color: #e0e0e0;
            line-height: 1.6;
        }
        
        .glass-effect {
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .file-upload-area {
            background: linear-gradient(135deg, rgba(30, 30, 30, 0.5) 0%, rgba(50, 50, 50, 0.5) 100%);
            border: 2px dashed rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
        }
        
        .file-upload-area:hover {
            border-color: var(--pastel-blue);
        }
        
        .chunk-card {
            background: linear-gradient(135deg, rgba(0, 0, 0, 0.2) 0%, rgba(0, 0, 0, 0.1) 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .progress-bar {
            background: linear-gradient(90deg, var(--pastel-blue) 0%, var(--pastel-green) 100%);
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
        }
        
        .floating-element {
            animation: float 5s ease-in-out infinite;
        }
        
        .query-bubble {
            background: linear-gradient(135deg, #333 0%, #444 100%);
            border-radius: 20px 20px 5px 20px;
        }
        
        .response-bubble {
            background: linear-gradient(135deg, rgba(0, 0, 0, 0.2) 0%, rgba(0, 0, 0, 0.1) 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px 20px 20px 5px;
        }
        
        h1 {
            font-size: 3.75rem;
            font-weight: 700;
        }
        
        h2 {
            font-size: 2.25rem;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <!-- Background Effects -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none">
        <div class="absolute top-20 left-10 w-64 h-64 bg-[var(--pastel-blue)] rounded-full opacity-5 blur-3xl floating-element"></div>
        <div class="absolute top-40 right-20 w-48 h-48 bg-[var(--pastel-green)] rounded-full opacity-5 blur-2xl floating-element" style="animation-delay: 1s;"></div>
        <div class="absolute bottom-20 left-1/3 w-56 h-56 bg-[var(--pastel-purple)] rounded-full opacity-5 blur-3xl floating-element" style="animation-delay: 2s;"></div>
    </div>

    <!-- Header -->
    <header class="relative z-10 py-8">
        <div class="container mx-auto px-6">
            <div class="text-center">
                <h1 class="text-6xl font-bold mb-4">AI Document Summarizer</h1>
                <p class="text-xl mb-6">Advanced Document Processing and Query Resolution</p>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto px-6 pb-16">
        <!-- File Upload Section -->
        <div class="glass-effect rounded-3xl p-10 mb-8">
            <h2 class="text-4xl font-bold mb-6 text-center">Document Upload</h2>
            
            <div id="fileUploadArea" class="file-upload-area rounded-2xl p-12 text-center cursor-pointer">
                <div class="mb-4">
                    <svg class="w-16 h-16 mx-auto text-[var(--pastel-blue)] mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                    </svg>
                </div>
                <p class="text-2xl font-semibold mb-2">Drop your documents here</p>
                <p class="text-gray-400 mb-4">or click to browse</p>
                <div class="flex justify-center space-x-2 text-sm text-gray-500">
                    <span>Supports: PDF, DOCX, PPTX, TXT</span>
                    <span>•</span>
                    <span>Max size: 100MB</span>
                </div>
            </div>
            
            <input type="file" id="fileInput" multiple accept=".pdf,.docx,.pptx,.txt" class="hidden">
            
            <!-- Processing Status -->
            <div id="processingStatus" class="mt-6 hidden">
                <div class="bg-gray-800 rounded-xl p-4">
                    <div class="flex items-center justify-between mb-2">
                        <span class="font-medium">Processing Document...</span>
                        <span id="processingPercentage" class="text-[var(--pastel-blue)] font-bold">0%</span>
                    </div>
                    <div class="w-full bg-gray-700 rounded-full h-2">
                        <div id="progressBar" class="progress-bar h-2 rounded-full" style="width: 0%"></div>
                    </div>
                    <div id="processingSteps" class="mt-4 space-y-2"></div>
                </div>
            </div>
            
            <!-- File List -->
            <div id="fileList" class="mt-6 space-y-3"></div>
        </div>

        <!-- Document Analysis & Summary -->
        <div id="documentAnalysis" class="glass-effect rounded-3xl p-10 mb-8 hidden">
            <h2 class="text-4xl font-bold mb-6">Document Analysis</h2>
            
            <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                <div class="chunk-card rounded-xl p-6">
                    <h3 class="text-lg font-semibold mb-2">Document Type</h3>
                    <p id="documentType" class="text-gray-400">-</p>
                </div>
                
                <div class="chunk-card rounded-xl p-6">
                    <h3 class="text-lg font-semibold mb-2">Page Count</h3>
                    <p id="pageCount" class="text-gray-400">-</p>
                </div>
                
                <div class="chunk-card rounded-xl p-6">
                    <h3 class="text-lg font-semibold mb-2">Chunks Created</h3>
                    <p id="chunkCount" class="text-gray-400">-</p>
                </div>
            </div>
            
            <div class="chunk-card rounded-xl p-6">
                <h3 class="text-xl font-semibold mb-4">Document Summary</h3>
                <div id="documentSummary" class="text-gray-400 leading-relaxed">
                    <div class="processing-animation">Generating summary...</div>
                </div>
            </div>
        </div>

        <!-- Query Interface -->
        <div class="glass-effect rounded-3xl p-10 mb-8">
            <h2 class="text-4xl font-bold mb-6">Query Resolver</h2>
            
            <div class="mb-6">
                <div class="relative">
                    <input 
                        type="text" 
                        id="queryInput" 
                        placeholder="Ask anything about your document..."
                        class="w-full px-6 py-4 bg-gray-800 border border-gray-700 rounded-2xl text-white placeholder-gray-500 focus:outline-none focus:border-[var(--pastel-blue)]"
                        disabled
                    >
                    <button 
                        id="querySubmit" 
                        class="absolute right-2 top-2 px-6 py-2 bg-gray-800 hover:bg-[var(--pastel-blue)]/20 rounded-xl text-white font-medium transition-all duration-200 disabled:opacity-50"
                        disabled
                    >
                        Ask
                    </button>
                </div>
                <div class="mt-3 flex flex-wrap gap-2">
                    <button class="suggestion-btn px-4 py-2 bg-gray-800 hover:bg-[var(--pastel-blue)]/20 rounded-full text-sm text-gray-400 transition-all duration-200">
                        What are the key points?
                    </button>
                    <button class="suggestion-btn px-4 py-2 bg-gray-800 hover:bg-[var(--pastel-blue)]/20 rounded-full text-sm text-gray-400 transition-all duration-200">
                        Explain the main concepts
                    </button>
                    <button class="suggestion-btn px-4 py-2 bg-gray-800 hover:bg-[var(--pastel-blue)]/20 rounded-full text-sm text-gray-400 transition-all duration-200">
                        What conclusions are drawn?
                    </button>
                </div>
            </div>
            
            <div id="queryHistory" class="space-y-4 max-h-96 overflow-y-auto"></div>
        </div>
    </main>

    <script>
        // Global state
        let documents = [];
        let currentDocument = null;
        let documentChunks = [];
        let isProcessing = false;

        // Initialize application
        document.addEventListener('DOMContentLoaded', function() {
            initializeFileUpload();
            initializeQueryInterface();
            initializeSuggestions();
        });

        function initializeFileUpload() {
            const fileUploadArea = document.getElementById('fileUploadArea');
            const fileInput = document.getElementById('fileInput');

            fileUploadArea.addEventListener('click', () => {
                if (!isProcessing) {
                    fileInput.click();
                }
            });

            fileInput.addEventListener('change', (e) => {
                handleFiles(e.target.files);
            });

            fileUploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                fileUploadArea.classList.add('dragover');
            });

            fileUploadArea.addEventListener('dragleave', () => {
                fileUploadArea.classList.remove('dragover');
            });

            fileUploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                fileUploadArea.classList.remove('dragover');
                handleFiles(e.dataTransfer.files);
            });
        }

        function initializeQueryInterface() {
            const queryInput = document.getElementById('queryInput');
            const querySubmit = document.getElementById('querySubmit');

            querySubmit.addEventListener('click', () => {
                const query = queryInput.value.trim();
                if (query) {
                    processQuery(query);
                    queryInput.value = '';
                }
            });

            queryInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    querySubmit.click();
                }
            });
        }

        function initializeSuggestions() {
            document.querySelectorAll('.suggestion-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const query = btn.textContent.trim();
                    document.getElementById('queryInput').value = query;
                    document.getElementById('querySubmit').click();
                });
            });
        }

        async function handleFiles(files) {
            if (isProcessing) return;

            for (const file of files) {
                if (validateFile(file)) {
                    await processDocument(file);
                }
            }
        }

        function validateFile(file) {
            const allowedTypes = [
                'application/pdf',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                'text/plain'
            ];

            if (!allowedTypes.includes(file.type)) {
                showNotification('Unsupported file type. Please upload PDF, DOCX, PPTX, or TXT files.', 'error');
                return false;
            }

            if (file.size > 100 * 1024 * 1024) {
                showNotification('File too large. Maximum size is 100MB.', 'error');
                return false;
            }

            return true;
        }

        async function processDocument(file) {
            isProcessing = true;
            showProcessingStatus();

            try {
                updateProcessingStep('Uploading document...', 10);
                
                // Create FormData for file upload
                const formData = new FormData();
                formData.append('file', file);
                
                updateProcessingStep('Processing document...', 30);
                
                // Send file to backend
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    let errorMessage = 'Upload failed';
                    let errorText = '';
                    try {
                        // Try to parse as JSON
                        const errorData = await response.json();
                        errorMessage = errorData.error || 'Upload failed';
                    } catch (jsonError) {
                        // Only try to read as text if .json() fails and errorText is still empty
                        if (!errorText) {
                            errorText = await response.text();
                            console.error('Non-JSON error response:', errorText);
                        }
                        errorMessage = `Server error (${response.status}): ${response.statusText}`;
                    }
                    throw new Error(errorMessage);
                }
                
                updateProcessingStep('Analyzing content...', 70);
                
                // Only read the response body once
                const result = await response.json();
                
                updateProcessingStep('Processing complete!', 100);
                
                const document = {
                    id: Date.now(),
                    name: file.name,
                    type: getFileType(file.name),
                    size: file.size,
                    pageCount: result.page_estimate || 1,
                    chunks: result.chunk_count || 0,
                    summary: result.summary,
                    classification: result.classification,
                    processingMethod: result.processing_method
                };
                
                documents.push(document);
                currentDocument = document;
                
                displayDocumentInfo(document);
                enableQueryInterface();
                
                setTimeout(() => {
                    hideProcessingStatus();
                    showNotification('Document processed successfully!', 'success');
                }, 1000);
                
            } catch (error) {
                console.error('Error processing document:', error);
                showNotification('Error processing document: ' + error.message, 'error');
                hideProcessingStatus();
            }
            
            isProcessing = false;
        }

        function getFileType(filename) {
            const extension = filename.split('.').pop().toLowerCase();
            const typeMap = {
                'pdf': 'PDF Document',
                'docx': 'Word Document',
                'pptx': 'PowerPoint Presentation',
                'txt': 'Text Document'
            };
            return typeMap[extension] || 'Unknown';
        }

        function displayDocumentInfo(docData) {
            document.getElementById('documentType').textContent = docData.type;
            document.getElementById('pageCount').textContent = `${docData.pageCount} pages (${docData.classification})`;
            document.getElementById('chunkCount').textContent = `${docData.chunks} chunks`;
            
            const summaryElement = document.getElementById('documentSummary');
            summaryElement.innerHTML = '';
            
            let i = 0;
            const summary = docData.summary;
            const typeInterval = setInterval(() => {
                if (i < summary.length) {
                    summaryElement.textContent += summary.charAt(i);
                    i++;
                } else {
                    clearInterval(typeInterval);
                }
            }, 20);
            
            document.getElementById('documentAnalysis').classList.remove('hidden');
        }

        function enableQueryInterface() {
            document.getElementById('queryInput').disabled = false;
            document.getElementById('querySubmit').disabled = false;
            document.querySelectorAll('.suggestion-btn').forEach(btn => {
                btn.disabled = false;
            });
        }

        async function processQuery(query) {
            if (!currentDocument) return;
            
            addQueryToHistory(query);
            
            try {
                const formData = new FormData();
                formData.append('filename', currentDocument.name);
                formData.append('query', query);
                
                const response = await fetch('/query', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    let errorMessage = 'Query failed';
                    try {
                        const errorData = await response.json();
                        errorMessage = errorData.error || 'Query failed';
                    } catch (jsonError) {
                        // If response is not JSON (e.g., HTML error page), get text content
                        const errorText = await response.text();
                        console.error('Non-JSON error response:', errorText);
                        errorMessage = `Server error (${response.status}): ${response.statusText}`;
                    }
                    throw new Error(errorMessage);
                }
                
                const result = await response.json();
                addResponseToHistory(result.answer);
                
            } catch (error) {
                console.error('Error processing query:', error);
                addResponseToHistory('Sorry, I encountered an error while processing your query. Please try again.');
            }
        }

        function addQueryToHistory(query) {
            const historyContainer = document.getElementById('queryHistory');
            const queryElement = document.createElement('div');
            queryElement.className = 'query-bubble p-4 ml-8';
            queryElement.innerHTML = `
                <div class="flex items-start">
                    <div class="flex-shrink-0 w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center mr-3 mt-1">
                        <span class="text-sm">U</span>
                    </div>
                    <div class="flex-1">
                        <p class="font-medium">${query}</p>
                        <p class="text-sm text-gray-500 mt-1">${new Date().toLocaleTimeString()}</p>
                    </div>
                </div>
            `;
            historyContainer.appendChild(queryElement);
            historyContainer.scrollTop = historyContainer.scrollHeight;
        }

        function addResponseToHistory(response) {
            const historyContainer = document.getElementById('queryHistory');
            const responseElement = document.createElement('div');
            responseElement.className = 'response-bubble p-4 mr-8';
            responseElement.innerHTML = `
                <div class="flex items-start">
                    <div class="flex-shrink-0 w-8 h-8 bg-[var(--pastel-blue)] rounded-full flex items-center justify-center mr-3 mt-1">
                        <span class="text-sm">A</span>
                    </div>
                    <div class="flex-1">
                        <div class="typing-indicator mb-2">
                            <span class="inline-block w-2 h-2 bg-[var(--pastel-blue)] rounded-full animate-pulse"></span>
                            <span class="inline-block w-2 h-2 bg-[var(--pastel-blue)] rounded-full animate-pulse ml-1" style="animation-delay: 0.2s;"></span>
                            <span class="inline-block w-2 h-2 bg-[var(--pastel-blue)] rounded-full animate-pulse ml-1" style="animation-delay: 0.4s;"></span>
                        </div>
                        <p class="response-text hidden leading-relaxed"></p>
                        <p class="text-sm text-gray-500 mt-2">${new Date().toLocaleTimeString()}</p>
                    </div>
                </div>
            `;
            historyContainer.appendChild(responseElement);
            historyContainer.scrollTop = historyContainer.scrollHeight;
            
            setTimeout(() => {
                const typingIndicator = responseElement.querySelector('.typing-indicator');
                const responseText = responseElement.querySelector('.response-text');
                
                typingIndicator.classList.add('hidden');
                responseText.classList.remove('hidden');
                
                let i = 0;
                const typeInterval = setInterval(() => {
                    if (i < response.length) {
                        responseText.textContent += response.charAt(i);
                        i++;
                        historyContainer.scrollTop = historyContainer.scrollHeight;
                    } else {
                        clearInterval(typeInterval);
                    }
                }, 30);
            }, 1500);
        }

        function showProcessingStatus() {
            document.getElementById('processingStatus').classList.remove('hidden');
            document.getElementById('fileUploadArea').style.opacity = '0.5';
            document.getElementById('fileUploadArea').style.pointerEvents = 'none';
        }

        function hideProcessingStatus() {
            document.getElementById('processingStatus').classList.add('hidden');
            document.getElementById('fileUploadArea').style.opacity = '1';
            document.getElementById('fileUploadArea').style.pointerEvents = 'auto';
        }

        function updateProcessingStep(message, percentage) {
            const stepsContainer = document.getElementById('processingSteps');
            const progressBar = document.getElementById('progressBar');
            const percentageDisplay = document.getElementById('processingPercentage');
            
            progressBar.style.width = percentage + '%';
            percentageDisplay.textContent = percentage + '%';
            
            const stepElement = document.createElement('div');
            stepElement.className = 'flex items-center text-sm text-gray-400';
            stepElement.innerHTML = `
                <div class="w-2 h-2 bg-[var(--pastel-blue)] rounded-full mr-3 flex-shrink-0"></div>
                <span>${message}</span>
            `;
            stepsContainer.appendChild(stepElement);
            
            while (stepsContainer.children.length > 3) {
                stepsContainer.removeChild(stepsContainer.firstChild);
            }
        }

        function showNotification(message, type = 'info') {
            const notification = document.createElement('div');
            const bgColor = type === 'error' ? 'bg-red-500' : type === 'success' ? 'bg-green-500' : 'bg-blue-500';
            
            notification.className = `fixed top-4 right-4 ${bgColor} text-white px-6 py-3 rounded-lg shadow-lg z-50 transform translate-x-full transition-transform duration-300`;
            notification.textContent = message;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.classList.remove('translate-x-full');
            }, 100);
            
            setTimeout(() => {
                notification.classList.add('translate-x-full');
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            }, 4000);
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
    if len(full_context) > 8000:
        sentences = full_context.split('. ')
        if len(sentences) > 20:
            relevant_sentences = sentences[:5] + sentences[-5:]
            full_context = '. '.join(relevant_sentences)
    # Use Mistral API for contextual response
    from app.summarizer import DocumentSummarizer
    summarizer = DocumentSummarizer()
    prompt = f"You are a helpful assistant that answers questions based on document content. Provide comprehensive, accurate answers using the given context. Use plain text format without markdown. Provide detailed responses that fully address the user's question.\n\nQuestion: {query}\n\nContext: {full_context}\n\nAnswer (comprehensive, plain text):"
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