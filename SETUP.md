# PlacementPrep Setup Guide

This guide will help you set up the PlacementPrep application with all necessary dependencies.

## Prerequisites

Before starting, ensure you have the following installed:

1. **Node.js** (v18 or higher) - [Download from nodejs.org](https://nodejs.org/)
2. **Python** (v3.9 or higher) - [Download from python.org](https://python.org/)
3. **PostgreSQL** (v13 or higher) - [Download from postgresql.org](https://postgresql.org/)
4. **Redis** (v6 or higher) - [Download from redis.io](https://redis.io/)

## Installation Steps

### 1. Install Node.js Dependencies

```bash
# Install frontend dependencies
cd apps/frontend
npm install

# Install root dependencies (if any)
cd ../..
npm install
```

### 2. Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r apps/backend/requirements.txt
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb placement_prep

# Run database migrations
cd apps/backend
alembic upgrade head
```

### 4. Environment Configuration

Create environment files:

**apps/backend/.env**:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/placement_prep
DATABASE_URL_SYNC=postgresql://postgres:password@localhost:5432/placement_prep
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-change-in-production
GROQ_API_KEY=your-groq-api-key
```

**apps/frontend/.env**:
```env
VITE_API_URL=http://localhost:8000/api/v1
```

### 5. Start Services

Start the services in separate terminals:

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start PostgreSQL (if not running as service)
postgres -D /usr/local/var/postgres

# Terminal 3: Start Backend API
cd apps/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 4: Start Frontend
cd apps/frontend
npm run dev
```

## Troubleshooting

### TypeScript Issues

If you encounter TypeScript errors in the frontend:

1. Ensure all dependencies are installed: `npm install`
2. Clear TypeScript cache: `npx tsc --build --clean`
3. Restart your IDE/editor

### Python Import Issues

If you encounter Python import errors:

1. Ensure virtual environment is activated
2. Install dependencies: `pip install -r requirements.txt`
3. Check Python path: `python -c "import sys; print(sys.path)"`

### Database Connection Issues

1. Ensure PostgreSQL is running
2. Check database credentials in `.env` file
3. Verify database exists: `psql -l`

### Redis Connection Issues

1. Ensure Redis is running: `redis-cli ping`
2. Check Redis URL in `.env` file

## Development Commands

### Frontend
```bash
cd apps/frontend
npm run dev          # Start development server
npm run build        # Build for production
npm run lint         # Run linter
npm run test         # Run tests
```

### Backend
```bash
cd apps/backend
uvicorn main:app --reload    # Start development server
alembic revision --autogenerate -m "message"  # Create migration
alembic upgrade head         # Apply migrations
pytest                       # Run tests
black .                      # Format code
```

## Project Structure

```
placement-prep/
├── apps/
│   ├── frontend/           # React + TypeScript frontend
│   │   ├── src/
│   │   │   ├── components/ # React components
│   │   │   ├── contexts/   # React contexts
│   │   │   ├── services/   # API services
│   │   │   ├── types/      # TypeScript types
│   │   │   └── lib/        # Utilities
│   │   └── package.json
│   └── backend/            # FastAPI backend
│       ├── app/
│       │   ├── api/        # API endpoints
│       │   ├── core/       # Core functionality
│       │   ├── models/     # Database models
│       │   ├── schemas/    # Pydantic schemas
│       │   └── services/   # Business logic
│       └── requirements.txt
├── packages/
│   └── shared/             # Shared utilities
└── docker-compose.yml     # Docker configuration
```

## Features Implemented

### Authentication System ✅
- User registration and login
- JWT token-based authentication
- Role-based access control (student, trainer, admin)
- Password strength validation
- Token refresh and blacklisting
- User profile management

### Frontend Components ✅
- Responsive login/register forms
- Protected routes
- Authentication context
- User dashboard
- Profile management

### Backend API ✅
- FastAPI with async support
- SQLAlchemy ORM with PostgreSQL
- Alembic migrations
- Comprehensive error handling
- Security utilities
- Role-based permissions

## Next Steps

1. Complete the remaining tasks from the specification
2. Add more features like question banks, coding challenges
3. Implement AI-powered interview simulations
4. Add comprehensive testing
5. Deploy to production

## Support

If you encounter any issues during setup, please check:
1. All prerequisites are installed
2. Environment variables are set correctly
3. Services (PostgreSQL, Redis) are running
4. Dependencies are installed

For additional help, refer to the individual component documentation or create an issue in the project repository.