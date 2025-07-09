# Ngrok Setup Script for RAG Application
# This script helps you configure ngrok authtoken for external access

param(
    [string]$AuthToken = "",
    [switch]$Help = $false
)

if ($Help) {
    Write-Host "Ngrok Setup Script" -ForegroundColor Green
    Write-Host "==================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\setup-ngrok.ps1 -AuthToken 'your_authtoken_here'" -ForegroundColor White
    Write-Host "  .\setup-ngrok.ps1 -Help" -ForegroundColor White
    Write-Host ""
    Write-Host "Steps to get your ngrok authtoken:" -ForegroundColor Yellow
    Write-Host "1. Sign up at https://ngrok.com" -ForegroundColor White
    Write-Host "2. Go to https://dashboard.ngrok.com/get-started/your-authtoken" -ForegroundColor White
    Write-Host "3. Copy your authtoken" -ForegroundColor White
    Write-Host "4. Run this script with your authtoken" -ForegroundColor White
    Write-Host ""
    Write-Host "Benefits of using ngrok authtoken:" -ForegroundColor Yellow
    Write-Host "- Stable URLs (paid plans)" -ForegroundColor White
    Write-Host "- Higher connection limits" -ForegroundColor White
    Write-Host "- Custom domains (paid plans)" -ForegroundColor White
    Write-Host "- Better reliability" -ForegroundColor White
    exit 0
}

if (-not $AuthToken) {
    Write-Host "No authtoken provided!" -ForegroundColor Red
    Write-Host ""
    Write-Host "To get your ngrok authtoken:" -ForegroundColor Yellow
    Write-Host "1. Visit https://ngrok.com and sign up" -ForegroundColor White
    Write-Host "2. Go to https://dashboard.ngrok.com/get-started/your-authtoken" -ForegroundColor White
    Write-Host "3. Copy your authtoken" -ForegroundColor White
    Write-Host "4. Run: .\setup-ngrok.ps1 -AuthToken 'your_authtoken_here'" -ForegroundColor White
    Write-Host ""
    Write-Host "For help: .\setup-ngrok.ps1 -Help" -ForegroundColor Cyan
    exit 1
}

Write-Host "Setting up ngrok authtoken..." -ForegroundColor Green

# Validate authtoken format (basic check)
if ($AuthToken.Length -lt 20) {
    Write-Host "Invalid authtoken format. Authtoken should be longer than 20 characters." -ForegroundColor Red
    exit 1
}

# Create .env file
$envContent = @"
# Ngrok Configuration
# Get your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken
NGROK_AUTHTOKEN=$AuthToken

# Optional: Set a custom domain (requires paid plan)
# NGROK_DOMAIN=your-custom-domain.ngrok.io
"@

try {
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "Created .env file with ngrok authtoken" -ForegroundColor Green
} catch {
    Write-Host "Failed to create .env file: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Ngrok authtoken configured successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Deploy the application:" -ForegroundColor White
Write-Host "   .\deploy.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Or deploy with explicit authtoken:" -ForegroundColor White
Write-Host "   .\deploy.ps1 -NgrokAuthToken '$AuthToken'" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Check ngrok status at: http://localhost:4040" -ForegroundColor White
Write-Host ""
Write-Host "Note: The .env file contains your authtoken. Keep it secure!" -ForegroundColor Yellow 