# RAG Document Summarizer

A modern, production-ready Retrieval-Augmented Generation (RAG) application for document summarization and question answering. Built with FastAPI, LangChain, and HuggingFace Transformers, this project enables advanced document processing, chunking, vector search, and LLM-powered summarization and querying.

## Features
- **Document Upload:** Supports PDF, DOCX, PPTX, and TXT files
- **OCR Support:** Extracts text from scanned PDFs using Tesseract OCR
- **Chunking:** Splits documents into manageable chunks for efficient processing
- **Vector Store:** Embeds and stores chunks for fast similarity search
- **LLM Summarization:** Uses Qwen2-0.5B (or fallback) for high-quality summaries and answers
- **Modern UI:** Clean, responsive web interface

## Requirements
- Python 3.10+ (Python 3.12 supported)
- [Poppler](https://github.com/oschwartz10612/poppler-windows) (for PDF to image conversion)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (for scanned PDF OCR)

Install required Python packages:
```sh
pip install -r requirements.txt
```

## Setup
1. **Install Poppler:**
   - Windows: Download and extract Poppler, add `bin/` to your PATH.
   - Linux/macOS: `sudo apt install poppler-utils` or `brew install poppler`.
2. **Install Tesseract:**
   - Windows: Download and install, add to PATH.
   - Linux/macOS: `sudo apt install tesseract-ocr` or `brew install tesseract`.
3. **Clone this repo and install Python dependencies:**
   ```sh
   git clone <your-repo-url>
   cd <repo-directory>
   pip install -r requirements.txt
   ```
4. **Run the app:**
   ```sh
   uvicorn app.main:app --reload
   ```
   Visit [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Usage
- Upload documents via the web UI.
- Summaries and chunked content are generated automatically.
- Ask questions about your documents using the query interface.

## Deployment
- Docker and deployment scripts are included for production use.
- See `README_DEPLOYMENT.md` for advanced deployment instructions.

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---
**Note:**
- Do not commit large files, sample documents, or sensitive data.
- For PDF/OCR support, ensure Poppler and Tesseract are installed on your system. 
