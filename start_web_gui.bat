@echo off
echo ====================================================
echo 🚀 Nimble Streamer Log Analyzer - Web GUI Launcher
echo ====================================================
echo.

echo 🔍 Checking system...
cd /d "C:\dev\ns_log_analayzer"

echo ✅ Changed to project directory: %CD%
echo.

echo 🔍 Checking if virtual environment exists...
if not exist ".venv\Scripts\python.exe" (
    echo ❌ Virtual environment not found!
    echo    Please create a virtual environment first
    echo    Run: python -m venv .venv
    pause
    exit /b 1
)

echo ✅ Virtual environment found
echo.

echo 🚀 Starting Web GUI...
echo    Using: .venv\Scripts\python.exe
echo    Port: Will auto-detect available port
echo.
echo    Once started, open your browser to the displayed URL
echo    Press Ctrl+C in this window to stop the server
echo.
echo ====================================================

:: Set environment variable to avoid GUI issues
set MPLBACKEND=Agg

".venv\Scripts\python.exe" web_gui.py

echo.
echo 👋 Web GUI has stopped
pause
