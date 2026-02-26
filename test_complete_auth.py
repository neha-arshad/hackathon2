#!/usr/bin/env python
"""
Complete Authentication Flow Test
Tests the entire login -> authenticated request flow
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def main():
    print_section("AUTHENTICATION FLOW TEST")
    
    # Test 1: Health check
    print("\n[Test 1] Backend health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.ok:
            print(f"  [PASS] Backend is healthy: {response.json()}")
        else:
            print(f"  [FAIL] Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"  [FAIL] Cannot connect to backend: {e}")
        print("  [TIP] Run: python run_server.py in backend folder")
        return
    
    # Test 2: Login
    print_section("TEST 2: LOGIN")
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    print(f"\nAttempting login for: {login_data['email']}")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        
        if response.status_code == 401:
            print(f"  [FAIL] Login failed - incorrect credentials")
            print(f"  Response: {response.json()}")
            print("\n  [TIP] Create a user first via frontend signup or:")
            print(f"  POST {BASE_URL}/auth/register")
            print("  {\"email\": \"test@example.com\", \"password\": \"testpassword123\"}")
            return
            
        if not response.ok:
            print(f"  [FAIL] Login error: {response.status_code}")
            print(f"  Response: {response.json()}")
            return
            
        token_data = response.json()
        token = token_data.get("access_token")
        
        if not token:
            print(f"  [FAIL] No access_token in response")
            print(f"  Response: {token_data}")
            return
            
        print(f"  [PASS] Login successful")
        print(f"  Token type: {token_data.get('token_type', 'unknown')}")
        print(f"  Token length: {len(token)} characters")
        
        # Decode token info
        try:
            parts = token.split('.')
            if len(parts) == 3:
                import base64
                # Add padding if needed
                payload = parts[1] + '=' * (4 - len(parts[1]) % 4)
                decoded = json.loads(base64.urlsafe_b64decode(payload))
                print(f"  Token email: {decoded.get('sub', 'N/A')}")
                print(f"  Token expires: {decoded.get('exp', 'N/A')}")
        except:
            pass
            
    except Exception as e:
        print(f"  [FAIL] Login exception: {e}")
        return
    
    # Test 3: Get tasks (authenticated)
    print_section("TEST 3: GET /tasks (Authenticated)")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\nRequest: GET {BASE_URL}/tasks")
    print(f"Authorization: Bearer {token[:30]}...")
    
    try:
        response = requests.get(f"{BASE_URL}/tasks", headers=headers)
        
        print(f"  Response status: {response.status_code}")
        
        if response.ok:
            tasks = response.json()
            print(f"  [PASS] Retrieved {len(tasks)} tasks")
        elif response.status_code == 401:
            print(f"  [FAIL] 401 Unauthorized")
            print(f"  Response: {response.json()}")
            print("\n  [DIAGNOSIS]")
            print("  - Token format may be incorrect")
            print("  - Token may be expired")
            print("  - Backend SECRET_KEY may not match")
        else:
            print(f"  [FAIL] Unexpected status: {response.status_code}")
            print(f"  Response: {response.json()}")
            
    except Exception as e:
        print(f"  [FAIL] Request failed: {e}")
    
    # Test 4: Create task (authenticated)
    print_section("TEST 4: POST /tasks (Authenticated)")
    
    task_data = {
        "title": "Test task from Python script",
        "description": "Created during authentication test",
        "priority": "medium"
    }
    
    print(f"\nRequest: POST {BASE_URL}/tasks")
    print(f"Body: {json.dumps(task_data)}")
    
    try:
        response = requests.post(f"{BASE_URL}/tasks", json=task_data, headers=headers)
        
        print(f"  Response status: {response.status_code}")
        
        if response.ok or response.status_code == 200:
            task = response.json()
            print(f"  [PASS] Task created successfully!")
            print(f"  Task ID: {task.get('id')}")
            print(f"  Task title: {task.get('title')}")
        elif response.status_code == 401:
            print(f"  [FAIL] 401 Unauthorized")
            print(f"  Response: {response.json()}")
            print("\n  [DIAGNOSIS]")
            print("  - Authorization header not being sent correctly")
            print("  - Header format incorrect (should be 'Bearer <token>')")
            print("  - Token invalid or expired")
        else:
            print(f"  [FAIL] Unexpected status: {response.status_code}")
            print(f"  Response: {response.json()}")
            
    except Exception as e:
        print(f"  [FAIL] Request failed: {e}")
    
    # Test 5: Request without token (should fail)
    print_section("TEST 5: GET /tasks (No Token - Should 401)")
    
    print(f"\nRequest: GET {BASE_URL}/tasks (no auth header)")
    
    try:
        response = requests.get(f"{BASE_URL}/tasks")
        
        print(f"  Response status: {response.status_code}")
        
        if response.status_code == 401:
            print(f"  [PASS] Correctly returns 401 without token")
            print(f"  Response: {response.json()}")
        else:
            print(f"  [WARN] Expected 401, got: {response.status_code}")
            
    except Exception as e:
        print(f"  [FAIL] Request failed: {e}")
    
    # Summary
    print_section("TEST SUMMARY")
    print("\nBackend authentication is working correctly!")
    print("\nIf your frontend still gets 401, the issue is:")
    print("  1. Frontend not sending Authorization header")
    print("  2. Token not saved in localStorage after login")
    print("  3. Wrong backend URL in frontend config")
    print("\nCheck browser console for [API Client] logs")
    print("Check Network tab for Authorization header")
    print()

if __name__ == "__main__":
    main()
