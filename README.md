# Full-Stack Todo Application

This is a full-stack todo application built with FastAPI (backend) and Next.js (frontend), preserving the business logic from Phase I.

## Architecture

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT-based (email + password)
- **API**: RESTful endpoints

### Frontend
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios

## Features

### Backend Features
- User registration and authentication
- Task CRUD operations
- Task filtering by completion status and priority
- Task search functionality
- Task sorting by creation date and priority
- JWT-based authentication and authorization
- Proper error handling and validation

### Frontend Features
- User-friendly authentication flow (login/signup)
- Protected dashboard with JWT
- Full task CRUD interface
- Advanced filtering (by status, priority)
- Search functionality
- Sorting options (by date, priority)
- Responsive UI with Tailwind CSS

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get JWT token

### Tasks
- `GET /tasks` - Get all user tasks
- `POST /tasks` - Create a new task
- `PUT /tasks/{id}` - Update a task
- `DELETE /tasks/{id}` - Delete a task
- `PUT /tasks/{id}/complete` - Mark task as complete/incomplete

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── models.py               # SQLAlchemy database models
├── schemas.py              # Pydantic schemas for request/response validation
├── database.py             # Database operations
├── services.py             # Business logic layer (integrates Phase I logic)
├── routes.py               # API route definitions
├── security.py             # Authentication and JWT utilities
├── config.py               # Configuration settings
├── dependencies.py         # FastAPI dependencies
├── errors.py               # Error handling utilities
└── requirements.txt        # Python dependencies

frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Home page
│   ├── auth/
│   │   ├── login/page.tsx  # Login page
│   │   └── signup/page.tsx # Signup page
│   └── dashboard/page.tsx  # Main dashboard with task management
├── package.json            # Node.js dependencies
├── tsconfig.json           # TypeScript configuration
├── tailwind.config.js      # Tailwind CSS configuration
└── postcss.config.js       # PostCSS configuration
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set up PostgreSQL database:
   - Create a database named `todoapp`
   - Update environment variables in `.env` file:
     ```
     DB_USER=your_db_username
     DB_PASSWORD=your_db_password
     DB_HOST=localhost
     DB_PORT=5432
     DB_NAME=todoapp
     SECRET_KEY=your_secret_key_here
     ```

4. Run the FastAPI application:
```bash
uvicorn main:app --reload --port 8000
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Run the Next.js development server:
```bash
npm run dev
```

The application will be accessible at `http://localhost:3000`.

## Environment Variables

For the backend, create a `.env` file in the backend directory with the following variables:

```
DB_USER=your_db_username
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=todoapp
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Phase I Logic Preservation

The application preserves the business logic from Phase I:
- Task validation rules (title cannot be empty, priority must be low/medium/high)
- Filtering and search functionality
- Sorting capabilities
- Task completion toggling
- All core task management operations

The Phase I logic has been integrated into the service layer (`services.py`) while maintaining separation between business logic and database operations.