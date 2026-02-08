#!/usr/bin/env python
"""
Script to start the backend server with proper configuration
"""

import subprocess
import sys
import os

def start_server():
    print("Starting backend server on port 8001...")

    # Change to backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_dir)

    # Start the server
    try:
        subprocess.run([sys.executable, '-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', '8001', '--reload'])
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    start_server()