"""
MCP Tools for Todo Chatbot
These tools interface with the backend API to perform todo operations
"""

import os
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel

# Get backend API base URL from environment or use default
BACKEND_BASE_URL = os.getenv('BACKEND_BASE_URL', 'http://localhost:8000')

# Token for authentication - should be set in environment for real usage
AUTH_TOKEN = os.getenv('AUTH_TOKEN', '')


class AddTaskParams(BaseModel):
    title: str
    description: Optional[str] = ""
    due_date: Optional[str] = None  # ISO format YYYY-MM-DD


class ListTasksParams(BaseModel):
    status: Optional[str] = "all"  # "all", "pending", "completed"


class UpdateTaskParams(BaseModel):
    task_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None


class DeleteTaskParams(BaseModel):
    task_id: int


class MarkTaskCompleteParams(BaseModel):
    task_id: int
    complete: bool


def make_api_request(endpoint: str, method: str = "GET", data: dict = None, auth_token: str = None, timeout: int = 30):
    """Helper function to make API requests to the backend"""
    headers = {
        "Content-Type": "application/json"
    }

    # Use the passed auth token, or fall back to environment variable
    token_to_use = auth_token or AUTH_TOKEN

    # Only add Authorization header if a token is provided
    if token_to_use:
        headers["Authorization"] = f"Bearer {token_to_use}"

    url = f"{BACKEND_BASE_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=timeout)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=timeout)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=timeout)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        # For successful responses, return the JSON
        if response.status_code in [200, 201, 204]:
            try:
                return response.json()
            except:
                # If no JSON response, return success message
                return {"success": True}
        else:
            # For error responses, return error details
            try:
                error_detail = response.json()
            except:
                error_detail = {"detail": response.text}
            return {"error": error_detail, "status_code": response.status_code}
    except requests.exceptions.ConnectionError:
        return {"error": {"detail": "Could not connect to backend API"}, "status_code": 503}
    except requests.exceptions.Timeout:
        return {"error": {"detail": "Request to backend API timed out"}, "status_code": 408}
    except Exception as e:
        return {"error": {"detail": f"Request failed: {str(e)}"}, "status_code": 500}


def add_task(params: AddTaskParams, auth_token: str = None) -> Dict:
    """
    Add a new task via the backend API
    """
    try:
        # Prepare the request payload
        payload = {
            "title": params.title,
            "description": params.description,
            "priority": "medium"  # Default priority
        }

        # If due_date is provided, we might need to handle it differently depending on backend schema
        # For now, we'll add it to the description if provided
        if params.due_date:
            payload["description"] += f" (Due: {params.due_date})" if payload["description"] else f"Due: {params.due_date}"

        result = make_api_request("/tasks", "POST", payload, auth_token, timeout=30)

        if "error" in result:
            return {"result": "Error adding task", "details": result["error"]}

        # Verify that the task was actually stored by checking if we got a valid response
        if not result or "id" not in result:
            return {"result": "Error adding task", "details": "Invalid response from backend - task may not have been stored"}

        return {"result": "Task added successfully", "task_id": result.get("id"), "task_data": result}

    except Exception as e:
        return {"result": "Error adding task", "details": str(e)}


def list_tasks(params: ListTasksParams, auth_token: str = None) -> Dict:
    """
    List tasks via the backend API
    """
    try:
        result = make_api_request("/tasks", "GET", auth_token=auth_token, timeout=30)

        if "error" in result:
            return {"result": "Error listing tasks", "details": result["error"]}

        tasks = result

        # Filter based on status if needed
        if params.status == "completed":
            tasks = [task for task in tasks if task.get("completed", False)]
        elif params.status == "pending":
            tasks = [task for task in tasks if not task.get("completed", False)]

        return {"result": f"Found {len(tasks)} tasks", "tasks": tasks}

    except Exception as e:
        return {"result": "Error listing tasks", "details": str(e)}


def update_task(params: UpdateTaskParams, auth_token: str = None) -> Dict:
    """
    Update an existing task via the backend API
    """
    try:
        # Prepare the request payload for update
        payload = {}
        if params.title is not None:
            payload["title"] = params.title
        if params.description is not None:
            payload["description"] = params.description

        # If due_date is provided, we might need to handle it differently depending on backend schema
        if params.due_date:
            payload["description"] = f"{payload.get('description', '')} (Due: {params.due_date})".strip()

        result = make_api_request(f"/tasks/{params.task_id}", "PUT", payload, auth_token, timeout=30)

        if "error" in result:
            return {"result": f"Error updating task {params.task_id}", "details": result["error"]}

        return {"result": f"Task {params.task_id} updated successfully"}

    except Exception as e:
        return {"result": f"Error updating task {params.task_id}", "details": str(e)}


def delete_task(params: DeleteTaskParams, auth_token: str = None) -> Dict:
    """
    Delete a task via the backend API
    """
    try:
        result = make_api_request(f"/tasks/{params.task_id}", "DELETE", auth_token=auth_token, timeout=30)

        if "error" in result:
            return {"result": f"Error deleting task {params.task_id}", "details": result["error"]}

        return {"result": f"Task {params.task_id} deleted successfully"}

    except Exception as e:
        return {"result": f"Error deleting task {params.task_id}", "details": str(e)}


def mark_task_complete(params: MarkTaskCompleteParams, auth_token: str = None) -> Dict:
    """
    Mark a task as complete/incomplete via the backend API
    """
    try:
        result = make_api_request(f"/tasks/{params.task_id}/complete", "PUT", {"completed": params.complete}, auth_token, timeout=30)

        if "error" in result:
            return {"result": f"Error updating task {params.task_id} status", "details": result["error"]}

        status_text = "completed" if params.complete else "pending"
        return {"result": f"Task {params.task_id} marked as {status_text}"}

    except Exception as e:
        return {"result": f"Error updating task {params.task_id} status", "details": str(e)}


# Tool definitions for the AI agent
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Add a new task to the todo list",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Title of the task"},
                    "description": {"type": "string", "description": "Detailed description of the task"},
                    "due_date": {"type": "string", "description": "Due date in ISO format (YYYY-MM-DD)"}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks or filter by completion status",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["all", "pending", "completed"], "description": "Filter tasks by status"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update an existing task",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "ID of the task to update"},
                    "title": {"type": "string", "description": "New title of the task"},
                    "description": {"type": "string", "description": "New description of the task"},
                    "due_date": {"type": "string", "description": "New due date in ISO format"}
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task by ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "ID of the task to delete"}
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mark_task_complete",
            "description": "Mark a task as complete or incomplete",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "ID of the task to update"},
                    "complete": {"type": "boolean", "description": "Whether the task is complete"}
                },
                "required": ["task_id", "complete"]
            }
        }
    }
]


def call_tool(tool_name: str, tool_args: Dict, auth_token: str = None) -> Dict:
    """
    Call the appropriate tool based on the tool name and arguments
    """
    try:
        if tool_name == "add_task":
            params = AddTaskParams(**tool_args)
            return add_task(params, auth_token)
        elif tool_name == "list_tasks":
            params = ListTasksParams(**tool_args)
            return list_tasks(params, auth_token)
        elif tool_name == "update_task":
            params = UpdateTaskParams(**tool_args)
            return update_task(params, auth_token)
        elif tool_name == "delete_task":
            params = DeleteTaskParams(**tool_args)
            return delete_task(params, auth_token)
        elif tool_name == "mark_task_complete":
            params = MarkTaskCompleteParams(**tool_args)
            return mark_task_complete(params, auth_token)
        else:
            return {"result": "Unknown tool", "details": f"Tool {tool_name} not found"}
    except Exception as e:
        return {"result": "Error calling tool", "details": str(e)}

