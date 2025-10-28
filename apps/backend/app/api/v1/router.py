from fastapi import APIRouter

# Import route modules
from app.api.v1.endpoints import auth, users, content, aptitude, coding, communication, resume, interview
# from app.api.v1.endpoints import sessions, chat  # Will be added in subsequent tasks

api_router = APIRouter()

# Health check for API
@api_router.get("/health")
async def api_health():
    """API health check"""
    return {
        "status": "healthy",
        "api_version": "v1",
        "message": "PlacementPrep API is running"
    }

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(aptitude.router, prefix="/aptitude", tags=["aptitude"])
api_router.include_router(coding.router, prefix="/coding", tags=["coding"])
api_router.include_router(communication.router, prefix="/communication", tags=["communication"])
api_router.include_router(resume.router, prefix="/resume", tags=["resume"])
api_router.include_router(interview.router, prefix="/interview", tags=["interview"])

# Will be added in subsequent tasks
# api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
# api_router.include_router(chat.router, prefix="/chat", tags=["chat"])