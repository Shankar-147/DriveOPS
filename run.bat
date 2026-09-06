@echo off
REM Starts the DriveOps backend + frontend and opens the site in your browser.
REM Just double-click this file (or run it) whenever you want to see the site live.
REM Close the two new console windows it opens to stop the servers.

cd /d "%~dp0"

echo Starting backend (FastAPI) on http://localhost:8000 ...
start "DriveOps Backend" cmd /k "venv\Scripts\python.exe -m uvicorn backend.main:app --port 8000"

echo Starting frontend (Vite) on http://localhost:5173 ...
start "DriveOps Frontend" cmd /k "cd frontend && npm run dev"

echo Waiting for the servers to come up...
timeout /t 6 /nobreak >nul

echo Opening the site in your browser...
start http://localhost:5173

echo.
echo Done. Two windows are now running the backend and frontend.
echo Close them whenever you want to stop the servers.
