#!/usr/bin/env python
"""
Test script to verify authentication flow and identify 401 issues.
This simulates what the frontend does: login -> get token -> create task.
"""
import requests
import json
import sys

# Set stdout to handle unicode
if sys.platform == "win32":
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE_URL = "http://localhost:8000"

def test_auth_flow():
    print("=" * 60)
    print("TESTING AUTHENTICATION FLOW")
    print("=" * 60)
    
    # Step 1: Login to get token
    print("\n[Step 1] Logging in...")
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Login response status: {response.status_code}")
        
        if response.status_code == 401:
            print(f"[FAIL] Login failed: {response.json()}")
            print("\n[TIP] Try creating a user first via /auth/register or the frontend signup page")
            return None
            
        token_data = response.json()
        token = token_data.get("access_token")
        print(f"[OK] Token received (length: {len(token) if token else 0})")
        print(f"Token type: {token_data.get('token_type', 'unknown')}")
        
    except requests.exceptions.ConnectionError:
        print(f"[FAIL] Cannot connect to backend at {BASE_URL}")
        print("[TIP] Make sure the backend server is running: python run_server.py")
        return None
    except Exception as e:
        print(f"[FAIL] Login error: {e}")
        return None
    
    # Step 2: Try to create a task with the token
    print("\n[Step 2] Creating task with token...")
    
    task_data = {
        "title": "Test Task from Script",
        "description": "This task was created by the test script",
        "priority": "medium"
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"Sending request:")
    print(f"  URL: POST {BASE_URL}/tasks")
    print(f"  Authorization: Bearer {token[:30]}...")
    print(f"  Body: {json.dumps(task_data)}")
    
    response = requests.post(f"{BASE_URL}/tasks", json=task_data, headers=headers)
    
    print(f"\nResponse status: {response.status_code}")
    
    if response.status_code == 200 or response.status_code == 201:
        print(f"[OK] Task created successfully!")
        print(f"Response: {response.json()}")
        return True
    elif response.status_code == 401:
        print(f"[FAIL] 401 Unauthorized!")
        print(f"Response: {response.json()}")
        print("\n[TIP] Check backend logs for details on why token validation failed")
        return False
    else:
        print(f"[WARN] Unexpected status: {response.status_code}")
        print(f"Response: {response.json()}")
        return False

def test_token_without_auth():
    """Test what happens when we call protected endpoint without token"""
    print("\n" + "=" * 60)
    print("TESTING PROTECTED ENDPOINT WITHOUT TOKEN")
    print("=" * 60)
    
    headers = {}  # No authorization header
    
    response = requests.get(f"{BASE_URL}/tasks", headers=headers)
    print(f"Response status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 401:
        print("[OK] Correctly returns 401 when no token provided")

if __name__ == "__main__":
    print("\n[TEST] Authentication Debug Test Script")
    print("This script tests the login -> create task flow\n")
    
    # First test without token to verify 401 is returned correctly
    test_token_without_auth()
    
    # Then test full auth flow
    success = test_auth_flow()
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    if success:
        print("[OK] Authentication is working correctly!")
        print("If frontend still gets 401, check:")
        print("  1. Browser console for [API Client] logs")
        print("  2. Verify token is stored in localStorage")
        print("  3. Check if token is being sent with requests")
    else:
        print("[WARN] Authentication issue detected")
        print("Check backend terminal for detailed DEBUG logs")
        print("Look for:")
        print("  - 'Authorization header:' - is it present?")
        print("  - 'Token extracted' - was token parsed correctly?")
        print("  - 'Token verified' - did JWT decoding succeed?")
        print("  - 'User authenticated' - was user found in DB?")
    
    print()
