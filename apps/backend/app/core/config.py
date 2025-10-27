from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "PlacementPrep API"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://frontend:3000"
    ]
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/placement_prep"
    DATABASE_URL_SYNC: str = "postgresql://postgres:password@localhost:5432/placement_prep"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # External APIs
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-70b-8192"
    
    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # Code Execution
    CODE_EXECUTION_TIMEOUT: int = 30
    CODE_EXECUTION_MEMORY_LIMIT: str = "128m"
    
    # ML Models
    WHISPER_MODEL: str = "base"
    SPACY_MODEL: str = "en_core_web_sm"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()