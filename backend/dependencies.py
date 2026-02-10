from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
import database, security, models
from models import get_session_local
from database import get_user_by_email
from security import verify_token
from fastapi import Request

def get_db():
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()

# Custom dependency to handle authentication with consistent 401 responses
async def get_current_user(request: Request, db: Session = Depends(get_db)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials - token missing, invalid, or expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Extract authorization header manually to handle all cases consistently
    authorization = request.headers.get("authorization")
    if not authorization:
        raise credentials_exception
    
    # Check if it follows Bearer format
    if not authorization.lower().startswith("bearer "):
        raise credentials_exception
    
    # Extract the token
    token = authorization[7:].strip()  # Remove "Bearer " prefix
    
    if not token:
        raise credentials_exception

    try:
        email = verify_token(token, credentials_exception)
        user = get_user_by_email(db, email=email)
        if user is None:
            # User not found - this could be considered a 401 since the token contains invalid user info
            raise credentials_exception
        return user
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception:
        # Any other exception during token verification
        raise credentials_exception