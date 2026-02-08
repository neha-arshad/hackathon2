"""
Simple server for the Todo Chatbot AI Agent
Provides an API endpoint to process natural language requests
"""

import os
import json
import asyncio
import signal
import threading
import time
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from agent import TodoChatAgent

# Global agent instance - in production, you'd want per-user instances
agent = TodoChatAgent()

# Thread pool for running the agent processing in a separate thread
executor = ThreadPoolExecutor(max_workers=4)


class ChatRequest(BaseModel):
    message: str
    



class ChatResponse(BaseModel):
    response: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown


app = FastAPI(title="Todo Chatbot API", version="1.0.0", lifespan=lifespan)

# Add CORS middleware before defining routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8001",  # Allow Swagger UI
        "http://127.0.0.1:8001",  # Allow Swagger UI
        "http://localhost:3001",  # Additional common ports
        "http://127.0.0.1:3001",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Be more specific about allowed methods
    allow_headers=["*"],
)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, authorization: str = Header(None)):
    """
    Process a natural language message and return AI response
    """
    try:
        # Use asyncio.wait_for to ensure the request doesn't hang indefinitely
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(executor, agent.process_message, request.message, authorization),
            timeout=45.0  # 45 second timeout for the entire request
        )
        return ChatResponse(response=response)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Request timeout: AI service took too long to respond")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@app.post("/reset")
async def reset_chat():
    """
    Reset the conversation history
    """
    agent.reset_conversation()
    return {"message": "Conversation history reset"}


@app.get("/")
async def root():
    """
    Health check endpoint
    """
    return {"message": "Todo Chatbot API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)


