"""
Test script to verify authentication fixes for the POST /tasks endpoint
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_without_token():
    """Test POST /tasks without token - should return 401"""
    print("Testing POST /tasks without token...")
    try:
        response = requests.post(f"{BASE_URL}/tasks", json={
            "title": "Test task",
            "description": "Test description",
            "priority": "medium"
        })
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json() if response.content else 'No content'}")
        if response.status_code == 401:
            print("✓ Correctly returned 401 Unauthorized")
        else:
            print("✗ Expected 401 Unauthorized")
    except Exception as e:
        print(f"Error: {e}")

def test_with_invalid_token():
    """Test POST /tasks with invalid token - should return 401"""
    print("\nTesting POST /tasks with invalid token...")
    try:
        response = requests.post(f"{BASE_URL}/tasks", 
                               json={"title": "Test task", "description": "Test description", "priority": "medium"},
                               headers={"Authorization": "Bearer invalid_token_here"})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json() if response.content else 'No content'}")
        if response.status_code == 401:
            print("✓ Correctly returned 401 Unauthorized")
        else:
            print("✗ Expected 401 Unauthorized")
    except Exception as e:
        print(f"Error: {e}")

def test_register_and_login():
    """Register a user, login, and test with valid token"""
    print("\nTesting registration, login, and task creation with valid token...")
    try:
        # Register a test user
        register_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        register_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        print(f"Registration Status: {register_response.status_code}")
        
        # Login to get token
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            print(f"Received token: {token[:20]}..." if token else "No token received")
            
            # Test creating a task with valid token
            task_response = requests.post(f"{BASE_URL}/tasks", 
                                       json={
                                           "title": "Test task from auth test",
                                           "description": "Test description",
                                           "priority": "medium"
                                       },
                                       headers={"Authorization": f"Bearer {token}"})
            print(f"Task Creation Status: {task_response.status_code}")
            if task_response.status_code == 200:
                print("✓ Successfully created task with valid token")
                print(f"Created task: {task_response.json()}")
            else:
                print(f"✗ Failed to create task: {task_response.json() if task_response.content else 'No content'}")
        else:
            print(f"✗ Login failed: {login_response.json() if login_response.content else 'No content'}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing authentication fixes...")
    test_without_token()
    test_with_invalid_token()
    test_register_and_login()
    print("\nTest completed.")