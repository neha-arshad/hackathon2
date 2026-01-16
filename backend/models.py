from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
import os
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Global variables for engine and session factory
engine = None
SessionLocal = None
Base = declarative_base()

def get_database_url():
    """Get the database URL from environment variables."""
    DATABASE_URL = os.getenv("DATABASE_URL", "")

    if DATABASE_URL:
        # Parse the DATABASE_URL to extract components
        parsed_url = urlparse(DATABASE_URL)
        DB_USER = parsed_url.username or os.getenv("DB_USER", "postgres")
        DB_PASSWORD = parsed_url.password or os.getenv("DB_PASSWORD", "password")
        DB_HOST = parsed_url.hostname or os.getenv("DB_HOST", "localhost")
        DB_PORT = parsed_url.port or os.getenv("DB_PORT", "5432")
        DB_NAME = parsed_url.path.lstrip('/') or os.getenv("DB_NAME", "todoapp")

        SQLALCHEMY_DATABASE_URL = DATABASE_URL
    else:
        # Fallback to individual environment variables
        DB_USER = os.getenv("DB_USER", "postgres")
        DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
        DB_HOST = os.getenv("DB_HOST", "localhost")
        DB_PORT = os.getenv("DB_PORT", "5432")
        DB_NAME = os.getenv("DB_NAME", "todoapp")

        SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    return SQLALCHEMY_DATABASE_URL

def get_engine():
    """Get the SQLAlchemy engine, creating it if it doesn't exist."""
    global engine
    if engine is None:
        SQLALCHEMY_DATABASE_URL = get_database_url()
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
    return engine

def get_session_local():
    """Get the SQLAlchemy SessionLocal, creating it if it doesn't exist."""
    global SessionLocal
    if SessionLocal is None:
        engine = get_engine()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, default="")
    completed = Column(Boolean, default=False)
    priority = Column(String, default="medium")  # low, medium, high
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, index=True)