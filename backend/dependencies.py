from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
import database, security, models
from models import get_session_local
from database import get_user_by_email
from security import verify_token
from fastapi import Request
import logging
import re

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_db():
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()


def extract_token_from_header(authorization: str | None) -> str | None:
    """
    Extract the JWT token from an Authorization header.
    
    Handles various formats:
    - "Bearer <token>" -> <token>
    - "bearer <token>" -> <token> (case-insensitive)
    - "Bearer Bearer <token>" -> <token> (handles double prefix)
    - "<token>" -> <token> (no prefix)
    
    Returns None if the header is empty or malformed.
    """
    if not authorization:
        return None
    
    # Strip whitespace
    auth = authorization.strip()
    
    if not auth:
        return None
    
    # Remove "Bearer " prefix (case-insensitive), handling multiple occurrences
    # This handles cases like "Bearer Bearer token" -> "token"
    pattern = re.compile(r'^Bearer\s+', re.IGNORECASE)
    while pattern.match(auth):
        auth = pattern.sub('', auth)
    
    return auth.strip() if auth.strip() else None


def validate_jwt_format(token: str) -> bool:
    """
    Validate that a token looks like a valid JWT format.
    JWT should have exactly 3 parts separated by dots.
    """
    if not token:
        return False
    
    parts = token.split('.')
    if len(parts) != 3:
        return False
    
    # Each part should be non-empty and contain only valid base64url characters
    base64url_pattern = re.compile(r'^[A-Za-z0-9_-]+$')
    return all(len(part) > 0 and base64url_pattern.match(part) for part in parts)


# Custom dependency to handle authentication with consistent 401 responses
async def get_current_user(request: Request, db: Session = Depends(get_db)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials - token missing, invalid, or expired",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Extract authorization header
    authorization = request.headers.get("authorization")

    # Debug logging (truncate for readability)
    auth_preview = authorization[:50] + "..." if authorization and len(authorization) > 50 else authorization
    logger.debug(f"Authorization header received: {auth_preview or 'None'}")

    if not authorization:
        logger.warning("No authorization header found")
        raise credentials_exception

    # Extract token, handling various formats including double "Bearer" prefix
    token = extract_token_from_header(authorization)

    if not token:
        logger.warning("Could not extract token from authorization header")
        raise credentials_exception

    # Validate JWT format before attempting to decode
    if not validate_jwt_format(token):
        logger.warning(f"Invalid JWT format received (length: {len(token)})")
        raise credentials_exception

    logger.debug(f"Token extracted and validated (length: {len(token)})")

    try:
        email = verify_token(token, credentials_exception)
        logger.debug(f"Token verified, email: {email}")
        user = get_user_by_email(db, email=email)
        if user is None:
            # User not found - this could be considered a 401 since the token contains invalid user info
            logger.warning(f"User not found in database: {email}")
            raise credentials_exception
        logger.debug(f"User authenticated successfully: {user.email}")
        return user
    except HTTPException as e:
        logger.warning(f"HTTPException during token verification: {e.detail}")
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error during authentication: {type(e).__name__}: {e}")
        # Any other exception during token verification
        raise credentials_exception