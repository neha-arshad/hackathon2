from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import routes

app = FastAPI(title="Todo App API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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