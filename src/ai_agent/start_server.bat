@echo off
REM Script to start the AI agent server

set BACKEND_BASE_URL=%BACKEND_BASE_URL%:"http://localhost:8000"
if "%BACKEND_BASE_URL%"=="" set BACKEND_BASE_URL=http://localhost:8000

echo Starting AI Agent Server...
echo Connecting to backend at: %BACKEND_BASE_URL%

uvicorn src.ai_agent.server:app --host 0.0.0.0 --port 8001 --reload