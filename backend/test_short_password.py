#!/usr/bin/env python3
"""
Test script to verify the password hashing function works with short passwords
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from security import get_password_hash

    # Test with a short password
    short_password = "testpass123"
    print(f"Testing password of length: {len(short_password)}")

    hashed = get_password_hash(short_password)
    print("Short password hashing successful!")
    print(f"Hashed short password: {hashed[:50]}...")  # Show first 50 chars

    print("SUCCESS: Password hashing test passed!")

except Exception as e:
    print(f"❌ Error in password hashing: {str(e)}")
    import traceback
    traceback.print_exc()