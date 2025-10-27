# PlacementPrep

AI-powered placement preparation platform built with React+Vite frontend, FastAPI backend, and advanced AI capabilities through Groq API with Llama 70B model.

## Features

- **Aptitude Tests**: Company-specific and topic-based practice questions
- **Communication Coaching**: Speech recording and AI-powered feedback
- **Technical Coding**: Multi-language code editor with automated testing
- **Resume Analysis**: ATS compatibility scoring and improvement suggestions
- **Mock Interviews**: End-to-end interview simulation with AI assistance
- **AI Chatbot**: Intelligent assistance powered by Llama 70B
- **Leaderboards**: Performance tracking and peer comparison
- **Admin Dashboard**: Content management and analytics

## Architecture

- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI + Python 3.11+ + SQLAlchemy + PostgreSQL
- **Cache**: Redis for session management and caching
- **Queue**: Celery for background task processing
- **AI**: Groq API with Llama 70B model integration
- **Infrastructure**: Docker + Kubernetes ready

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 15+
- Redis 7+

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd placement-prep
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   cp apps/backend/.env.example apps/backend/.env
   cp apps/frontend/.env.example apps/frontend/.env
   ```
   
   Update the `.env` files with your configuration values.

4. **Start development environment with Docker**
   ```bash
   npm run docker:dev
   ```

5. **Or run services individually**
   ```bash
   # Start databases
   docker-compose -f docker-compose.dev.yml up postgres redis -d
   
   # Start backend
   cd apps/backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   
   # Start frontend (in another terminal)
   cd apps/frontend
   npm install
   npm run dev
   ```

### Production Deployment

1. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Update with production values
   ```

2. **Deploy with Docker Compose**
   ```bash
   npm run docker:prod
   ```

## Project Structure

```
placement-prep/
├── apps/
│   ├── frontend/          # React+Vite frontend application
│   │   ├── src/
│   │   ├── public/
│   │   ├── package.json
│   │   └── vite.config.ts
│   └── backend/           # FastAPI backend application
│       ├── app/
│       │   ├── api/       # API routes
│       │   ├── core/      # Core configuration
│       │   ├── models/    # Database models
│       │   └── services/  # Business logic
│       ├── main.py
│       └── requirements.txt
├── packages/
│   └── shared/            # Shared TypeScript types and utilities
│       ├── src/
│       └── package.json
├── nginx/                 # Nginx configuration
├── scripts/               # Database and deployment scripts
├── docker-compose.dev.yml # Development environment
├── docker-compose.prod.yml # Production environment
└── package.json           # Monorepo configuration
```

## API Documentation

When running in development mode, API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

### Backend (.env)
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: JWT signing secret
- `GROQ_API_KEY`: Groq API key for AI features

### Frontend (.env)
- `VITE_API_URL`: Backend API URL

## Development

### Running Tests
```bash
# Frontend tests
cd apps/frontend
npm test

# Backend tests
cd apps/backend
pytest
```

### Code Quality
```bash
# Frontend linting
cd apps/frontend
npm run lint

# Backend formatting
cd apps/backend
black .
isort .
mypy .
```

### Database Migrations
```bash
cd apps/backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.