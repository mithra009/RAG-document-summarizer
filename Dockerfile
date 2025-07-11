# Use official Python image
FROM python:3.10-slim

# System dependencies for OCR and PDF processing
RUN apt-get update && \
    apt-get install -y tesseract-ocr poppler-utils curl unzip libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy application code
COPY app/ ./app
COPY requirements.txt .
RUN mkdir -p ./uploaded_docs

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Download and install ngrok
RUN curl -s https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz | tar -xz -C /usr/local/bin

# Expose FastAPI and ngrok dashboard ports
EXPOSE 8000 4040

# Copy entrypoint script
COPY --from=busybox:latest /bin/sh /bin/sh
COPY --from=busybox:latest /bin/sleep /bin/sleep

# Entrypoint script to start both FastAPI and ngrok
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Set environment variables (ngrok authtoken and Mistral API key can be set at runtime)
ENV NGROK_AUTHTOKEN=""
ENV MISTRAL_API_KEY=""

ENTRYPOINT ["/docker-entrypoint.sh"]