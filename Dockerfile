# -------- Stage 1: Build Frontend --------
FROM node:20-slim AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend ./
RUN npm run build

# -------- Stage 2: Build Backend & final image --------
FROM python:3.10-slim AS backend

# Environment
ARG MISTRAL_API_KEY
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MISTRAL_API_KEY=${MISTRAL_API_KEY}

# Create non-root user
RUN addgroup --system app && adduser --system --ingroup app app
WORKDIR /app

# System deps (for PDF/text extraction etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libreoffice poppler-utils libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Backend source
COPY app ./app

# Static frontend
COPY --from=frontend-builder /frontend/dist ./static

# Create uploads directory with correct ownership
RUN mkdir -p /app/uploaded_docs && chown -R app:app /app/uploaded_docs

# Uploaded docs volume (optional)
VOLUME ["/app/uploaded_docs"]

USER app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]