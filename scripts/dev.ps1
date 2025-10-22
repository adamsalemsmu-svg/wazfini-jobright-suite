& backend\.venv\Scripts\Activate.ps1
Start-Process powershell -ArgumentList "-NoExit -Command cd backend; uvicorn app.main:app --reload --port 8000"
Start-Process powershell -ArgumentList "-NoExit -Command cd frontend; npm run dev"
