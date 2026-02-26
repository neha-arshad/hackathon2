from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status
from config import settings
import logging
import re

logger = logging.getLogger(__name__)

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

# Bcrypt has a 72-byte password limit. We truncate to 72 bytes to comply.
BCRYPT_MAX_PASSWORD_LENGTH = 72

# Configure passlib to use bcrypt with proper settings
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def validate_jwt_format(token: str) -> bool:
    """
    Validate that a token looks like a valid JWT format before attempting to decode.
    JWT should have exactly 3 parts separated by dots.
    """
    if not token or not isinstance(token, str):
        return False
    
    # Token should be a reasonable length (not too short, not too long)
    if len(token) < 50 or len(token) > 10000:
        logger.warning(f"Token length suspicious: {len(token)}")
        return False
    
    parts = token.split('.')
    if len(parts) != 3:
        logger.warning(f"Invalid JWT structure: expected 3 parts, got {len(parts)}")
        return False
    
    # Each part should be non-empty and contain only valid base64url characters
    base64url_pattern = re.compile(r'^[A-Za-z0-9_-]+$')
    for i, part in enumerate(parts):
        if not part:
            logger.warning(f"JWT part {i} is empty")
            return False
        if not base64url_pattern.match(part):
            logger.warning(f"JWT part {i} contains invalid characters")
            return False
    
    return True


def _truncate_password(password: str) -> str:
    """
    Truncate password to comply with bcrypt's 72-byte limit.
    
    Bcrypt only processes the first 72 bytes of a password. To avoid errors
    and ensure consistent behavior, we explicitly truncate passwords that
    exceed this limit.
    
    Args:
        password: The raw password string
        
    Returns:
        Password truncated to at most 72 bytes when encoded as UTF-8
    """
    # Encode to bytes to check actual byte length
    password_bytes = password.encode('utf-8')
    
    if len(password_bytes) <= BCRYPT_MAX_PASSWORD_LENGTH:
        return password
    
    # Truncate to 72 bytes
    truncated_bytes = password_bytes[:BCRYPT_MAX_PASSWORD_LENGTH]
    
    # Try to decode back to string, handling potential multi-byte character cuts
    try:
        # Attempt to decode; if we cut a multi-byte character, this will fail
        return truncated_bytes.decode('utf-8')
    except UnicodeDecodeError:
        # If decoding fails, we cut in the middle of a multi-byte character
        # Keep removing bytes until we can decode successfully
        while len(truncated_bytes) > 0:
            try:
                return truncated_bytes.decode('utf-8')
            except UnicodeDecodeError:
                truncated_bytes = truncated_bytes[:-1]
        # Fallback: return empty string if all bytes were invalid
        return ""


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password: The raw password to verify
        hashed_password: The bcrypt hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        # Truncate password to comply with bcrypt limits before verification
        truncated_password = _truncate_password(plain_password)
        
        if truncated_password != plain_password:
            logger.debug("Password was truncated to comply with bcrypt 72-byte limit")
        
        return pwd_context.verify(truncated_password, hashed_password)
    except Exception as e:
        logger.error(f"Error verifying password: {type(e).__name__}: {e}")
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: The raw password to hash
        
    Returns:
        The bcrypt hashed password
        
    Note:
        Passwords longer than 72 bytes are truncated to comply with bcrypt's limit.
        This is a bcrypt limitation, not a security flaw - the truncated password
        still provides strong security.
    """
    # Truncate password to comply with bcrypt's 72-byte limit
    truncated_password = _truncate_password(password)
    
    if truncated_password != password:
        logger.info(f"Password truncated from {len(password.encode('utf-8'))} bytes to {BCRYPT_MAX_PASSWORD_LENGTH} bytes for bcrypt compatibility")
    
    return pwd_context.hash(truncated_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.debug(f"Token created with exp: {expire}, data: {data}")
    return encoded_jwt


def verify_token(token: str, credentials_exception: HTTPException) -> str:
    """
    Verify and decode a JWT token.
    
    Args:
        token: The raw JWT token (without "Bearer " prefix)
        credentials_exception: The exception to raise on failure
        
    Returns:
        The email from the token payload
        
    Raises:
        HTTPException: 401 Unauthorized if token is invalid, expired, or malformed
    """
    # Validate JWT format before attempting to decode
    if not validate_jwt_format(token):
        logger.warning(f"Token validation failed: invalid JWT format")
        raise credentials_exception
    
    try:
        logger.debug(f"Verifying token (length: {len(token)})")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            logger.warning("Token payload missing 'sub' claim")
            raise credentials_exception
        logger.debug(f"Token decoded successfully, email: {email}")
        return email
    except jwt.ExpiredSignatureError:
        # Token has expired - this should be a 401
        logger.warning("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTClaimsError as e:
        # Invalid claims - this should be a 401
        logger.warning(f"Invalid token claims: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        # Catch all JWT errors (InvalidSignatureError, DecodeError, etc.)
        logger.warning(f"Invalid token: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or malformed token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        # Other JWT errors from python-jose
        logger.warning(f"JWT error: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token validation failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        # Any other exception during token verification
        logger.error(f"Unexpected error verifying token: {type(e).__name__}: {e}")
        raise credentials_exception