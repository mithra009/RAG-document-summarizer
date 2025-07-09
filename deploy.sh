#!/bin/bash

# RAG Application Docker Deployment Script for Linux/Mac
# This script builds and runs the RAG application with ngrok for external access

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Default values
NGROK_AUTHTOKEN=""
BUILD_ONLY=false
STOP_ONLY=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --token)
            NGROK_AUTHTOKEN="$2"
            shift 2
            ;;
        --build-only)
            BUILD_ONLY=true
            shift
            ;;
        --stop-only)
            STOP_ONLY=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --token TOKEN     Set ngrok auth token"
            echo "  --build-only      Only build the Docker image"
            echo "  --stop-only       Stop running containers"
            echo "  -h, --help        Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo -e "${GREEN}🚀 RAG Application Docker Deployment${NC}"
echo -e "${GREEN}=====================================${NC}"

# Check if Docker is running
if ! docker version >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker is running${NC}"

# Check if docker-compose is available
if ! docker-compose --version >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker Compose is not available. Please install Docker Compose.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose is available${NC}"

# Stop existing containers if requested
if [ "$STOP_ONLY" = true ]; then
    echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
    docker-compose down
    echo -e "${GREEN}✅ Containers stopped${NC}"
    exit 0
fi

# Set ngrok auth token if provided
if [ -n "$NGROK_AUTHTOKEN" ]; then
    export NGROK_AUTHTOKEN="$NGROK_AUTHTOKEN"
    echo -e "${GREEN}🔑 Ngrok auth token set${NC}"
else
    echo -e "${YELLOW}⚠️  No ngrok auth token provided. Using free tier (limited connections)${NC}"
fi

# Create necessary directories
echo -e "${YELLOW}📁 Creating necessary directories...${NC}"
mkdir -p uploaded_docs offload
echo -e "${GREEN}✅ Directories created${NC}"

# Build the Docker image
echo -e "${YELLOW}🔨 Building Docker image...${NC}"
if ! docker-compose build; then
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker image built successfully${NC}"

if [ "$BUILD_ONLY" = true ]; then
    echo -e "${GREEN}✅ Build completed. Use 'docker-compose up' to start the application.${NC}"
    exit 0
fi

# Start the application
echo -e "${YELLOW}🚀 Starting RAG application with ngrok...${NC}"
docker-compose up -d

# Wait for services to start
echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 10

# Check if services are running
if docker-compose ps rag-app | grep -q "Up"; then
    echo -e "${GREEN}✅ RAG application is running${NC}"
else
    echo -e "${RED}❌ RAG application failed to start${NC}"
    docker-compose logs rag-app
    exit 1
fi

if docker-compose ps ngrok | grep -q "Up"; then
    echo -e "${GREEN}✅ Ngrok is running${NC}"
else
    echo -e "${RED}❌ Ngrok failed to start${NC}"
    docker-compose logs ngrok
    exit 1
fi

# Get ngrok URL
echo -e "${YELLOW}🔍 Getting ngrok URL...${NC}"
sleep 5

if command -v curl >/dev/null 2>&1; then
    NGROK_RESPONSE=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null)
    if [ $? -eq 0 ]; then
        PUBLIC_URL=$(echo "$NGROK_RESPONSE" | grep -o '"public_url":"[^"]*"' | cut -d'"' -f4)
        if [ -n "$PUBLIC_URL" ]; then
            echo -e "${GREEN}🌐 Public URL: $PUBLIC_URL${NC}"
        fi
    fi
fi

echo ""
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "${GREEN}=====================================${NC}"
echo -e "${CYAN}📱 Local Access: http://localhost:8000${NC}"
echo -e "${CYAN}🌐 Ngrok Dashboard: http://localhost:4040${NC}"
if [ -n "$PUBLIC_URL" ]; then
    echo -e "${CYAN}🌍 Public Access: $PUBLIC_URL${NC}"
fi
echo ""
echo -e "${YELLOW}📋 Useful commands:${NC}"
echo -e "${WHITE}  View logs: docker-compose logs -f${NC}"
echo -e "${WHITE}  Stop services: docker-compose down${NC}"
echo -e "${WHITE}  Restart services: docker-compose restart${NC}"
echo -e "${WHITE}  View ngrok tunnels: http://localhost:4040${NC}" 