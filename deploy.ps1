# RAG Application Docker Deployment Script for Windows
# This script builds and runs the RAG application with ngrok for external access

param(
    [string]$NgrokAuthToken = "",
    [switch]$BuildOnly = $false,
    [switch]$StopOnly = $false
)

Write-Host "RAG Application Docker Deployment" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "Docker is running" -ForegroundColor Green
} catch {
    Write-Host "Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check if docker-compose is available
try {
    docker-compose --version | Out-Null
    Write-Host "Docker Compose is available" -ForegroundColor Green
} catch {
    Write-Host "Docker Compose is not available. Please install Docker Compose." -ForegroundColor Red
    exit 1
}

# Stop existing containers if requested
if ($StopOnly) {
    Write-Host "Stopping existing containers..." -ForegroundColor Yellow
    docker-compose down
    Write-Host "Containers stopped" -ForegroundColor Green
    exit 0
}

# Set ngrok auth token if provided
if ($NgrokAuthToken) {
    $env:NGROK_AUTHTOKEN = $NgrokAuthToken
    Write-Host "Ngrok auth token set" -ForegroundColor Green
} else {
    Write-Host "No ngrok auth token provided. Using free tier (limited connections)" -ForegroundColor Yellow
}

# Create necessary directories
Write-Host "Creating necessary directories..." -ForegroundColor Yellow
if (!(Test-Path "uploaded_docs")) {
    New-Item -ItemType Directory -Path "uploaded_docs" | Out-Null
}
if (!(Test-Path "offload")) {
    New-Item -ItemType Directory -Path "offload" | Out-Null
}
Write-Host "Directories created" -ForegroundColor Green

# Build the Docker image
Write-Host "Building Docker image..." -ForegroundColor Yellow
docker-compose build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker build failed" -ForegroundColor Red
    exit 1
}
Write-Host "Docker image built successfully" -ForegroundColor Green

if ($BuildOnly) {
    Write-Host "Build completed. Use docker-compose up to start the application." -ForegroundColor Green
    exit 0
}

# Start the application
Write-Host "Starting RAG application with ngrok..." -ForegroundColor Yellow
docker-compose up -d

# Wait for services to start
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check if services are running
$ragStatus = docker-compose ps rag-app
$ngrokStatus = docker-compose ps ngrok

if ($ragStatus -like "*Up*") {
    Write-Host "RAG application is running" -ForegroundColor Green
} else {
    Write-Host "RAG application failed to start" -ForegroundColor Red
    docker-compose logs rag-app
    exit 1
}

if ($ngrokStatus -like "*Up*") {
    Write-Host "Ngrok is running" -ForegroundColor Green
} else {
    Write-Host "Ngrok failed to start" -ForegroundColor Red
    docker-compose logs ngrok
    exit 1
}

# Get ngrok URL
Write-Host "Getting ngrok URL..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

try {
    $ngrokResponse = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -Method Get
    $publicUrl = $ngrokResponse.tunnels[0].public_url
    Write-Host "Public URL: $publicUrl" -ForegroundColor Green
} catch {
    Write-Host "Could not retrieve ngrok URL. Check http://localhost:4040 for tunnel status" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Deployment completed successfully!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host "Local Access: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Ngrok Dashboard: http://localhost:4040" -ForegroundColor Cyan
if ($publicUrl) {
    Write-Host "Public Access: $publicUrl" -ForegroundColor Cyan
}
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  View logs: docker-compose logs -f" -ForegroundColor White
Write-Host "  Stop services: docker-compose down" -ForegroundColor White
Write-Host "  Restart services: docker-compose restart" -ForegroundColor White
Write-Host "  View ngrok tunnels: http://localhost:4040" -ForegroundColor White 