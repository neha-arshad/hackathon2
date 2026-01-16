from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, get_engine, get_session_local
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use the functions from models to get the engine and session factory
engine = get_engine()
SessionLocal = get_session_local()

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()