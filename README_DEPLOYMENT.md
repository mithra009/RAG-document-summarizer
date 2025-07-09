# 🚀 RAG Application Docker Deployment Guide

This guide will help you deploy the RAG (Retrieval-Augmented Generation) application using Docker with ngrok for external access.

## 📋 Prerequisites

- **Docker Desktop** installed and running
- **Docker Compose** (usually included with Docker Desktop)
- **Git** (for cloning the repository)
- **Mistral AI API Key** (required for AI features)
- **Optional**: ngrok auth token for unlimited connections

## 🏗️ Architecture

The deployment includes:
- **RAG Application**: FastAPI app with OCR, AI summarization, and document processing
- **Mistral AI API**: Cloud-based AI model for summaries and query responses
- **Ngrok**: Provides secure tunnels for external access
- **Tesseract OCR**: Pre-installed in the Docker container
- **Poppler**: PDF processing utilities

## 🚀 Quick Start

### Windows (PowerShell)

```powershell
# Deploy with ngrok authtoken and Mistral API key for external access
.\deploy.ps1 -NgrokAuthToken "your_ngrok_authtoken_here" -MistralApiKey "your_mistral_api_key_here"

# Deploy without authtoken (free tier, limited connections)
.\deploy.ps1 -MistralApiKey "your_mistral_api_key_here"

# Build only
.\deploy.ps1 -BuildOnly

# Stop services
.\deploy.ps1 -StopOnly
```

### Linux/Mac (Bash)

```bash
# Deploy with ngrok authtoken and Mistral API key for external access
./deploy.sh --token "your_ngrok_authtoken_here" --mistral-key "your_mistral_api_key_here"

# Deploy without authtoken (free tier, limited connections)
./deploy.sh --mistral-key "your_mistral_api_key_here"

# Build only
./deploy.sh --build-only

# Stop services
./deploy.sh --stop-only
```

### Manual Docker Commands

```bash
# Set environment variables
export MISTRAL_API_KEY="your_mistral_api_key_here"
export NGROK_AUTHTOKEN="your_ngrok_authtoken_here"  # Optional

# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

## 🌐 Access URLs

After successful deployment, you can access:

- **Local Application**: http://localhost:8000
- **Ngrok Dashboard**: http://localhost:4040
- **Public URL**: Will be displayed in the deployment output

## 🔧 Configuration

### Environment Variables

You can customize the deployment by setting environment variables:

```bash
# Set Mistral AI API key (REQUIRED)
export MISTRAL_API_KEY="your_mistral_api_key_here"

# Set ngrok auth token (optional)
export NGROK_AUTHTOKEN="your_token_here"

# Set Tesseract path (usually not needed)
export TESSERACT_CMD="/usr/bin/tesseract"
```

### Mistral AI API Configuration

The application uses Mistral AI API for:
- Document summarization
- Query responses
- Context-aware answers

**Important:** The `MISTRAL_API_KEY` environment variable is required for all AI-powered features.

### Ngrok Configuration

The ngrok service is configured to:
- Automatically create a tunnel to the RAG application
- Expose the dashboard on port 4040
- Use the provided auth token (if available)

## 📁 Directory Structure

```
RAG LC/
├── app/                    # Application source code
├── uploaded_docs/          # Uploaded documents (persistent)
├── Dockerfile             # Docker image definition
├── docker-compose.yml     # Multi-service orchestration
├── deploy.ps1            # Windows deployment script
├── deploy.sh             # Linux/Mac deployment script
└── requirements.txt      # Python dependencies
```

## 🔍 Troubleshooting

### Common Issues

1. **Docker not running**
   ```
   Error: Docker is not running
   Solution: Start Docker Desktop
   ```

2. **Port already in use**
   ```
   Error: Port 8000 or 4040 already in use
   Solution: Stop other services using these ports
   ```

3. **Mistral API key not set**
   ```
   Error: Mistral API key is required
   Solution: Set MISTRAL_API_KEY environment variable
   ```

4. **Ngrok tunnel not created**
   ```
   Check: http://localhost:4040
   Solution: Wait a few minutes for ngrok to initialize
   ```

5. **OCR not working**
   ```
   Check: Tesseract is pre-installed in the container
   Solution: Check application logs for OCR errors
   ```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f rag-app
docker-compose logs -f ngrok

# Recent logs
docker-compose logs --tail=100
```

### Health Checks

The application includes health checks:
- **RAG App**: Checks if the web server is responding
- **Ngrok**: Monitors tunnel status

## 🔒 Security Considerations

1. **Mistral API Key**: Keep your API key secure and never commit it to version control
2. **Ngrok Free Tier**: Limited connections, consider paid plan for production
3. **Public Access**: The ngrok URL is publicly accessible
4. **File Uploads**: Documents are stored in the `uploaded_docs` directory

## 📊 Monitoring

### Application Metrics

- **Health Check**: http://localhost:8000/ (should return HTML)
- **Ngrok Status**: http://localhost:4040 (tunnel information)
- **Container Status**: `docker-compose ps`

### Performance Tips

1. **API Calls**: Mistral AI API calls may have rate limits
2. **Memory Usage**: The application uses ~1-2GB RAM (reduced from local models)
3. **Storage**: No local model storage required
4. **CPU**: OCR processing is CPU-intensive

## 🛠️ Development

### Local Development

For development without Docker:

```bash
# Install dependencies
pip install -r requirements.txt

# Set Mistral API key
export MISTRAL_API_KEY="your_mistral_api_key_here"

# Install Tesseract (system-specific)
# Windows: Use the installer
# Linux: sudo apt-get install tesseract-ocr
# Mac: brew install tesseract

# Run locally
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
``` 