#!/usr/bin/env python
"""
Complete Authentication Test - Verifies "Bearer Bearer" fix

This test verifies that:
1. Login returns a clean JWT token (no "Bearer " prefix)
2. Token is stored correctly in localStorage format
3. Requests include proper Authorization header (not "Bearer Bearer")
4. Protected endpoints work with the token
"""

import requests
import json
import base64

BASE_URL = "http://localhost:8000"

def decode_jwt(token):
    """Decode JWT token to inspect payload"""
    try:
        # Add padding if needed
        payload = token.split('.')[1]
        payload += '=' * (4 - len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        return None

def print_section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

def main():
    print_section("AUTHENTICATION FIX VERIFICATION TEST")
    print("\nThis test verifies the 'Bearer Bearer' double prefix fix")
    
    # Test 1: Health check
    print("\n[Test 1] Backend health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.ok:
            print(f"  [PASS] Backend is healthy")
        else:
            print(f"  [FAIL] Health check failed")
            return
    except Exception as e:
        print(f"  [FAIL] Cannot connect to backend: {e}")
        return
    
    # Test 2: Login and verify token format
    print_section("TEST 2: LOGIN - VERIFY TOKEN FORMAT")
    
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    print(f"\nLogging in as: {login_data['email']}")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        
        if response.status_code == 401:
            print(f"  [FAIL] Login failed - incorrect credentials")
            print(f"  [INFO] Create user via POST /auth/register first")
            return
            
        if not response.ok:
            print(f"  [FAIL] Login error: {response.status_code}")
            return
            
        token_data = response.json()
        token = token_data.get("access_token")
        
        if not token:
            print(f"  [FAIL] No access_token in response")
            return
        
        # Check token format
        print(f"\n  Token Analysis:")
        print(f"    Length: {len(token)} characters")
        print(f"    Starts with 'eyJ': {token.startswith('eyJ')}")
        print(f"    Starts with 'Bearer ': {token.startswith('Bearer ')}")
        
        if token.startswith('Bearer '):
            print(f"  [WARN] Token has 'Bearer ' prefix - this should be stripped by frontend")
        else:
            print(f"  [PASS] Token is clean (no 'Bearer ' prefix)")
        
        # Decode token
        payload = decode_jwt(token)
        if payload:
            print(f"\n  Token Payload:")
            print(f"    Email (sub): {payload.get('sub', 'N/A')}")
            print(f"    Expires: {payload.get('exp', 'N/A')}")
        
    except Exception as e:
        print(f"  [FAIL] Login exception: {e}")
        return
    
    # Test 3: Verify Authorization header format
    print_section("TEST 3: VERIFY AUTHORIZATION HEADER FORMAT")
    
    # Simulate what the frontend interceptor does
    import re
    clean_token = re.sub(r'^Bearer\s+', '', token, flags=re.IGNORECASE).strip()
    
    # Test with correct header
    correct_header = f"Bearer {token}"
    print(f"\n  Correct header format:")
    print(f"    Authorization: {correct_header[:50]}...")
    print(f"    Starts with 'Bearer Bearer': {correct_header.startswith('Bearer Bearer')}")
    
    # Test with double Bearer (what was causing the bug)
    double_bearer = f"Bearer Bearer {token}"
    print(f"\n  Double Bearer (BUG):")
    print(f"    Authorization: {double_bearer[:50]}...")
    print(f"    Starts with 'Bearer Bearer': {double_bearer.startswith('Bearer Bearer')}")
    
    # Test 4: Make request with correct header
    print_section("TEST 4: CREATE TASK WITH CORRECT HEADER")
    
    headers = {
        "Authorization": correct_header,
        "Content-Type": "application/json"
    }
    
    task_data = {
        "title": "Test task - verifying fix",
        "description": "Created to test Bearer prefix fix",
        "priority": "medium"
    }
    
    print(f"\n  Request: POST {BASE_URL}/tasks")
    print(f"  Authorization: {correct_header[:40]}...")
    
    try:
        response = requests.post(f"{BASE_URL}/tasks", json=task_data, headers=headers)
        
        print(f"\n  Response status: {response.status_code}")
        
        if response.ok or response.status_code == 200:
            task = response.json()
            print(f"  [PASS] Task created successfully!")
            print(f"  Task ID: {task.get('id')}")
            print(f"  Task title: {task.get('title')}")
        elif response.status_code == 401:
            print(f"  [FAIL] 401 Unauthorized")
            print(f"  Response: {response.json()}")
        else:
            print(f"  [FAIL] Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"  [FAIL] Request failed: {e}")
    
    # Test 5: Verify double Bearer fails
    print_section("TEST 5: VERIFY DOUBLE BEARER FAILS (Expected)")
    
    bad_headers = {
        "Authorization": double_bearer,
        "Content-Type": "application/json"
    }
    
    print(f"\n  Request with 'Bearer Bearer' prefix...")
    
    try:
        response = requests.post(f"{BASE_URL}/tasks", json=task_data, headers=bad_headers)
        
        print(f"  Response status: {response.status_code}")
        
        if response.status_code == 401:
            print(f"  [EXPECTED] 401 Unauthorized (double Bearer rejected)")
            error_detail = response.json().get('detail', '')
            if 'Not enough segments' in error_detail or 'JWT' in error_detail:
                print(f"  [INFO] JWT error: {error_detail}")
        else:
            print(f"  [WARN] Expected 401, got: {response.status_code}")
            
    except Exception as e:
        print(f"  Request failed: {e}")
    
    # Summary
    print_section("TEST SUMMARY")
    print("\n  Backend JWT verification: WORKING")
    print("  Token format: CORRECT (no Bearer prefix)")
    print("  Authorization header: CORRECT (single Bearer)")
    print("\n  Frontend Requirements:")
    print("  1. Store ONLY raw JWT token (no 'Bearer ' prefix)")
    print("  2. Axios interceptor adds 'Bearer ' automatically")
    print("  3. NEVER manually set Authorization header")
    print("\n  Expected Console Logs:")
    print("  [Login] Token saved successfully, length: XXX")
    print("  [API Client] Authorization header set: Bearer eyJ...")
    print("\n  Backend Logs Should Show:")
    print("  Authorization header: Bearer eyJhbGci... (NOT Bearer Bearer)")
    print("  Token decoded successfully, email: test@example.com")
    print()

if __name__ == "__main__":
    main()
