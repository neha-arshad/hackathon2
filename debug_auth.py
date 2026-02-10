"""
Debug script to understand the authentication behavior
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def debug_auth_behavior():
    print("Testing different authentication scenarios...")

    # Test 1: No Authorization header at all
    print("\\n1. Request with no Authorization header:")
    try:
        response = requests.post(f"{BASE_URL}/tasks", json={
            "title": "Test task",
            "description": "Test description",
            "priority": "medium"
        }, headers={})  # No Authorization header
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test 2: Empty Authorization header
    print("\\n2. Request with empty Authorization header:")
    try:
        response = requests.post(f"{BASE_URL}/tasks", json={
            "title": "Test task",
            "description": "Test description",
            "priority": "medium"
        }, headers={"Authorization": ""})
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test 3: Malformed Authorization header
    print("\\n3. Request with malformed Authorization header:")
    try:
        response = requests.post(f"{BASE_URL}/tasks", json={
            "title": "Test task",
            "description": "Test description",
            "priority": "medium"
        }, headers={"Authorization": "InvalidFormat"})
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test 4: Valid Bearer format but invalid token
    print("\\n4. Request with Bearer + invalid token:")
    try:
        response = requests.post(f"{BASE_URL}/tasks", json={
            "title": "Test task",
            "description": "Test description",
            "priority": "medium"
        }, headers={"Authorization": "Bearer invalid_token_here"})
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    debug_auth_behavior()