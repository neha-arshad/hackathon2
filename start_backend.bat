@echo off
echo Setting up and starting the Todo App backend...

REM Change to the backend directory
cd /d "%~dp0\backend"

REM Initialize the database
echo Initializing database...
python init_db.py

REM Start the server on port 8001
echo Starting server on port 8001...
python run_server.py