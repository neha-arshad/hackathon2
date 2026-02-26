"""
Test script to verify bcrypt/passlib compatibility fix.
Run this after installing the updated requirements.

Usage:
    python test_bcrypt_fix.py
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_bcrypt_version():
    """Test that bcrypt version is compatible."""
    import bcrypt
    print(f"bcrypt version: {bcrypt.__version__}")
    
    # Check version is compatible
    version_parts = [int(x) for x in bcrypt.__version__.split('.')[:2]]
    if version_parts[0] > 3:
        print("WARNING: bcrypt 4.x+ may have compatibility issues with passlib")
        return False
    print("✓ bcrypt version is compatible (3.x)")
    return True


def test_passlib_bcrypt():
    """Test that passlib can use bcrypt correctly."""
    from passlib.context import CryptContext
    
    try:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        print("✓ passlib CryptContext created with bcrypt")
        return True
    except Exception as e:
        print(f"✗ Failed to create CryptContext: {e}")
        return False


def test_password_hashing():
    """Test password hashing and verification."""
    from security import get_password_hash, verify_password
    
    test_cases = [
        ("simple_password", "Simple ASCII password"),
        ("a" * 50, "50 character password"),
        ("a" * 72, "72 byte password (exact limit)"),
        ("a" * 100, "100 byte password (over limit)"),
        ("パスワード", "Japanese characters"),
        ("Пароль", "Cyrillic characters"),
        ("🔐🔒🔑", "Emoji characters"),
        ("Mixed_パスワード_123", "Mixed scripts"),
    ]
    
    all_passed = True
    
    for password, description in test_cases:
        try:
            byte_len = len(password.encode('utf-8'))
            hashed = get_password_hash(password)
            verified = verify_password(password, hashed)
            
            if verified:
                print(f"✓ {description} ({byte_len} bytes): hashed and verified")
            else:
                print(f"✗ {description} ({byte_len} bytes): verification FAILED")
                all_passed = False
        except Exception as e:
            print(f"✗ {description} ({byte_len} bytes): ERROR - {e}")
            all_passed = False
    
    return all_passed


def test_long_password_truncation():
    """Test that long passwords are handled correctly."""
    from security import get_password_hash, verify_password, _truncate_password
    
    # Create a password longer than 72 bytes
    long_password = "a" * 100
    
    # Test truncation function
    truncated = _truncate_password(long_password)
    truncated_len = len(truncated.encode('utf-8'))
    
    if truncated_len <= 72:
        print(f"✓ Long password truncated correctly: 100 bytes -> {truncated_len} bytes")
    else:
        print(f"✗ Long password NOT truncated: {truncated_len} bytes")
        return False
    
    # Test that hashing and verification work
    hashed = get_password_hash(long_password)
    if verify_password(long_password, hashed):
        print("✓ Long password hashing and verification works")
        return True
    else:
        print("✗ Long password verification FAILED")
        return False


def test_utf8_truncation():
    """Test that UTF-8 multi-byte characters are handled correctly."""
    from security import _truncate_password
    
    # Create a password with multi-byte characters that would be cut
    # Each Japanese character is 3 bytes in UTF-8
    utf8_password = "パスワード" * 30  # 120 bytes
    
    truncated = _truncate_password(utf8_password)
    truncated_len = len(truncated.encode('utf-8'))
    
    if truncated_len <= 72:
        print(f"✓ UTF-8 password truncated correctly: {len(utf8_password.encode('utf-8'))} bytes -> {truncated_len} bytes")
        
        # Verify the truncated string is valid UTF-8
        try:
            truncated.encode('utf-8').decode('utf-8')
            print("✓ Truncated password is valid UTF-8")
            return True
        except UnicodeDecodeError:
            print("✗ Truncated password is NOT valid UTF-8")
            return False
    else:
        print(f"✗ UTF-8 password NOT truncated: {truncated_len} bytes")
        return False


def main():
    print("=" * 60)
    print("Bcrypt/Passlib Compatibility Test")
    print("=" * 60)
    print()
    
    results = []
    
    print("1. Testing bcrypt version...")
    results.append(test_bcrypt_version())
    print()
    
    print("2. Testing passlib bcrypt context...")
    results.append(test_passlib_bcrypt())
    print()
    
    print("3. Testing password hashing...")
    results.append(test_password_hashing())
    print()
    
    print("4. Testing long password truncation...")
    results.append(test_long_password_truncation())
    print()
    
    print("5. Testing UTF-8 truncation...")
    results.append(test_utf8_truncation())
    print()
    
    print("=" * 60)
    if all(results):
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
