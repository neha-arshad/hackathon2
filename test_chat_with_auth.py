"""
Test script to verify the chat functionality with authentication
"""
import requests
import json

def test_chat_with_auth():
    print("Testing chat functionality with authentication...")
    
    # First, register a user with the main backend
    print("\n1. Registering user with main backend...")
    todo_backend_url = "http://localhost:8001"
    
    user_data = {
        "email": "chat_test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{todo_backend_url}/auth/register", json=user_data)
        print(f"Registration response: {response.status_code}")
        if response.status_code != 200 and response.status_code != 400:  # 400 might mean already exists
            print(f"Registration failed: {response.text}")
            return
    except Exception as e:
        print(f"Error during registration: {e}")
        return
    
    # Login to get token
    print("\n2. Logging in to get token...")
    try:
        response = requests.post(f"{todo_backend_url}/auth/login", json=user_data)
        print(f"Login response: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            print(f"Token received: {access_token[:20]}...")
        else:
            print(f"Login failed: {response.text}")
            return
    except Exception as e:
        print(f"Error during login: {e}")
        return
    
    # Test the chat endpoint with the token
    print("\n3. Testing chat endpoint with token...")
    chat_url = "http://localhost:8000/chat"
    
    chat_data = {
        "message": "Add a task to buy groceries"
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(chat_url, json=chat_data, headers=headers)
        print(f"Chat response status: {response.status_code}")
        if response.status_code == 200:
            chat_result = response.json()
            print(f"Chat response: {chat_result}")
        else:
            print(f"Chat request failed: {response.text}")
    except Exception as e:
        print(f"Error during chat request: {e}")
        print("Note: The chat server may not be running on port 8000")
    
    # Also test direct task creation to compare
    print("\n4. Testing direct task creation...")
    task_data = {
        "title": "Direct task test",
        "description": "Created directly via API",
        "priority": "medium"
    }
    
    try:
        response = requests.post(f"{todo_backend_url}/tasks", json=task_data, headers=headers)
        print(f"Direct task creation response: {response.status_code}")
        if response.status_code == 200:
            task_result = response.json()
            print(f"Direct task created: {task_result}")
        else:
            print(f"Direct task creation failed: {response.text}")
    except Exception as e:
        print(f"Error during direct task creation: {e}")

if __name__ == "__main__":
    test_chat_with_auth()