# 🚀 RAG Application Docker Deployment Guide

This guide will help you deploy the RAG (Retrieval-Augmented Generation) application using Docker with ngrok for external access.

## 📋 Prerequisites

- **Docker Desktop** installed and running
- **Docker Compose** (usually included with Docker Desktop)
- **Git** (for cloning the repository)
- **Optional**: ngrok auth token for unlimited connections

## 🏗️ Architecture

The deployment includes:
- **RAG Application**: FastAPI app with OCR, AI summarization, and document processing
- **Ngrok**: Provides secure tunnels for external access
- **Tesseract OCR**: Pre-installed in the Docker container
- **Poppler**: PDF processing utilities

## 🚀 Quick Start

### Windows (PowerShell)

```powershell
# Deploy with ngrok authtoken for external access
.\deploy.ps1 -NgrokAuthToken "your_ngrok_authtoken_here"

# Deploy without authtoken (free tier, limited connections)
.\deploy.ps1

# Build only
.\deploy.ps1 -BuildOnly

# Stop services
.\deploy.ps1 -StopOnly
```

### Linux/Mac (Bash)

```bash
# Deploy with ngrok authtoken for external access
./deploy.sh --token "your_ngrok_authtoken_here"

# Deploy without authtoken (free tier, limited connections)
./deploy.sh

# Build only
./deploy.sh --build-only

# Stop services
./deploy.sh --stop-only
```

### Manual Docker Commands

```bash
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
# Set ngrok auth token
export NGROK_AUTHTOKEN="your_token_here"

# Set Tesseract path (usually not needed)
export TESSERACT_CMD="/usr/bin/tesseract"
```

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
├── offload/               # Model cache (persistent)
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

3. **Ngrok tunnel not created**
   ```
   Check: http://localhost:4040
   Solution: Wait a few minutes for ngrok to initialize
   ```

4. **OCR not working**
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

1. **Ngrok Free Tier**: Limited connections, consider paid plan for production
2. **Public Access**: The ngrok URL is publicly accessible
3. **File Uploads**: Documents are stored in the `uploaded_docs` directory
4. **Model Cache**: AI models are cached in the `offload` directory

## 📊 Monitoring

### Application Metrics

- **Health Check**: http://localhost:8000/ (should return HTML)
- **Ngrok Status**: http://localhost:4040 (tunnel information)
- **Container Status**: `docker-compose ps`

### Performance Tips

1. **First Run**: Initial startup may take 5-10 minutes (model downloads)
2. **Memory Usage**: The application uses ~2-4GB RAM
3. **Storage**: Models are cached for faster subsequent starts
4. **CPU**: OCR processing is CPU-intensive

## 🛠️ Development

### Local Development

For development without Docker:

```bash
# Install dependencies
pip install -r requirements.txt

# Install Tesseract (system-specific)
# Windows: Use the installer
# Linux: sudo apt-get install tesseract-ocr
# Mac: brew install tesseract

# Run locally
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Building Custom Images

```bash
# Build with custom tag
docker build -t rag-app:custom .

# Run custom image
docker run -p 8000:8000 rag-app:custom
```

## 📞 Support

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Verify Docker is running: `docker version`
3. Check port availability: `netstat -an | grep 8000`
4. Review the troubleshooting section above

## 🔄 Updates

To update the application:

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose up -d --build
```

## 📝 License

This deployment setup is part of the RAG Application project. 

## Ngrok Configuration for External Access

### Getting Your Ngrok Authtoken

1. **Sign up for ngrok**: Visit [ngrok.com](https://ngrok.com) and create a free account
2. **Get your authtoken**: 
   - Go to [https://dashboard.ngrok.com/get-started/your-authtoken](https://dashboard.ngrok.com/get-started/your-authtoken)
   - Copy your authtoken (looks like: `2abc123def456ghi789jkl`)

### Using Ngrok Authtoken

**Option 1: Command Line Parameter (Recommended)**
```bash
# Windows
.\deploy.ps1 -NgrokAuthToken "2abc123def456ghi789jkl"

# Linux/Mac
./deploy.sh --token "2abc123def456ghi789jkl"
```

**Option 2: Environment Variable**
```bash
# Windows PowerShell
$env:NGROK_AUTHTOKEN="2abc123def456ghi789jkl"
.\deploy.ps1

# Linux/Mac
export NGROK_AUTHTOKEN="2abc123def456ghi789jkl"
./deploy.sh
```

**Option 3: .env File**
Create a `.env` file in the project root:
```env
NGROK_AUTHTOKEN=2abc123def456ghi789jkl
```

### Benefits of Using Ngrok Authtoken

- **Free Tier**: 1 tunnel, 40 connections/minute
- **Paid Plans**: Multiple tunnels, custom domains, more connections
- **Stable URLs**: URLs don't change between restarts (with paid plans)
- **Custom Domains**: Use your own domain (paid plans)

### Without Authtoken (Free Tier Limitations)

- Limited to 1 tunnel
- URLs change on each restart
- 40 connections per minute
- No custom domains

## Manual Docker Deployment

If you prefer to use docker-compose directly:

```bash
# Set ngrok authtoken
export NGROK_AUTHTOKEN="your_authtoken_here"

# Build and start
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Accessing the Application

After successful deployment:

- **Local Access**: http://localhost:8000
- **Ngrok Dashboard**: http://localhost:4040
- **Public URL**: Will be displayed in the deployment output

## Troubleshooting

### Ngrok Issues

1. **Container restarting**: Check if authtoken is valid
   ```bash
   docker-compose logs ngrok
   ```

2. **No public URL**: Wait a few seconds for ngrok to establish tunnel
   ```bash
   # Check tunnel status
   curl http://localhost:4040/api/tunnels
   ```

3. **Connection limits**: Upgrade to paid ngrok plan for higher limits

### Application Issues

1. **Model loading errors**: Check available RAM (8GB+ recommended)
   ```bash
   docker-compose logs rag-app
   ```

2. **Document processing errors**: Check file format and size
   - Supported: PDF, DOCX, PPTX, TXT
   - Max size: 100MB

3. **Port conflicts**: Ensure ports 8000 and 4040 are available

## Security Considerations

- **Public Access**: The ngrok URL is publicly accessible
- **File Uploads**: Be careful with sensitive documents
- **Authentication**: Consider adding authentication for production use
- **HTTPS**: ngrok provides HTTPS by default

## Production Deployment

For production environments:

1. **Use a paid ngrok plan** for stable URLs and custom domains
2. **Add authentication** to the application
3. **Use environment variables** for sensitive configuration
4. **Monitor logs** regularly
5. **Backup data** in the `uploaded_docs` directory

## Useful Commands

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f rag-app
docker-compose logs -f ngrok

# Restart services
docker-compose restart

# Rebuild and restart
docker-compose up --build -d

# Stop all services
docker-compose down

# Remove all data (including uploaded documents)
docker-compose down -v
```

## Support

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Verify Docker is running: `docker version`
3. Check ngrok status: http://localhost:4040
4. Ensure ports are available: `netstat -an | grep :8000`

For ngrok-specific issues, visit [ngrok documentation](https://ngrok.com/docs). 