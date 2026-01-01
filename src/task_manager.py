from typing import List, Optional
from src.models import Task

class TaskManager:
    def __init__(self):
        self.tasks: List[Task] = []
        self.next_id = 1
    
    def add_task(self, title: str, description: str = "", priority: str = "medium") -> Task:
        if not title.strip():
            raise ValueError("Task title cannot be empty")
        
        if priority not in ["low", "medium", "high"]:
            raise ValueError("Priority must be 'low', 'medium', or 'high'")
        
        task = Task(self.next_id, title, description, completed=False, priority=priority)
        self.tasks.append(task)
        self.next_id += 1
        return task
    
    def get_all_tasks(self) -> List[Task]:
        return self.tasks
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def update_task(self, task_id: int, title: str = None, description: str = None, priority: str = None) -> bool:
        task = self.get_task_by_id(task_id)
        if task:
            if title is not None:
                if not title.strip():
                    raise ValueError("Task title cannot be empty")
                task.title = title
            if description is not None:
                task.description = description
            if priority is not None:
                if priority not in ["low", "medium", "high"]:
                    raise ValueError("Priority must be 'low', 'medium', or 'high'")
                task.priority = priority
            return True
        return False
    
    def delete_task(self, task_id: int) -> bool:
        task = self.get_task_by_id(task_id)
        if task:
            self.tasks.remove(task)
            return True
        return False
    
    def mark_task_complete(self, task_id: int, completed: bool) -> bool:
        task = self.get_task_by_id(task_id)
        if task:
            task.completed = completed
            return True
        return False
    
    def filter_tasks(self, completed: Optional[bool] = None, priority: Optional[str] = None) -> List[Task]:
        filtered_tasks = self.tasks
        
        if completed is not None:
            filtered_tasks = [task for task in filtered_tasks if task.completed == completed]
        
        if priority is not None:
            filtered_tasks = [task for task in filtered_tasks if task.priority == priority]
        
        return filtered_tasks
    
    def search_tasks(self, keyword: str) -> List[Task]:
        keyword = keyword.lower()
        return [task for task in self.tasks if keyword in task.title.lower() or keyword in task.description.lower()]
    
    def sort_tasks(self, by: str, reverse: bool = False) -> List[Task]:
        if by == "created_at":
            return sorted(self.tasks, key=lambda t: t.created_at, reverse=reverse)
        elif by == "priority":
            priority_order = {"high": 1, "medium": 2, "low": 3}
            return sorted(self.tasks, key=lambda t: priority_order[t.priority], reverse=reverse)
        else:
            raise ValueError("Sort by must be 'created_at' or 'priority'")