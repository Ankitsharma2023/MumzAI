@echo off
REM ===== Mumz Assistant - backend setup (Windows) =====
cd /d "%~dp0"

echo Creating Python virtual environment...
python -m venv .venv
if errorlevel 1 (
  echo.
  echo Could not run "python". Try installing Python 3.11+ from python.org
  echo and make sure "Add Python to PATH" was ticked. Or try: py -m venv .venv
  pause
  exit /b 1
)

call .venv\Scripts\activate.bat
echo Upgrading pip...
python -m pip install --upgrade pip
echo Installing dependencies (this can take a few minutes the first time)...
pip install -r requirements.txt

if not exist .env (
  copy .env.example .env
  echo.
  echo  >>> IMPORTANT: open  backend\.env  and fill in:
  echo        GEMINI_API_KEY   ^(from https://aistudio.google.com/apikey^)
  echo        MONGODB_URI      ^(your Atlas connection string^)
)

echo.
echo Setup done. Next, run:  seed.bat
pause
