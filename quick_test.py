import requests
import json

BASE_URL = 'http://localhost:8000'

# Test 1: Register user
print('Test 1: Registering user...')
register_data = {'email': 'test_final@example.com', 'password': 'password123'}
reg_resp = requests.post(f'{BASE_URL}/auth/register', json=register_data)
print(f'Register status: {reg_resp.status_code}')

# Test 2: Login to get token
print('Test 2: Logging in...')
login_data = {'email': 'test_final@example.com', 'password': 'password123'}
login_resp = requests.post(f'{BASE_URL}/auth/login', json=login_data)
token = login_resp.json().get('access_token') if login_resp.status_code == 200 else None
print(f'Login status: {login_resp.status_code}')
print(f'Token received: {bool(token)}')

# Test 3: Create task without token (should fail)
print('Test 3: Creating task without token...')
no_auth_resp = requests.post(f'{BASE_URL}/tasks', json={'title': 'Test', 'description': '', 'priority': 'medium'})
print(f'Status without auth: {no_auth_resp.status_code} (expected: 401)')

# Test 4: Create task with valid token (should succeed)
if token:
    print('Test 4: Creating task with valid token...')
    valid_auth_resp = requests.post(f'{BASE_URL}/tasks', 
                                   json={'title': 'Valid Auth Task', 'description': '', 'priority': 'medium'},
                                   headers={'Authorization': f'Bearer {token}'})
    print(f'Status with valid auth: {valid_auth_resp.status_code} (expected: 200)')
    if valid_auth_resp.status_code == 200:
        task_data = valid_auth_resp.json()
        print(f'Task created successfully: {task_data["title"]}')
        print(f'Task ID: {task_data["id"]}')
    else:
        print(f'Error: {valid_auth_resp.text}')
else:
    print('No token available for test 4')

print('\nAll tests completed!')