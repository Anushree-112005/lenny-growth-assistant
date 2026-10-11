# ==============================================================================
# The Lenny Growth Assistant — Windows PowerShell Launcher
# ==============================================================================

Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host " Starting The Lenny Growth Assistant (Oogway Labs Take-Home)" -ForegroundColor Cyan
Write-Host "==============================================================" -ForegroundColor Cyan

# 1. Environment and Path setup
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$pythonExe = Join-Path $scriptDir "backend\.venv\Scripts\python.exe"
$uvicornExe = Join-Path $scriptDir "backend\.venv\Scripts\uvicorn.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Host "[ERROR] Virtual environment not found at backend\.venv!" -ForegroundColor Red
    Write-Host "Please create virtual environment and install requirements." -ForegroundColor Yellow
    exit 1
}

# 2. Check PostgreSQL Service
Write-Host "`n[1/5] Verifying PostgreSQL..." -ForegroundColor Yellow
$pgService = Get-Service -Name "*postgres*" -ErrorAction SilentlyContinue | Where-Object { $_.Status -eq "Running" }
if ($pgService) {
    Write-Host " - PostgreSQL service is running: $($pgService.Name)" -ForegroundColor Green
} else {
    Write-Host " - Warning: PostgreSQL service not detected as running." -ForegroundColor Red
}

# 3. Check Ollama
Write-Host "`n[2/5] Checking Ollama Local Server..." -ForegroundColor Yellow
try {
    $ollamaCheck = curl.exe -s --max-time 3 http://localhost:11434/api/tags
    if ($ollamaCheck -match "qwen2.5:3b") {
        Write-Host " - Ollama is reachable with model 'qwen2.5:3b' installed." -ForegroundColor Green
    } else {
        Write-Host " - Ollama is reachable, but 'qwen2.5:3b' may need pulling (`ollama pull qwen2.5:3b`)." -ForegroundColor Yellow
    }
} catch {
    Write-Host " - Warning: Ollama not reachable on http://localhost:11434. Start with `ollama serve`." -ForegroundColor Red
}

# 4. Ingest Transcripts if needed
Write-Host "`n[3/5] Verifying Ingested Transcripts in Database..." -ForegroundColor Yellow
$env:PYTHONPATH = "backend"
& $pythonExe -m app.retrieval.ingest --dir transcripts

# 5. Launch Backend
Write-Host "`n[4/5] Starting FastAPI Backend on http://127.0.0.1:8000..." -ForegroundColor Yellow
$backendJob = Start-Process -FilePath $uvicornExe -ArgumentList "app.main:app", "--host", "127.0.0.1", "--port", "8000" -WorkingDirectory $scriptDir -PassThru -WindowStyle Minimized
Write-Host " - Backend started (PID: $($backendJob.Id))." -ForegroundColor Green

# 6. Launch Frontend
Write-Host "`n[5/5] Starting React + Vite Frontend on http://localhost:5173..." -ForegroundColor Yellow
$frontendDir = Join-Path $scriptDir "frontend"
$frontendJob = Start-Process -FilePath "npm.cmd" -ArgumentList "run", "dev" -WorkingDirectory $frontendDir -PassThru -WindowStyle Minimized
Write-Host " - Frontend dev server started (PID: $($frontendJob.Id))." -ForegroundColor Green

Write-Host "`n==============================================================" -ForegroundColor Green
Write-Host " Application ready!" -ForegroundColor Green
Write-Host " Open your browser to: http://localhost:5173" -ForegroundColor Cyan
Write-Host " API Documentation:    http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host " Health Check:         http://127.0.0.1:8000/health" -ForegroundColor Cyan
Write-Host "==============================================================" -ForegroundColor Green
Write-Host "Press Ctrl+C or close this window when done."
Start-Process "http://localhost:5173"
