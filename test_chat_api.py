#!/usr/bin/env python3
"""
Test script to check the chat API functionality
"""

import requests
import json

def test_chat_api():
    print("Testing chat API connection...")

    # Test the chat endpoint
    url = "http://localhost:8001/chat"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "message": "Hello, can you help me with my tasks?"
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            response_data = response.json()
            print(f"Response: {response_data}")
        else:
            print(f"Error Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print("Connection error: Could not connect to the chat API at http://localhost:8001/chat")
        print("Make sure the AI agent server is running on port 8001")
    except Exception as e:
        print(f"An error occurred: {e}")

def test_health_check():
    print("\nTesting health check endpoint...")

    # Test the root endpoint
    url = "http://localhost:8001/"

    try:
        response = requests.get(url)
        print(f"Health Check Status Code: {response.status_code}")
        print(f"Health Check Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("Connection error: Could not connect to the server at http://localhost:8001/")
    except Exception as e:
        print(f"An error occurred during health check: {e}")

if __name__ == "__main__":
    print("Starting chat API tests...")
    test_health_check()
    test_chat_api()