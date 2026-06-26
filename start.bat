@echo off
echo Starting ClaimSense AI...

:: Start FastAPI backend in a new window
start "ClaimSense Backend" cmd /k "cd /d %~dp0 && uvicorn app.main:app --reload"

:: Give the backend a moment to initialize
timeout /t 2 /nobreak >nul

:: Start Vite frontend in a new window
start "ClaimSense Frontend" cmd /k "cd /d %~dp0frontend && pnpm dev"

echo.
echo Both servers are starting:
echo   Backend  ^>  http://localhost:8000
echo   Frontend ^>  http://localhost:5173
echo   API Docs ^>  http://localhost:8000/docs
echo.
echo Close the server windows to stop.
