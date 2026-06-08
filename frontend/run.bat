@echo off
REM ===== Start the frontend at http://localhost:3000 =====
cd /d "%~dp0"
echo Starting Mumz Assistant UI at http://localhost:3000  (Ctrl+C to stop)
call npm run dev
