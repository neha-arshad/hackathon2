#!/usr/bin/env python3
"""
Test script to verify database connection
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from sqlalchemy import text
    from models import get_engine

    print("Attempting to connect to the database...")

    # Get the engine (this will initialize it with the correct URL)
    engine = get_engine()

    # Test the connection
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        version = result.fetchone()
        print("SUCCESS: Successfully connected to PostgreSQL!")
        print(f"PostgreSQL version: {version[0]}")

except Exception as e:
    print(f"ERROR: Failed to connect to database: {str(e)}")
    sys.exit(1)

print("✅ Database connection test passed!")