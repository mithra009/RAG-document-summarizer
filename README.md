# RAG Document Summarizer

A modern, production-ready Retrieval-Augmented Generation (RAG) application for document summarization and question answering. Built with FastAPI, LangChain, and Mistral AI API, this project enables advanced document processing, chunking, vector search, and AI-powered summarization and querying.

## Features
- **Document Upload:** Supports PDF, DOCX, PPTX, and TXT files
- **OCR Support:** Extracts text from scanned PDFs using Tesseract OCR
- **Chunking:** Splits documents into manageable chunks for efficient processing
- **Vector Store:** Embeds and stores chunks for fast similarity search
- **AI Summarization:** Uses Mistral AI API for high-quality summaries and answers
- **Modern UI:** Clean, responsive web interface

## Requirements
- Python 3.10+ (Python 3.12 supported)
- [Poppler](https://github.com/oschwartz10612/poppler-windows) (for PDF to image conversion)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (for scanned PDF OCR)
- **Mistral AI API Key:** Required for AI-powered features

Install required Python packages:
```sh
pip install -r requirements.txt
```

## Setup
1. **Get Mistral AI API Key:**
   - Sign up at [Mistral AI](https://mistral.ai/)
   - Generate an API key from your dashboard
   - Set the API key as an environment variable: `export MISTRAL_API_KEY="your_api_key_here"`

2. **Install Poppler:**
   - Windows: Download and extract Poppler, add `bin/` to your PATH.
   - Linux/macOS: `sudo apt install poppler-utils` or `brew install poppler`.

3. **Install Tesseract:**
   - Windows: Download and install, add to PATH.
   - Linux/macOS: `sudo apt install tesseract-ocr` or `brew install tesseract`.

4. **Clone this repo and install Python dependencies:**
   ```sh
   git clone <your-repo-url>
   cd <repo-directory>
   pip install -r requirements.txt
   ```

5. **Run the app:**
   ```sh
   uvicorn app.main:app --reload
   ```
   Visit [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Usage
- Upload documents via the web UI.
- Summaries and chunked content are generated automatically using Mistral AI.
- Ask questions about your documents using the query interface.

## Deployment
- Docker and deployment scripts are included for production use.
- See `README_DEPLOYMENT.md` for advanced deployment instructions.
- **Important:** Set the `MISTRAL_API_KEY` environment variable in your deployment environment.

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](LICENSE)

---
**Note:**
- Do not commit large files, sample documents, or sensitive data.
- For PDF/OCR support, ensure Poppler and Tesseract are installed on your system.
- The Mistral AI API key is required for all AI-powered features. 