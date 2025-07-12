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
RUN mkdir -p ./uploaded_docs

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose FastAPI port
EXPOSE 8000

# Set environment variables
ENV MISTRAL_API_KEY=""

# Start FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]