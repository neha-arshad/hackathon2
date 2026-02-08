"""
Test script for the Todo API to verify endpoints work correctly
"""
import requests
import json

BASE_URL = "http://localhost:8001"

def test_api():
    print("Testing Todo API...")
    
    # First, register a test user
    print("\n1. Registering a test user...")
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
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
    print("\n2. Logging in to get token...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=user_data)
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
    
    # Test creating a task
    print("\n3. Creating a task...")
    task_data = {
        "title": "Test task from API test",
        "description": "This is a test task created via API",
        "priority": "medium"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/tasks", json=task_data, headers=headers)
        print(f"Create task response: {response.status_code}")
        if response.status_code == 200:
            task = response.json()
            print(f"Task created: {task}")
        else:
            print(f"Task creation failed: {response.text}")
    except Exception as e:
        print(f"Error creating task: {e}")
    
    # Test getting tasks
    print("\n4. Getting tasks...")
    try:
        response = requests.get(f"{BASE_URL}/tasks", headers=headers)
        print(f"Get tasks response: {response.status_code}")
        if response.status_code == 200:
            tasks = response.json()
            print(f"Tasks retrieved: {len(tasks)} tasks")
            for task in tasks:
                print(f"  - {task['id']}: {task['title']} ({task['completed']})")
        else:
            print(f"Getting tasks failed: {response.text}")
    except Exception as e:
        print(f"Error getting tasks: {e}")

if __name__ == "__main__":
    test_api()