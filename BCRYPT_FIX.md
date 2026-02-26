# Bcrypt/Passlib Compatibility Fix

## Problem

The backend was experiencing bcrypt version compatibility issues:

```
WARNING:passlib.handlers.bcrypt:(trapped) error reading bcrypt version
AttributeError: module 'bcrypt' has no attribute '__about__'
ERROR:security:Error verifying password: password cannot be longer than 72 bytes
```

### Root Causes

1. **bcrypt version mismatch**: `passlib[bcrypt]==1.7.4` is incompatible with `bcrypt>=4.0.0`
   - bcrypt 4.0+ removed the `__about__` attribute that passlib tries to read
   - This causes version detection failures and warnings

2. **Password length limit**: bcrypt has a hard 72-byte limit on passwords
   - Passwords exceeding 72 bytes cause errors during hashing/verification
   - UTF-8 multi-byte characters complicate simple character-based truncation

## Solution

### 1. Pin Compatible bcrypt Version

Updated `backend/requirements.txt` to explicitly pin bcrypt to a compatible version:

```txt
bcrypt==3.2.2
passlib[bcrypt]==1.7.4
```

### 2. Robust Password Truncation

Updated `backend/security.py` with proper password handling:

- Added `_truncate_password()` function that:
  - Correctly handles UTF-8 multi-byte characters
  - Truncates to exactly 72 bytes (not characters)
  - Gracefully handles edge cases

- Updated `get_password_hash()` and `verify_password()` to:
  - Always truncate passwords before hashing/verification
  - Log when truncation occurs
  - Provide clear error messages

## Installation Commands

### Clean Install (Recommended)

```bash
# Navigate to backend directory
cd backend

# Uninstall existing packages
pip uninstall -y bcrypt passlib

# Clear pip cache (optional, helps if you have cached incompatible versions)
pip cache purge

# Reinstall with pinned versions
pip install -r requirements.txt
```

### Quick Fix

```bash
pip install --force-reinstall bcrypt==3.2.2 passlib[bcrypt]==1.7.4
```

### Verify Installation

```bash
# Check installed versions
pip show bcrypt
pip show passlib

# Expected output:
# bcrypt: 3.2.2
# passlib: 1.7.4
```

## Testing

After installation, verify the fix works:

```bash
# Test password hashing
python -c "
from security import get_password_hash, verify_password

# Test normal password
hashed = get_password_hash('test_password')
print(f'Hash created: {hashed[:20]}...')
print(f'Verification: {verify_password(\"test_password\", hashed)}')

# Test long password (>72 bytes)
long_password = 'a' * 100
hashed_long = get_password_hash(long_password)
print(f'Long password hashed: {verify_password(long_password, hashed_long)}')

# Test UTF-8 password
utf8_password = 'パスワードテスト' * 10
hashed_utf8 = get_password_hash(utf8_password)
print(f'UTF-8 password hashed: {verify_password(utf8_password, hashed_utf8)}')
"
```

## Production Notes

### Password Length Policy

While the code now handles long passwords safely, consider implementing a password policy:

- **Minimum length**: 8 characters (recommended)
- **Maximum length**: 72 bytes (bcrypt limit)
- **Recommendation**: Enforce 8-128 character passwords at the API level

### Example Validation

```python
from fastapi import HTTPException

def validate_password(password: str) -> None:
    if len(password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters"
        )
    if len(password.encode('utf-8')) > 72:
        raise HTTPException(
            status_code=400,
            detail="Password must not exceed 72 bytes"
        )
```

### Migration for Existing Users

Existing password hashes are unaffected. The fix only changes how new passwords are hashed and verified:

- **Existing hashes**: Continue to work as before
- **New registrations**: Use the improved truncation logic
- **Login**: Both old and new hashes are verified correctly

## Files Changed

1. `backend/requirements.txt` - Added `bcrypt==3.2.2`
2. `backend/security.py` - Added robust password truncation

## References

- [passlib bcrypt compatibility](https://passlib.readthedocs.io/en/stable/lib/passlib.hash.bcrypt.html)
- [bcrypt password limit](https://github.com/pyca/bcrypt/issues/718)
- [CVE-2019-16923](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-16923) - bcrypt 72-byte limit discussion
