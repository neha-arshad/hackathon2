@echo off
REM Batch script to start the backend services for the Todo App

echo Starting Todo App backend services...

REM Start the main backend API server in a new window
echo Starting backend API server on port 8000...
start cmd /k "cd /d %~dp0\backend && python run_server.py"

REM Wait a moment for the backend to start
timeout /t 3 /nobreak >nul

REM Start the AI agent server in a new window
echo Starting AI agent server on port 8001...
set BACKEND_BASE_URL=http://localhost:8000
start cmd /k "cd /d %~dp0\src\ai_agent && python -c ^^"import os^^ os.environ['BACKEND_BASE_URL'] = 'http://localhost:8000'^^ from server import app^^ import uvicorn^^ uvicorn.run(app, host='0.0.0.0', port=8001)^^""

echo Backend services started!
echo Backend API: http://localhost:8000
echo AI Agent: http://localhost:8001
echo Check the new command windows for server status.
pause