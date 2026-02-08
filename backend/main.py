from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import routes

app = FastAPI(title="Todo App API", version="1.0.0")

# Add CORS middleware - specifically allowing localhost:3000 for frontend connecting to localhost:8001
# Also allow Swagger UI and other development origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8000",
        "http://localhost:8001",  # Main backend
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8001",  # For Swagger UI access
        "http://localhost:*",  # Allow any localhost port for development
        "http://127.0.0.1:*"   # Allow any localhost port for development
    ],  # Allow specific origins for development (frontend:3000 to backend:8001)
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],  # Explicitly allow methods including HEAD for Swagger
    allow_headers=["*"],
    # Expose headers that might be needed by clients
    expose_headers=["Access-Control-Allow-Origin", "Access-Control-Allow-Credentials"]
)

# Include the routes
app.include_router(routes.router, prefix="", tags=["todo-app"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Todo App API"}

# Optional: Add a health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}