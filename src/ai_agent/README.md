# AI-Powered Todo Chatbot

This component implements an AI-powered chat interface for managing todos using natural language. The system follows the Phase III specifications by using MCP tools to interface with the existing backend.

## Architecture

- **AI Agent**: Processes natural language using simulated or real OpenAI API
- **MCP Tools**: Interface layer that calls backend APIs for all operations
- **Backend API**: Existing FastAPI backend (unchanged)
- **Frontend**: Next.js chat interface

## Components

### MCP Tools (`tools.py`)
Defines functions that interface with the backend API:
- `add_task`: Create new tasks
- `list_tasks`: Retrieve tasks with filtering
- `update_task`: Modify existing tasks
- `delete_task`: Remove tasks
- `mark_task_complete`: Update completion status

### AI Agent (`agent.py`)
Processes natural language requests:
- Real OpenAI API when `OPENAI_API_KEY` is provided
- Simulated parsing when no API key is available
- Calls appropriate MCP tools based on user intent

### Server (`server.py`)
Exposes a REST API for the chat interface:
- `/chat`: Process natural language messages
- `/reset`: Clear conversation history

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables:
   ```bash
   export BACKEND_BASE_URL="http://localhost:8000"  # Point to your backend
   export OPENAI_API_KEY="your-openai-api-key"      # Optional, for real AI
   ```

3. Start the AI agent server:
   ```bash
   uvicorn src.ai_agent.server:app --host 0.0.0.0 --port 8001
   ```

## Usage

1. Ensure the backend server is running on the specified URL
2. Start the AI agent server
3. Access the chat interface through the frontend at `/chat`
4. Use natural language to manage your todos:
   - "Add a task to buy groceries tomorrow"
   - "Show my completed tasks"
   - "Mark task 1 as done"
   - "Delete the old task"

## Important Notes

- All business logic remains in the backend
- The AI layer only processes language and calls tools
- Direct database access is prohibited in the AI layer
- All operations go through the existing backend API