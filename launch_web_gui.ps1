# Nimble Streamer Log Analyzer - PowerShell Launcher
# Avoids threading issues by using proper environment setup

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "🚀 Nimble Streamer Log Analyzer - PowerShell Launcher" -ForegroundColor Yellow
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "✅ Changed to project directory: $(Get-Location)" -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "   Please create a virtual environment first" -ForegroundColor Red
    Write-Host "   Run: python -m venv .venv" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Virtual environment found" -ForegroundColor Green
Write-Host ""

# Set environment variables to avoid GUI issues
$env:MPLBACKEND = "Agg"

Write-Host "🚀 Starting Web GUI..." -ForegroundColor Yellow
Write-Host "   Using: .venv\Scripts\python.exe" -ForegroundColor Gray
Write-Host "   Backend: Non-interactive (avoids threading issues)" -ForegroundColor Gray
Write-Host ""
Write-Host "   Once started, open your browser to the displayed URL" -ForegroundColor Cyan
Write-Host "   Press Ctrl+C in this window to stop the server" -ForegroundColor Cyan
Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan

try {
    & ".venv\Scripts\python.exe" simple_launcher.py
}
catch {
    Write-Host ""
    Write-Host "❌ Error occurred: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "💡 Try running as administrator or check if ports are available" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "👋 Web GUI has stopped" -ForegroundColor Yellow
Read-Host "Press Enter to exit"
