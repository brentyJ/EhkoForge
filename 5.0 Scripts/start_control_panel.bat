@echo off
REM EhkoForge Control Panel Launcher
REM Starts the control panel server and opens in browser

echo ========================================
echo   EhkoForge Control Panel v1.0
echo ========================================
echo.

cd /d "%~dp0"

REM Check if flask-cors is installed
python -c "import flask_cors" 2>nul
if errorlevel 1 (
    echo [ERROR] flask-cors not installed
    echo Installing flask-cors...
    pip install flask-cors
    echo.
)

echo Starting control panel server on port 5001...
echo.
echo Backend: http://localhost:5001
echo Frontend Dev: http://localhost:3000 (if running npm run dev)
echo.
echo Press Ctrl+C to stop
echo.

REM Start the server
python control_server.py

pause
