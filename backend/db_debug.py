#!/usr/bin/env python3
"""
Debug script to check database URL configuration
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and print the database URL before creating engine
from models import get_database_url

print("DATABASE_URL environment variable:", os.getenv("DATABASE_URL", "Not set"))

db_url = get_database_url()
print("Parsed database URL:", db_url)

# Now test the connection
try:
    from sqlalchemy import text
    from models import get_engine

    print("Getting engine...")
    engine = get_engine()

    print("Testing connection...")
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        version = result.fetchone()
        print("SUCCESS: Successfully connected to PostgreSQL!")
        print(f"PostgreSQL version: {version[0]}")

except Exception as e:
    print(f"ERROR: Failed to connect to database: {str(e)}")
    import traceback
    traceback.print_exc()