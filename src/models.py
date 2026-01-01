from datetime import datetime
from typing import Optional

class Task:
    def __init__(self, id: int, title: str, description: str = "", completed: bool = False, priority: str = "medium"):
        self.id = id
        self.title = title
        self.description = description
        self.completed = completed
        self.priority = priority
        self.created_at = datetime.now()
    
    def __str__(self):
        status = "✓" if self.completed else "○"
        return f"{status} [{self.priority.upper()}] Task #{self.id}: {self.title} - {self.description}"
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "priority": self.priority,
            "created_at": self.created_at.isoformat()
        }