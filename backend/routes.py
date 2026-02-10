from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta, datetime
import schemas, services, database, models
from database import get_user_by_email
from security import verify_password, create_access_token, verify_token
from config import settings
from dependencies import get_db, get_current_user
from errors import handle_bad_request_error, handle_not_found_error, handle_unauthorized_error

router = APIRouter()

security = HTTPBearer()

@router.post("/auth/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        handle_bad_request_error("Email already registered")

    # Create new user
    try:
        db_user = database.create_user(db=db, user=user)
        return db_user
    except Exception as e:
        handle_bad_request_error(f"Error creating user: {str(e)}")

@router.post("/auth/login", response_model=schemas.Token)
def login(user_credentials: schemas.UserCreate, db: Session = Depends(get_db)):
    # Find user by email
    user = get_user_by_email(db, email=user_credentials.email)
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        handle_unauthorized_error("Incorrect email or password")

    # Create access token
    try:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )

        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        handle_bad_request_error(f"Error creating access token: {str(e)}")

@router.get("/tasks", response_model=List[schemas.TaskResponse])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        tasks = database.get_tasks(db, current_user.id, skip=skip, limit=limit)
        return tasks
    except Exception as e:
        handle_bad_request_error(f"Error retrieving tasks: {str(e)}")

@router.post("/tasks", response_model=schemas.TaskResponse)
async def create_task(
    task: schemas.TaskCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new task for the authenticated user.
    Returns 200 on success, 400 on validation error, 401 on unauthorized.
    """
    try:
        # Validate input data
        if not task.title or not task.title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task title is required and cannot be empty"
            )

        # Use the service layer to create task with validation
        task_service = services.TaskService(db)
        db_task = task_service.add_task(task, current_user.id)

        # Verify the task was actually stored
        if db_task is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create task in database"
            )

        return db_task
    except ValueError as e:
        handle_bad_request_error(str(e))
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        handle_bad_request_error(f"Error creating task: {str(e)}")

@router.get("/tasks/{task_id}", response_model=schemas.TaskResponse)
async def get_task(
    task_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = database.get_task(db, task_id, current_user.id)
    if not task:
        handle_not_found_error("Task")
    return task

@router.put("/tasks/{task_id}", response_model=schemas.TaskResponse)
async def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Use the service layer to update task with validation
    try:
        task_service = services.TaskService(db)
        success = task_service.update_task(task_id, task_update, current_user.id)
        if not success:
            handle_not_found_error("Task")

        updated_task = database.get_task(db, task_id, current_user.id)
        return updated_task
    except ValueError as e:
        handle_bad_request_error(str(e))
    except Exception as e:
        handle_bad_request_error(f"Error updating task: {str(e)}")

@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Use the service layer to delete task
    try:
        task_service = services.TaskService(db)
        success = task_service.delete_task(task_id, current_user.id)
        if not success:
            handle_not_found_error("Task")
        return {"message": "Task deleted successfully"}
    except Exception as e:
        handle_bad_request_error(f"Error deleting task: {str(e)}")

@router.put("/tasks/{task_id}/complete")
async def mark_task_complete(
    task_id: int,
    completed: bool,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Use the service layer to mark task complete/incomplete
    try:
        task_service = services.TaskService(db)
        success = task_service.mark_task_complete(task_id, completed, current_user.id)
        if not success:
            handle_not_found_error("Task")
        return {"message": f"Task marked as {'completed' if completed else 'pending'}"}
    except Exception as e:
        handle_bad_request_error(f"Error updating task status: {str(e)}")


# ChatTask API routes
@router.get("/chat_tasks", response_model=List[schemas.ChatTaskResponse])
async def get_chat_tasks(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        chat_tasks = database.get_chat_tasks(db, current_user.id, skip=skip, limit=limit)
        return chat_tasks
    except Exception as e:
        handle_bad_request_error(f"Error retrieving chat tasks: {str(e)}")


@router.post("/chat_tasks", response_model=schemas.ChatTaskResponse)
async def create_chat_task(
    chat_task: schemas.ChatTaskCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Use the service layer to create chat task with validation
    try:
        chat_task_service = services.ChatTaskService(db)
        db_chat_task = chat_task_service.create_chat_task(chat_task)
        return db_chat_task
    except ValueError as e:
        handle_bad_request_error(str(e))
    except Exception as e:
        handle_bad_request_error(f"Error creating chat task: {str(e)}")


@router.get("/chat_tasks/{chat_task_id}", response_model=schemas.ChatTaskResponse)
async def get_chat_task(
    chat_task_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chat_task = database.get_chat_task(db, chat_task_id, current_user.id)
    if not chat_task:
        handle_not_found_error("ChatTask")
    return chat_task


@router.put("/chat_tasks/{chat_task_id}", response_model=schemas.ChatTaskResponse)
async def update_chat_task(
    chat_task_id: int,
    chat_task_update: schemas.ChatTaskUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Use the service layer to update chat task with validation
    try:
        chat_task_service = services.ChatTaskService(db)
        success = chat_task_service.update_chat_task(chat_task_id, chat_task_update, current_user.id)
        if not success:
            handle_not_found_error("ChatTask")

        updated_chat_task = database.get_chat_task(db, chat_task_id, current_user.id)
        return updated_chat_task
    except ValueError as e:
        handle_bad_request_error(str(e))
    except Exception as e:
        handle_bad_request_error(f"Error updating chat task: {str(e)}")


@router.delete("/chat_tasks/{chat_task_id}")
async def delete_chat_task(
    chat_task_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Use the service layer to delete chat task
    try:
        chat_task_service = services.ChatTaskService(db)
        success = chat_task_service.delete_chat_task(chat_task_id, current_user.id)
        if not success:
            handle_not_found_error("ChatTask")
        return {"message": "Chat task deleted successfully"}
    except Exception as e:
        handle_bad_request_error(f"Error deleting chat task: {str(e)}")


@router.get("/chat_tasks/status/{status}", response_model=List[schemas.ChatTaskResponse])
async def get_chat_tasks_by_status(
    status: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        chat_tasks = database.get_chat_tasks_by_status(db, current_user.id, status)
        return chat_tasks
    except Exception as e:
        handle_bad_request_error(f"Error retrieving chat tasks by status: {str(e)}")


# Chat endpoint for AI agent integration - public access for Swagger UI testing
@router.post("/chat")
def chat_endpoint(message_data: dict):
    """
    Endpoint to interact with the AI chatbot.
    Expects a JSON payload with a 'message' field.
    """
    try:
        user_message = message_data.get("message", "")
        if not user_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message field is required"
            )

        # For now, return a simple echo response
        # In a real implementation, this would call the AI agent
        response = {
            "response": f"Echo: {user_message}",
            "timestamp": datetime.utcnow().isoformat()
        }

        return response
    except HTTPException:
        raise
    except Exception as e:
        handle_bad_request_error(f"Error processing chat message: {str(e)}")