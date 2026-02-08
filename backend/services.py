from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import database, models, schemas

class TaskService:
    def __init__(self, db: Session):
        self.db = db
        # We'll use the database operations from the database module
        # but preserve the business logic from Phase I where possible

    def add_task(self, task_create: schemas.TaskCreate, owner_id: int) -> models.Task:
        # Validate input like Phase I
        if not task_create.title or not task_create.title.strip():
            raise ValueError("Task title cannot be empty")

        if task_create.priority not in ["low", "medium", "high"]:
            raise ValueError("Priority must be 'low', 'medium', or 'high'")

        # Use database function to create task
        created_task = database.create_task(self.db, task_create, owner_id)
        
        # Verify the task was actually stored
        if created_task is None:
            raise ValueError("Failed to create task in database")
        
        return created_task

    def get_all_tasks(self, owner_id: int) -> List[models.Task]:
        return database.get_tasks(self.db, owner_id)

    def get_task_by_id(self, task_id: int, owner_id: int) -> Optional[models.Task]:
        return database.get_task(self.db, task_id, owner_id)

    def update_task(self, task_id: int, task_update: schemas.TaskUpdate, owner_id: int) -> bool:
        # Validate input like Phase I if title or priority is being updated
        if task_update.title is not None:
            if not task_update.title.strip():
                raise ValueError("Task title cannot be empty")
        
        if task_update.priority is not None:
            if task_update.priority not in ["low", "medium", "high"]:
                raise ValueError("Priority must be 'low', 'medium', or 'high'")

        updated_task = database.update_task(self.db, task_id, task_update, owner_id)
        return updated_task is not None

    def delete_task(self, task_id: int, owner_id: int) -> bool:
        return database.delete_task(self.db, task_id, owner_id)

    def mark_task_complete(self, task_id: int, completed: bool, owner_id: int) -> bool:
        task = self.get_task_by_id(task_id, owner_id)
        if task:
            task_update = schemas.TaskUpdate(completed=completed)
            updated_task = database.update_task(self.db, task_id, task_update, owner_id)
            return updated_task is not None
        return False

    def filter_tasks(self, owner_id: int, completed: Optional[bool] = None, priority: Optional[str] = None) -> List[models.Task]:
        # Get all tasks first
        tasks = self.get_all_tasks(owner_id)

        # Apply filters like Phase I
        if completed is not None:
            tasks = [task for task in tasks if task.completed == completed]

        if priority is not None:
            tasks = [task for task in tasks if task.priority == priority]

        return tasks

    def search_tasks(self, owner_id: int, keyword: str) -> List[models.Task]:
        # Use database search
        return database.search_tasks(self.db, owner_id, keyword)

    def sort_tasks(self, owner_id: int, by: str, reverse: bool = False) -> List[models.Task]:
        # Get all tasks first
        tasks = self.get_all_tasks(owner_id)

        if by == "created_at":
            return sorted(tasks, key=lambda t: t.created_at, reverse=reverse)
        elif by == "priority":
            priority_order = {"high": 1, "medium": 2, "low": 3}
            return sorted(tasks, key=lambda t: priority_order.get(t.priority, 4), reverse=reverse)
        else:
            raise ValueError("Sort by must be 'created_at' or 'priority'")


class ChatTaskService:
    def __init__(self, db: Session):
        self.db = db

    def create_chat_task(self, chat_task_create: schemas.ChatTaskCreate) -> models.ChatTask:
        # Validate input
        if not chat_task_create.user_message.strip():
            raise ValueError("User message cannot be empty")

        if chat_task_create.status not in ["pending", "done", "error"]:
            raise ValueError("Status must be 'pending', 'done', or 'error'")

        # Use database function to create chat task
        return database.create_chat_task(self.db, chat_task_create)

    def get_all_chat_tasks(self, user_id: int) -> List[models.ChatTask]:
        return database.get_chat_tasks(self.db, user_id)

    def get_chat_task_by_id(self, chat_task_id: int, user_id: int) -> Optional[models.ChatTask]:
        return database.get_chat_task(self.db, chat_task_id, user_id)

    def update_chat_task(self, chat_task_id: int, chat_task_update: schemas.ChatTaskUpdate, user_id: int) -> bool:
        # Validate input if status is being updated
        if chat_task_update.status is not None:
            if chat_task_update.status not in ["pending", "done", "error"]:
                raise ValueError("Status must be 'pending', 'done', or 'error'")

        updated_chat_task = database.update_chat_task(self.db, chat_task_id, chat_task_update, user_id)
        return updated_chat_task is not None

    def delete_chat_task(self, chat_task_id: int, user_id: int) -> bool:
        return database.delete_chat_task(self.db, chat_task_id, user_id)

    def get_chat_tasks_by_status(self, user_id: int, status: str) -> List[models.ChatTask]:
        return database.get_chat_tasks_by_status(self.db, user_id, status)