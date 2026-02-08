# from src.task_manager import TaskManager
from .task_manager import TaskManager

from src.models import Task
import sys

def display_menu():
    print("\n" + "="*50)
    print("TODO APPLICATION - CONSOLE VERSION")
    print("="*50)
    print("1. Add Task")
    print("2. View All Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Mark Task Complete/Incomplete")
    print("6. Filter Tasks")
    print("7. Search Tasks")
    print("8. Sort Tasks")
    print("9. Exit")
    print("-"*50)

def get_task_details():
    title = input("Enter task title: ").strip()
    if not title:
        raise ValueError("Task title cannot be empty")
    
    description = input("Enter task description (optional): ").strip()
    priority = input("Enter priority (low/medium/high) [default: medium]: ").strip().lower()
    
    if not priority:
        priority = "medium"
    elif priority not in ["low", "medium", "high"]:
        raise ValueError("Priority must be 'low', 'medium', or 'high'")
    
    return title, description, priority

def print_tasks(tasks):
    if not tasks:
        print("No tasks found.")
        return
    
    print("\nTasks:")
    for task in tasks:
        status = "Completed" if task.completed else "Pending"
        print(f"ID: {task.id} | {task} | Status: {status}")

def get_task_id():
    try:
        task_id = int(input("Enter task ID: "))
        return task_id
    except ValueError:
        raise ValueError("Task ID must be an integer")

def main():
    task_manager = TaskManager()
    
    while True:
        try:
            display_menu()
            choice = input("Enter your choice (1-9): ").strip()
            
            if choice == "1":
                # Add Task
                title, description, priority = get_task_details()
                task = task_manager.add_task(title, description, priority)
                print(f"Task '{task.title}' added successfully with ID: {task.id}")
            
            elif choice == "2":
                # View All Tasks
                tasks = task_manager.get_all_tasks()
                print_tasks(tasks)
            
            elif choice == "3":
                # Update Task
                task_id = get_task_id()
                task = task_manager.get_task_by_id(task_id)
                if not task:
                    print(f"Task with ID {task_id} not found.")
                    continue
                
                print(f"Current task: {task}")
                print("Enter new details (leave blank to keep current value):")
                
                title_input = input(f"New title (current: {task.title}): ").strip()
                title = title_input if title_input else task.title
                
                description_input = input(f"New description (current: {task.description}): ").strip()
                description = description_input if description_input else task.description
                
                priority_input = input(f"New priority (current: {task.priority}) [low/medium/high]: ").strip()
                priority = priority_input if priority_input else task.priority
                
                if task_manager.update_task(task_id, title, description, priority):
                    print(f"Task {task_id} updated successfully.")
                else:
                    print(f"Failed to update task {task_id}.")
            
            elif choice == "4":
                # Delete Task
                task_id = get_task_id()
                task = task_manager.get_task_by_id(task_id)
                if not task:
                    print(f"Task with ID {task_id} not found.")
                    continue
                
                confirm = input(f"Are you sure you want to delete task '{task.title}'? (yes/no): ").strip().lower()
                if confirm == "yes":
                    if task_manager.delete_task(task_id):
                        print(f"Task {task_id} deleted successfully.")
                    else:
                        print(f"Failed to delete task {task_id}.")
                else:
                    print("Deletion cancelled.")
            
            elif choice == "5":
                # Mark Task Complete/Incomplete
                task_id = get_task_id()
                task = task_manager.get_task_by_id(task_id)
                if not task:
                    print(f"Task with ID {task_id} not found.")
                    continue
                
                current_status = "completed" if task.completed else "pending"
                new_status = input(f"Current status: {current_status}. Mark as (completed/pending): ").strip().lower()
                
                if new_status in ["completed", "complete", "c"]:
                    task_manager.mark_task_complete(task_id, True)
                    print(f"Task {task_id} marked as completed.")
                elif new_status in ["pending", "incomplete", "p"]:
                    task_manager.mark_task_complete(task_id, False)
                    print(f"Task {task_id} marked as pending.")
                else:
                    print("Invalid input. Use 'completed' or 'pending'.")
            
            elif choice == "6":
                # Filter Tasks
                print("Filter options:")
                print("1. By completion status")
                print("2. By priority")
                print("3. Both")
                
                filter_choice = input("Enter your choice (1-3): ").strip()
                
                completed = None
                priority = None
                
                if filter_choice in ["1", "3"]:
                    status = input("Show (completed/pending): ").strip().lower()
                    if status in ["completed", "complete", "c"]:
                        completed = True
                    elif status in ["pending", "incomplete", "p"]:
                        completed = False
                    else:
                        print("Invalid status, showing all tasks by default.")
                
                if filter_choice in ["2", "3"]:
                    priority = input("Enter priority (low/medium/high): ").strip().lower()
                    if priority not in ["low", "medium", "high"]:
                        print("Invalid priority, showing all tasks by default.")
                        priority = None
                
                tasks = task_manager.filter_tasks(completed, priority)
                print_tasks(tasks)
            
            elif choice == "7":
                # Search Tasks
                keyword = input("Enter keyword to search in title or description: ").strip()
                if keyword:
                    tasks = task_manager.search_tasks(keyword)
                    print_tasks(tasks)
                else:
                    print("Keyword cannot be empty.")
            
            elif choice == "8":
                # Sort Tasks
                print("Sort options:")
                print("1. By creation time")
                print("2. By priority")
                
                sort_choice = input("Enter your choice (1-2): ").strip()
                
                if sort_choice == "1":
                    order = input("Order (asc/desc): ").strip().lower()
                    reverse = True if order == "desc" else False
                    tasks = task_manager.sort_tasks("created_at", reverse=reverse)
                    print_tasks(tasks)
                elif sort_choice == "2":
                    order = input("Order (asc/desc): ").strip().lower()
                    reverse = True if order == "desc" else False
                    tasks = task_manager.sort_tasks("priority", reverse=reverse)
                    print_tasks(tasks)
                else:
                    print("Invalid sort option.")
            
            elif choice == "9":
                # Exit
                print("Thank you for using the Todo Application. Goodbye!")
                sys.exit(0)
            
            else:
                print("Invalid choice. Please enter a number between 1-9.")
        
        except ValueError as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("\n\nThank you for using the Todo Application. Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()