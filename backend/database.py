from sqlalchemy.orm import Session
import models, schemas
from security import get_password_hash
from typing import List, Optional

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_tasks(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Task).filter(models.Task.owner_id == owner_id).offset(skip).limit(limit).all()

def get_task(db: Session, task_id: int, owner_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id, models.Task.owner_id == owner_id).first()

def create_task(db: Session, task: schemas.TaskCreate, owner_id: int):
    db_task = models.Task(**task.dict(), owner_id=owner_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate, owner_id: int):
    db_task = get_task(db, task_id, owner_id)
    if db_task:
        for field, value in task_update.dict(exclude_unset=True).items():
            setattr(db_task, field, value)
        db.commit()
        db.refresh(db_task)
        return db_task
    return None

def delete_task(db: Session, task_id: int, owner_id: int):
    db_task = get_task(db, task_id, owner_id)
    if db_task:
        db.delete(db_task)
        db.commit()
        return True
    return False

def get_tasks_by_completion(db: Session, owner_id: int, completed: Optional[bool] = None):
    query = db.query(models.Task).filter(models.Task.owner_id == owner_id)
    if completed is not None:
        query = query.filter(models.Task.completed == completed)
    return query.all()

def get_tasks_by_priority(db: Session, owner_id: int, priority: Optional[str] = None):
    query = db.query(models.Task).filter(models.Task.owner_id == owner_id)
    if priority is not None:
        query = query.filter(models.Task.priority == priority)
    return query.all()

def search_tasks(db: Session, owner_id: int, keyword: str):
    return db.query(models.Task).filter(
        models.Task.owner_id == owner_id,
        (models.Task.title.contains(keyword)) | (models.Task.description.contains(keyword))
    ).all()