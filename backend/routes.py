from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
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
def get_tasks(
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
def create_task(
    task: schemas.TaskCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Use the service layer to create task with validation
    try:
        task_service = services.TaskService(db)
        db_task = task_service.add_task(task, current_user.id)
        return db_task
    except ValueError as e:
        handle_bad_request_error(str(e))
    except Exception as e:
        handle_bad_request_error(f"Error creating task: {str(e)}")

@router.get("/tasks/{task_id}", response_model=schemas.TaskResponse)
def get_task(
    task_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = database.get_task(db, task_id, current_user.id)
    if not task:
        handle_not_found_error("Task")
    return task

@router.put("/tasks/{task_id}", response_model=schemas.TaskResponse)
def update_task(
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
def delete_task(
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
def mark_task_complete(
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