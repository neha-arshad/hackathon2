"""
Final test to verify the authentication fixes work end-to-end
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_end_to_end_flow():
    print("Testing end-to-end authentication flow...")

    # Step 1: Register a new user
    print("\\n1. Registering a new user...")
    register_data = {
        "email": "e2e_test@example.com",
        "password": "securepassword123"
    }
    register_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print(f"   Registration Status: {register_response.status_code}")
    if register_response.status_code != 200:
        print(f"   Registration Error: {register_response.text}")
        return False

    # Step 2: Login to get token
    print("\\n2. Logging in to get token...")
    login_data = {
        "email": "e2e_test@example.com",
        "password": "securepassword123"
    }
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"   Login Status: {login_response.status_code}")
    if login_response.status_code != 200:
        print(f"   Login Error: {login_response.text}")
        return False
    
    token = login_response.json().get("access_token")
    print(f"   Got token: {token[:20]}..." if token else "   No token received")

    # Step 3: Test creating a task without token (should fail with 401)
    print("\\n3. Creating task without token (should fail with 401)...")
    no_auth_response = requests.post(f"{BASE_URL}/tasks", json={
        "title": "Test task without auth",
        "description": "This should fail",
        "priority": "medium"
    })
    print(f"   Status: {no_auth_response.status_code}")
    if no_auth_response.status_code != 401:
        print(f"   Expected 401, got {no_auth_response.status_code}")
        return False
    print("   ✓ Correctly rejected request without authentication")

    # Step 4: Test creating a task with invalid token (should fail with 401)
    print("\\n4. Creating task with invalid token (should fail with 401)...")
    invalid_auth_response = requests.post(f"{BASE_URL}/tasks", 
                                       json={
                                           "title": "Test task with invalid token",
                                           "description": "This should fail",
                                           "priority": "medium"
                                       },
                                       headers={"Authorization": "Bearer invalid_token_here"})
    print(f"   Status: {invalid_auth_response.status_code}")
    if invalid_auth_response.status_code != 401:
        print(f"   Expected 401, got {invalid_auth_response.status_code}")
        return False
    print("   ✓ Correctly rejected request with invalid token")

    # Step 5: Test creating a task with valid token (should succeed)
    print("\\n5. Creating task with valid token (should succeed)...")
    valid_auth_response = requests.post(f"{BASE_URL}/tasks", 
                                     json={
                                         "title": "Successfully created task",
                                         "description": "This should work with valid token",
                                         "priority": "high"
                                     },
                                     headers={"Authorization": f"Bearer {token}"})
    print(f"   Status: {valid_auth_response.status_code}")
    if valid_auth_response.status_code != 200:
        print(f"   Expected 200, got {valid_auth_response.status_code}")
        print(f"   Error: {valid_auth_response.text}")
        return False
    
    created_task = valid_auth_response.json()
    print(f"   Created task: {created_task['title']} (ID: {created_task['id']})")
    print("   ✓ Successfully created task with valid authentication")

    # Step 6: Test getting tasks with valid token (should succeed)
    print("\\n6. Getting tasks with valid token (should succeed)...")
    get_tasks_response = requests.get(f"{BASE_URL}/tasks", 
                                   headers={"Authorization": f"Bearer {token}"})
    print(f"   Status: {get_tasks_response.status_code}")
    if get_tasks_response.status_code != 200:
        print(f"   Expected 200, got {get_tasks_response.status_code}")
        return False
    
    tasks = get_tasks_response.json()
    print(f"   Retrieved {len(tasks)} tasks")
    print("   ✓ Successfully retrieved tasks with valid authentication")

    # Step 7: Test updating the task
    print("\\n7. Updating task with valid token (should succeed)...")
    task_id = created_task['id']
    update_response = requests.put(f"{BASE_URL}/tasks/{task_id}", 
                                json={
                                    "title": "Updated task title",
                                    "description": "Updated description",
                                    "priority": "low"
                                },
                                headers={"Authorization": f"Bearer {token}"})
    print(f"   Status: {update_response.status_code}")
    if update_response.status_code != 200:
        print(f"   Expected 200, got {update_response.status_code}")
        return False
    
    updated_task = update_response.json()
    print(f"   Updated task: {updated_task['title']}")
    print("   ✓ Successfully updated task with valid authentication")

    # Step 8: Test marking task as complete
    print("\\n8. Marking task as complete (should succeed)...")
    complete_response = requests.put(f"{BASE_URL}/tasks/{task_id}/complete", 
                                  json={"completed": True},
                                  headers={"Authorization": f"Bearer {token}"})
    print(f"   Status: {complete_response.status_code}")
    if complete_response.status_code != 200:
        print(f"   Expected 200, got {complete_response.status_code}")
        return False
    print("   ✓ Successfully marked task as complete")

    # Step 9: Test deleting the task
    print("\\n9. Deleting task with valid token (should succeed)...")
    delete_response = requests.delete(f"{BASE_URL}/tasks/{task_id}", 
                                   headers={"Authorization": f"Bearer {token}"})
    print(f"   Status: {delete_response.status_code}")
    if delete_response.status_code != 200:
        print(f"   Expected 200, got {delete_response.status_code}")
        return False
    print("   ✓ Successfully deleted task with valid authentication")

    print("\\n✓ All end-to-end tests passed! Authentication is working correctly.")
    return True

if __name__ == "__main__":
    success = test_end_to_end_flow()
    if success:
        print("\\n🎉 Authentication fixes are working perfectly!")
        print("  - Missing tokens return 401")
        print("  - Invalid tokens return 401") 
        print("  - Valid tokens allow access to protected endpoints")
        print("  - All CRUD operations work with proper authentication")
    else:
        print("\\n❌ Some tests failed. Please check the implementation.")