#!/usr/bin/env python3
"""
Test script to verify the password hashing function works correctly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from security import get_password_hash

    # Test with a long password
    long_password = "a" * 80  # 80 characters, definitely over 72 bytes
    print(f"Testing password of length: {len(long_password)}")

    hashed = get_password_hash(long_password)
    print("Password hashing successful!")
    print(f"Hashed password: {hashed[:50]}...")  # Show first 50 chars

    # Test with a short password
    short_password = "shortpass"
    print(f"Testing password of length: {len(short_password)}")

    hashed_short = get_password_hash(short_password)
    print("Short password hashing successful!")
    print(f"Hashed short password: {hashed_short[:50]}...")  # Show first 50 chars

    print("✅ Password hashing test passed!")

except Exception as e:
    print(f"❌ Error in password hashing: {str(e)}")
    import traceback
    traceback.print_exc()