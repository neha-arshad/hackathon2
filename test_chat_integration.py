"""
Test script to verify chat integration with backend API
"""
import requests
import json

TODO_BACKEND_URL = "http://localhost:8001"
CHAT_BACKEND_URL = "http://localhost:8000"  # Chat server runs on port 8000

def test_chat_integration():
    print("Testing Chat Integration with Backend API...")
    
    # First, start the main todo backend server on port 8001
    print("\n1. Starting Todo Backend Server on port 8001...")
    # Note: This assumes the server is already running
    try:
        response = requests.get(f"{TODO_BACKEND_URL}/")
        print(f"Todo backend status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error connecting to todo backend: {e}")
        return
    
    # Register a test user
    print("\n2. Registering a test user...")
    user_data = {
        "email": "chat_test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{TODO_BACKEND_URL}/auth/register", json=user_data)
        print(f"Registration response: {response.status_code}")
        if response.status_code == 200:
            user = response.json()
            print(f"User registered: {user}")
        else:
            print(f"Registration failed: {response.text}")
    except Exception as e:
        print(f"Error during registration: {e}")
        return
    
    # Login to get token
    print("\n3. Logging in to get token...")
    try:
        response = requests.post(f"{TODO_BACKEND_URL}/auth/login", json=user_data)
        print(f"Login response: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            print(f"Token received: {access_token[:20]}...")
            
            # Set up headers with the token
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        else:
            print(f"Login failed: {response.text}")
            return
    except Exception as e:
        print(f"Error during login: {e}")
        return
    
    # Test creating a task directly via the todo API
    print("\n4. Creating a task directly via todo API...")
    task_data = {
        "title": "Direct API Task",
        "description": "This task was created directly via the API",
        "priority": "medium"
    }
    
    try:
        response = requests.post(f"{TODO_BACKEND_URL}/tasks", json=task_data, headers=headers)
        print(f"Direct API create task response: {response.status_code}")
        if response.status_code == 200:
            task = response.json()
            print(f"Task created via direct API: {task}")
        else:
            print(f"Direct API task creation failed: {response.text}")
    except Exception as e:
        print(f"Error creating task via direct API: {e}")
    
    # Test getting tasks to see what's in the database
    print("\n5. Getting tasks from database...")
    try:
        response = requests.get(f"{TODO_BACKEND_URL}/tasks", headers=headers)
        print(f"Get tasks response: {response.status_code}")
        if response.status_code == 200:
            tasks = response.json()
            print(f"Current tasks in database: {len(tasks)}")
            for task in tasks:
                print(f"  - {task['id']}: {task['title']} ({task['completed']})")
        else:
            print(f"Getting tasks failed: {response.text}")
    except Exception as e:
        print(f"Error getting tasks: {e}")
    
    print("\nNote: To test the chat integration, you would need to start the chat server on port 8000")
    print("and make requests to it with the Authorization header.")
    print("The chat server will then use the provided token to call the todo backend.")

if __name__ == "__main__":
    test_chat_integration()