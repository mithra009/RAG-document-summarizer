# RAG Document Summarizer

A modern Retrieval-Augmented Generation (RAG) web app for uploading documents, getting AI-generated summaries and asking questions.

---

## Features
* Upload **PDF / DOCX / PPTX / TXT** documents
* Automatic OCR for scanned PDFs
* Chunking + embeddings stored in Chroma DB
* AI summary + question-answering powered by **Mistral-AI**
* FastAPI backend + React/Vite frontend (Tailwind CSS)
* Ready for container deployment with a single Dockerfile

---

## Local Development

```bash
# 1. Clone & enter repo
# 2. Backend
python -m venv .venv && source .venv/bin/activate  # or 'venv\Scripts\activate' on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload  # backend on http://localhost:8000

# 3. Frontend (in another terminal)
cd frontend
npm ci
npm run dev  # Vite dev-server on http://localhost:5173
```

Set environment variables in a `.env` file (backend reads it automatically):

```
MISTRAL_API_KEY=your_key_here
VITE_API_URL=http://localhost:8000
```

---

## Build & Run with Docker

```bash
# Build image (multi-stage – no local Node/Python needed)
docker build -t rag-app .

# Run container, mapping port 8000
docker run -p 8000:8000 --name rag rag-app
```

Optional `docker-compose.yml` (single service):

```yaml
version: "3.9"
services:
  rag-app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - uploaded_docs:/app/uploaded_docs
volumes:
  uploaded_docs:
```

---

## Environment Variables
| Variable | Description |
|----------|-------------|
| `MISTRAL_API_KEY` | Required for Mistral calls |
| `VITE_API_URL` | Frontend base URL for backend (defaults to `/`) |

---

## License
MIT
