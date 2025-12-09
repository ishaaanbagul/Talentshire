<#
One-click Windows setup (PowerShell)

What this does:
- Creates a Python virtualenv under `backend\venv` (if not present)
- Installs Python packages from `backend\requirements.txt`
- Builds the frontend (`npm install` + `npm run build`) if Node is available
- Starts backend (`python main.py`) in a new window and logs to `backend\logs` (keeps running)
- Serves frontend `dist/` on port 3000 using `python -m http.server 3000` in a new window

Notes:
- This script is idempotent and safe: if you already have a venv or `dist/` it will skip recreation where possible.
- The DB is optional. If you do not set `DATABASE_URL` (or PG* env vars), the app will behave exactly as on macOS.
- Run PowerShell as Administrator only if you need to install global tools. Otherwise use normal user PowerShell.

Usage:
Open PowerShell (ensure ExecutionPolicy allows running scripts) and run:
  powershell -ExecutionPolicy Bypass -File .\scripts\windows\one_click_setup.ps1
#>

Set-StrictMode -Version Latest

function Write-Title($s){ Write-Host "`n=== $s ===`n" -ForegroundColor Cyan }

Write-Title "One-click setup: Online Test Report Dashboard"

# Get the project root (2 levels up from scripts/windows)
$root = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path))
Push-Location $root

# Ensure directories
if (-not (Test-Path backend)) { Write-Host "Missing backend folder" -ForegroundColor Red; Exit 1 }
if (-not (Test-Path frontend)) { Write-Host "Missing frontend folder" -ForegroundColor Yellow }

### Backend venv and pip install
Push-Location backend
if (-not (Test-Path venv)) {
    Write-Host "Creating Python virtual environment in backend\venv..."
    python -m venv venv
} else {
    Write-Host "Virtualenv exists: backend\venv"
}

Write-Host "Activating venv and installing backend requirements..."
$activate = Join-Path (Get-Location) 'venv\Scripts\Activate.ps1'
if (Test-Path $activate) {
    & powershell -NoProfile -ExecutionPolicy Bypass -Command "& '$activate'; pip install -r requirements.txt"
} else {
    Write-Host "Activation script not found. Ensure Python venv was created correctly." -ForegroundColor Yellow
}

# Create logs dir
if (-not (Test-Path logs)) { New-Item -ItemType Directory -Path logs | Out-Null }

# Start backend in new window
$backendLog = Join-Path (Get-Location) 'logs\backend.log'
Write-Host "Starting backend (main.py) in a new window. Logs: $backendLog"
Start-Process -FilePath "powershell" -ArgumentList "-NoExit","-Command","& { cd '$(Get-Location)'; .\venv\Scripts\python.exe main.py > '$backendLog' 2>&1 }" -WindowStyle Normal

Pop-Location

### Frontend build (optional if Node available)
Push-Location frontend
if (Get-Command npm -ErrorAction SilentlyContinue) {
    Write-Host "Installing frontend npm packages..."
    npm install
    Write-Host "Building frontend (npm run build)..."
    npm run build

    # Serve dist in new window
    $dist = Join-Path (Get-Location) 'dist'
    if (-not (Test-Path $dist)) { Write-Host "Warning: dist not found after build" -ForegroundColor Yellow }
    Write-Host "Starting static server for frontend in a new window (port 3000)"
    Start-Process -FilePath "powershell" -ArgumentList "-NoExit","-Command","& { cd '$dist'; python -m http.server 3000 > ../http_server.log 2>&1 }" -WindowStyle Normal
} else {
    Write-Host "npm not found. Skipping frontend build. If you want to serve frontend, install Node.js and run 'npm install' and 'npm run build' inside frontend folder." -ForegroundColor Yellow
}

Pop-Location

Write-Title "Done"
Write-Host "Backend: http://localhost:8000" -ForegroundColor Green
Write-Host "Frontend (static): http://localhost:3000 (if built and served)" -ForegroundColor Green

Pop-Location

Write-Host "If you want to stop the services, close the windows started by this script or kill the processes." -ForegroundColor Yellow
