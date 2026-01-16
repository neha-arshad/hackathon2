# Backend Setup Guide

## Prerequisites

- Python 3.8+
- PostgreSQL database

## Installation

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables by creating a `.env` file:
```
DB_USER=your_postgres_username
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=todoapp
SECRET_KEY=your_secret_key_here_must_be_long_and_random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

4. Initialize the database:
```bash
python init_db.py
```

5. Start the server:
```bash
python run_server.py
```

Or alternatively:
```bash
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

After starting the server, you can view the API documentation at:
- `http://localhost:8000/docs` (Swagger UI)
- `http://localhost:8000/redoc` (ReDoc)

## Troubleshooting

### Import Errors
If you encounter import errors, make sure you're running the server from the backend directory and all modules are properly installed.

### Database Connection Issues
- Ensure PostgreSQL is running
- Verify your database credentials in the `.env` file
- Make sure the database specified in `DB_NAME` exists

### Registration Issues
- Ensure the database tables are created by running `python init_db.py`
- Check that the users table exists in your database