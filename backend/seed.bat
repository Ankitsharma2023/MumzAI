@echo off
REM ===== Load products into MongoDB + build the vector index (run once) =====
cd /d "%~dp0"
call .venv\Scripts\activate.bat

echo Seeding MongoDB from products.json...
python seed_db.py
if errorlevel 1 ( echo Seeding failed - check MONGODB_URI in .env & pause & exit /b 1 )

echo Building the ChromaDB vector index...
python ingest.py

echo.
echo Done. Next, run:  run.bat
pause
