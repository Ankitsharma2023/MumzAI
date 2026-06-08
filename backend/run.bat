@echo off
REM ===== Start the backend API at http://localhost:8000 =====
cd /d "%~dp0"
call .venv\Scripts\activate.bat
echo Starting Mumz Assistant API at http://localhost:8000  (Ctrl+C to stop)
uvicorn main:app --reload --port 8000
