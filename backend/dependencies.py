from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import database, security, models
from models import get_session_local
from database import get_user_by_email
from security import verify_token

security = HTTPBearer()

def get_db():
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()

def get_current_user(db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    email = verify_token(credentials.credentials, credentials_exception)
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user