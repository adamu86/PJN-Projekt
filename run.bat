@echo off
cd /d "%~dp0"

start cmd /k "cd frontend && npm install && npm run dev"

python -m venv backend\venv

call backend\venv\Scripts\activate.bat
pip install -r backend\requirements.txt

start cmd /k "cd backend && .\venv\Scripts\python.exe -m uvicorn main:app --reload"