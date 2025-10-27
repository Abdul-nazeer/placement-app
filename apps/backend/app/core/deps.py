from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.auth import AuthService
from app.services.content import ContentService
from app.models.user import User, UserRole


# Security scheme for JWT tokens
security = HTTPBearer()


async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Get authentication service instance"""
    return AuthService(db)


async def get_content_service(db: AsyncSession = Depends(get_db)) -> ContentService:
    """Get content service instance"""
    return ContentService(db)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """Get current authenticated user"""
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "MISSING_TOKEN",
                "message": "Authentication token is required"
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return await auth_service.get_current_user(credentials.credentials)


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "INACTIVE_USER",
                "message": "User account is inactive"
            }
        )
    
    return current_user


def require_role(required_role: UserRole):
    """Dependency factory for role-based access control"""
    
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role != required_role.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "INSUFFICIENT_PERMISSIONS",
                    "message": f"This endpoint requires {required_role.value} role"
                }
            )
        return current_user
    
    return role_checker


def require_roles(*required_roles: UserRole):
    """Dependency factory for multiple role access control"""
    
    async def roles_checker(current_user: User = Depends(get_current_active_user)) -> User:
        allowed_roles = [role.value for role in required_roles]
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "INSUFFICIENT_PERMISSIONS",
                    "message": f"This endpoint requires one of these roles: {', '.join(allowed_roles)}"
                }
            )
        return current_user
    
    return roles_checker


# Convenience dependencies for common roles
get_current_student = require_role(UserRole.STUDENT)
get_current_trainer = require_role(UserRole.TRAINER)
get_current_admin = require_role(UserRole.ADMIN)
get_trainer_or_admin = require_roles(UserRole.TRAINER, UserRole.ADMIN)


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[User]:
    """Get current user if token is provided, otherwise return None"""
    
    if not credentials:
        return None
    
    try:
        return await auth_service.get_current_user(credentials.credentials)
    except HTTPException:
        return None