@echo off
REM ===== Mumz Assistant - frontend setup (Windows) =====
cd /d "%~dp0"

echo Installing frontend dependencies...
call npm install
if errorlevel 1 (
  echo.
  echo Could not run "npm". Install Node.js 18+ from https://nodejs.org
  pause
  exit /b 1
)

if not exist .env.local (
  copy .env.local.example .env.local
)

echo.
echo Setup done. Next, run:  run.bat
pause
