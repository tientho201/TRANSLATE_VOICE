# Voice Translator - Windows Startup Script
# Run: .\start.ps1

Write-Host ""
Write-Host "========================================"
Write-Host "   Voice Translator - Starting...   "
Write-Host "========================================"
Write-Host ""

# Check if .env exists
if (-Not (Test-Path "backend\.env")) {
    Write-Host "[ERROR] backend\.env not found!" -ForegroundColor Red
    Write-Host "Please create backend\.env with your GROQ_API_KEY" -ForegroundColor Yellow
    exit 1
}

# Check if GROQ_API_KEY is set
$envContent = Get-Content "backend\.env" -Raw
if ($envContent -notmatch "GROQ_API_KEY=\S+") {
    Write-Host "[ERROR] GROQ_API_KEY is not set in backend\.env" -ForegroundColor Red
    exit 1
}

Write-Host "[1/2] Starting FastAPI backend on port 8000..." -ForegroundColor Green
$backendPath = Join-Path $PWD "backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

Start-Sleep -Seconds 2

Write-Host "[2/2] Starting Streamlit frontend on port 8501..." -ForegroundColor Green
$frontendPath = Join-Path $PWD "frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; streamlit run app.py"

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "========================================"
Write-Host "  Both services are starting up!" -ForegroundColor Green
Write-Host "  Frontend : http://localhost:8501" -ForegroundColor Yellow
Write-Host "  Backend  : http://localhost:8000" -ForegroundColor Yellow
Write-Host "  API Docs : http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "========================================"
Write-Host ""
