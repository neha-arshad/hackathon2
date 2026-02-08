"""
Test script for MCP tools
Validates that the tools can properly interface with the backend API
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools import call_tool, AddTaskParams, ListTasksParams, UpdateTaskParams, DeleteTaskParams, MarkTaskCompleteParams

def test_add_task():
    """Test adding a task"""
    print("Testing add_task...")

    params = AddTaskParams(
        title="Test task from AI agent",
        description="This is a test task created by the AI agent",
        due_date=None
    )

    result = call_tool("add_task", params.dict())
    print(f"Add task result: {result}")
    return result


def test_list_tasks():
    """Test listing tasks"""
    print("\nTesting list_tasks...")

    params = ListTasksParams(status="all")

    result = call_tool("list_tasks", params.dict())
    print(f"List tasks result: {result}")
    return result


def test_update_task(task_id: int):
    """Test updating a task"""
    print(f"\nTesting update_task for task {task_id}...")

    params = UpdateTaskParams(
        task_id=task_id,
        title="Updated test task",
        description="This task was updated by the AI agent",
        due_date=None
    )

    result = call_tool("update_task", params.dict())
    print(f"Update task result: {result}")
    return result


def test_mark_task_complete(task_id: int):
    """Test marking a task as complete"""
    print(f"\nTesting mark_task_complete for task {task_id}...")

    params = MarkTaskCompleteParams(
        task_id=task_id,
        complete=True
    )

    result = call_tool("mark_task_complete", params.dict())
    print(f"Mark task complete result: {result}")
    return result


def test_delete_task(task_id: int):
    """Test deleting a task"""
    print(f"\nTesting delete_task for task {task_id}...")

    params = DeleteTaskParams(task_id=task_id)

    result = call_tool("delete_task", params.dict())
    print(f"Delete task result: {result}")
    return result


def run_tests():
    """Run all tests in sequence"""
    print("Starting MCP tools tests...\n")

    # Test adding a task
    add_result = test_add_task()

    # Extract task ID from the result if possible
    task_id = None
    if isinstance(add_result, dict) and "task_id" in add_result:
        task_id = add_result["task_id"]
    elif isinstance(add_result, dict) and "tasks" in add_result:
        # If we got a list of tasks, try to get the last one's ID
        tasks = add_result.get("tasks", [])
        if tasks:
            task_id = tasks[-1]["id"]

    if task_id:
        print(f"Using task ID: {task_id} for subsequent tests\n")

        # Test listing tasks
        test_list_tasks()

        # Test updating the task
        test_update_task(task_id)

        # Test marking as complete
        test_mark_task_complete(task_id)

        # Test deleting the task
        test_delete_task(task_id)
    else:
        print("Could not extract task ID from add result, skipping update/delete tests")

        # Just test listing tasks
        test_list_tasks()

    print("\nTests completed!")


if __name__ == "__main__":
    run_tests()