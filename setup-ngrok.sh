#!/bin/bash

# Ngrok Setup Script for RAG Application
# This script helps you configure ngrok authtoken for external access

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Default values
AUTHTOKEN=""
HELP=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --token)
            AUTHTOKEN="$2"
            shift 2
            ;;
        -h|--help)
            HELP=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [ "$HELP" = true ]; then
    echo -e "${GREEN}🔧 Ngrok Setup Script${NC}"
    echo -e "${GREEN}====================${NC}"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo -e "${WHITE}  ./setup-ngrok.sh --token 'your_authtoken_here'${NC}"
    echo -e "${WHITE}  ./setup-ngrok.sh --help${NC}"
    echo ""
    echo -e "${YELLOW}Steps to get your ngrok authtoken:${NC}"
    echo -e "${WHITE}1. Sign up at https://ngrok.com${NC}"
    echo -e "${WHITE}2. Go to https://dashboard.ngrok.com/get-started/your-authtoken${NC}"
    echo -e "${WHITE}3. Copy your authtoken${NC}"
    echo -e "${WHITE}4. Run this script with your authtoken${NC}"
    echo ""
    echo -e "${YELLOW}Benefits of using ngrok authtoken:${NC}"
    echo -e "${WHITE}- Stable URLs (paid plans)${NC}"
    echo -e "${WHITE}- Higher connection limits${NC}"
    echo -e "${WHITE}- Custom domains (paid plans)${NC}"
    echo -e "${WHITE}- Better reliability${NC}"
    exit 0
fi

if [ -z "$AUTHTOKEN" ]; then
    echo -e "${RED}❌ No authtoken provided!${NC}"
    echo ""
    echo -e "${YELLOW}To get your ngrok authtoken:${NC}"
    echo -e "${WHITE}1. Visit https://ngrok.com and sign up${NC}"
    echo -e "${WHITE}2. Go to https://dashboard.ngrok.com/get-started/your-authtoken${NC}"
    echo -e "${WHITE}3. Copy your authtoken${NC}"
    echo -e "${WHITE}4. Run: ./setup-ngrok.sh --token 'your_authtoken_here'${NC}"
    echo ""
    echo -e "${CYAN}For help: ./setup-ngrok.sh --help${NC}"
    exit 1
fi

echo -e "${GREEN}🔧 Setting up ngrok authtoken...${NC}"

# Validate authtoken format (basic check)
if [ ${#AUTHTOKEN} -lt 20 ]; then
    echo -e "${RED}❌ Invalid authtoken format. Authtoken should be longer than 20 characters.${NC}"
    exit 1
fi

# Create .env file
cat > .env << EOF
# Ngrok Configuration
# Get your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken
NGROK_AUTHTOKEN=$AUTHTOKEN

# Optional: Set a custom domain (requires paid plan)
# NGROK_DOMAIN=your-custom-domain.ngrok.io
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Created .env file with ngrok authtoken${NC}"
else
    echo -e "${RED}❌ Failed to create .env file${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 Ngrok authtoken configured successfully!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "${WHITE}1. Deploy the application:${NC}"
echo -e "${CYAN}   ./deploy.sh${NC}"
echo ""
echo -e "${WHITE}2. Or deploy with explicit authtoken:${NC}"
echo -e "${CYAN}   ./deploy.sh --token '$AUTHTOKEN'${NC}"
echo ""
echo -e "${WHITE}3. Check ngrok status at: http://localhost:4040${NC}"
echo ""
echo -e "${YELLOW}Note: The .env file contains your authtoken. Keep it secure!${NC}" 