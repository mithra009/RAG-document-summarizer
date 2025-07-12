---
title: RAG Document Summarizer
emoji: 📄
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
short_description: Advanced AI-powered document summarization and question answering using RAG
---

# RAG Document Summarizer

A modern, production-ready Retrieval-Augmented Generation (RAG) application for document summarization and question answering. Built with FastAPI, LangChain, and Mistral AI API, this project enables advanced document processing, chunking, vector search, and AI-powered summarization and querying.

## Features
- **Document Upload:** Supports PDF, DOCX, PPTX, and TXT files
- **OCR Support:** Extracts text from scanned PDFs using Tesseract OCR
- **Chunking:** Splits documents into manageable chunks for efficient processing
- **Vector Store:** Embeds and stores chunks for fast similarity search
- **AI Summarization:** Uses Mistral AI API for high-quality summaries and answers
- **Modern UI:** Clean, responsive web interface

## How to Use
1. Upload your documents (PDF, DOCX, PPTX, TXT)
2. The system will automatically process and chunk your documents
3. Ask questions about your documents using the query interface
4. Get AI-powered summaries and answers based on your document content

## Technical Stack
- **Backend:** FastAPI, Python 3.10+
- **AI/ML:** LangChain, Mistral AI API, Sentence Transformers
- **Vector Database:** ChromaDB
- **Document Processing:** PyPDF2, pdfplumber, unstructured, pytesseract
- **Frontend:** Modern HTML/CSS/JavaScript with Tailwind CSS

## Environment Variables
- `MISTRAL_API_KEY`: Required for AI-powered features (get from [Mistral AI](https://mistral.ai/))

## License
MIT License
