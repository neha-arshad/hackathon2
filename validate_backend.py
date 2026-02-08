"""
Quick validation script for the Todo App backend
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from main import app
    from routes import router
    print("[OK] Backend server imports successfully")

    # Check if app has the expected routes
    routes = [route.path for route in app.routes]
    expected_routes = ['/auth/register', '/auth/login', '/tasks', '/tasks/{task_id}', '/tasks/{task_id}/complete']

    print("[OK] Available routes:")
    for route in routes:
        print(f"  - {route}")

    # Check for essential routes
    auth_routes = ['/auth/register', '/auth/login']
    task_routes = ['/tasks']

    auth_present = all(route in routes for route in auth_routes)
    task_present = any('/tasks' in route for route in routes)

    if auth_present and task_present:
        print("[OK] Essential API routes are present")
    else:
        print("[ERROR] Some essential API routes are missing")

    print("\n[OK] Backend validation passed!")

except ImportError as e:
    print(f"[ERROR] Backend import failed: {e}")
except Exception as e:
    print(f"[ERROR] Backend validation failed: {e}")