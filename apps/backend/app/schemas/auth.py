from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from app.models.user import UserRole


class UserRegistration(BaseModel):
    """User registration request schema"""
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = UserRole.STUDENT
    
    class Config:
        json_encoders = {
            UserRole: lambda v: v.value
        }


class UserLogin(BaseModel):
    """User login request schema"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: "UserResponse"


class TokenRefresh(BaseModel):
    """Token refresh request schema"""
    refresh_token: str


class UserResponse(BaseModel):
    """User response schema"""
    id: uuid.UUID
    email: str
    name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    profile: Optional["UserProfileResponse"] = None
    
    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    """User profile response schema"""
    id: uuid.UUID
    college: Optional[str] = None
    graduation_year: Optional[int] = None
    target_companies: list = []
    preferred_roles: list = []
    skill_levels: dict = {}
    bio: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    resume_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """User profile update request schema"""
    college: Optional[str] = Field(None, max_length=255)
    graduation_year: Optional[int] = Field(None, ge=1950, le=2030)
    target_companies: Optional[list] = None
    preferred_roles: Optional[list] = None
    skill_levels: Optional[dict] = None
    bio: Optional[str] = Field(None, max_length=1000)
    phone: Optional[str] = Field(None, max_length=20)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    github_url: Optional[str] = Field(None, max_length=500)
    
    @validator('skill_levels')
    def validate_skill_levels(cls, v):
        if v is not None:
            for skill, level in v.items():
                if not isinstance(level, int) or not (1 <= level <= 10):
                    raise ValueError(f"Skill level for {skill} must be an integer between 1 and 10")
        return v


class PasswordChange(BaseModel):
    """Password change request schema"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class PasswordReset(BaseModel):
    """Password reset request schema"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class LogoutRequest(BaseModel):
    """Logout request schema"""
    refresh_token: Optional[str] = None


class ValidationError(BaseModel):
    """Validation error response schema"""
    field: str
    message: str


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime


# Update forward references
TokenResponse.model_rebuild()
UserResponse.model_rebuild()