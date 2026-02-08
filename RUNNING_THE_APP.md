# Todo App - Complete Setup Guide

## Project Overview
This project consists of:
1. Backend API (FastAPI) - Runs on port 8000
2. AI Agent Server - Runs on port 8001
3. Frontend (Next.js) - Runs on port 3000

## Prerequisites
- Python 3.8+
- Node.js 16+

## Setup Instructions

### 1. Backend Setup
```bash
# Navigate to backend directory
cd backend/

# Create virtual environment (optional but recommended)
python -m venv venv
# On Windows: venv\Scripts\activate
# On Linux/Mac: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env  # If available, or create manually

# Initialize database (if needed)
python init_db.py

# Run the backend server
python run_server.py
# OR
uvicorn main:app --reload --port 8000
```

### 2. AI Agent Setup
```bash
# Navigate to AI agent directory
cd src/ai_agent/

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export BACKEND_BASE_URL="http://localhost:8000"
export AUTH_TOKEN=""  # Set this if you have a valid token

# Run the AI agent server
uvicorn server:app --reload --port 8001
```

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend/

# Install dependencies
npm install

# Run the development server
npm run dev
```

## Environment Variables

### Backend (.env in backend/ folder)
```
DATABASE_URL=postgresql://username:password@localhost/dbname
SECRET_KEY=your-super-secret-key
```

### AI Agent (set in environment or .env)
```
BACKEND_BASE_URL=http://localhost:8000
AUTH_TOKEN=your-auth-token-if-available
OPENAI_API_KEY=your-openai-api-key  # Optional, for real AI
```

## Running the Application

1. **Start Backend Server (Port 8000)**:
   ```bash
   cd backend && python run_server.py
   ```

2. **Start AI Agent Server (Port 8001)**:
   ```bash
   cd src/ai_agent && uvicorn server:app --port 8001
   ```

3. **Start Frontend (Port 3000)**:
   ```bash
   cd frontend && npm run dev
   ```

## API Documentation
- Backend API: http://localhost:8000/docs
- AI Agent API: http://localhost:80001/docs

## Features
- User Registration/Login
- Todo Management (CRUD operations)
- AI Chat Interface for natural language todo management
- Filtering and sorting capabilities

## Troubleshooting

### Common Issues:

1. **Backend server won't start**:
   - Check if the port 8000 is available
   - Verify database connection settings
   - Ensure all dependencies are installed

2. **AI agent can't connect to backend**:
   - Verify BACKEND_BASE_URL is set correctly
   - Check if backend server is running
   - Ensure network connectivity between services

3. **Frontend can't connect to backend**:
   - Check API endpoints in frontend code
   - Verify CORS settings in backend

4. **Authentication errors**:
   - Register a user first via /auth/register
   - Login to obtain a token via /auth/login
   - Use the token for authenticated requests