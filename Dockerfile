# Use official Python image
FROM python:3.10-slim

# System dependencies for OCR and PDF processing
RUN apt-get update && \
    apt-get install -y tesseract-ocr poppler-utils libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy application code
COPY app/ ./app
COPY requirements.txt .
RUN mkdir -p ./uploaded_docs && chmod 777 ./uploaded_docs

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose FastAPI port
EXPOSE 7860

# Set environment variables
ENV MISTRAL_API_KEY=""

RUN mkdir -p /app/cache && chmod 777 /app/cache
ENV TRANSFORMERS_CACHE=/app/cache

# Create a startup script
RUN echo '#!/bin/bash\n\
echo "Starting RAG Document Summarizer..."\n\
sleep 5\n\
exec uvicorn app.main:app --host 0.0.0.0 --port 7860 --timeout-keep-alive 75\n\
' > /app/start.sh && chmod +x /app/start.sh

# Start FastAPI application with startup script
CMD ["/app/start.sh"]