from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import structlog

from app.core.database import get_db
from app.core.deps import get_auth_service, get_current_active_user, security
from app.services.auth import AuthService
from app.schemas.auth import (
    UserRegistration, UserLogin, TokenResponse, TokenRefresh,
    UserResponse, LogoutRequest, PasswordChange, ErrorResponse
)
from app.models.user import User

logger = structlog.get_logger()

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Register a new user account with email validation and password strength requirements"
)
async def register_user(
    user_data: UserRegistration,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
) -> UserResponse:
    """Register a new user"""
    
    try:
        logger.info(
            "User registration attempt",
            email=user_data.email,
            role=user_data.role.value,
            client_ip=request.client.host
        )
        
        user = await auth_service.register_user(user_data)
        
        logger.info(
            "User registered successfully",
            user_id=str(user.id),
            email=user.email,
            role=user.role
        )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "User registration failed",
            error=str(e),
            email=user_data.email
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "REGISTRATION_FAILED",
                "message": "Failed to register user"
            }
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate user and return JWT access and refresh tokens"
)
async def login_user(
    credentials: UserLogin,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    """Authenticate user and return tokens"""
    
    try:
        logger.info(
            "User login attempt",
            email=credentials.email,
            client_ip=request.client.host
        )
        
        token_response = await auth_service.authenticate_user(credentials)
        
        logger.info(
            "User logged in successfully",
            user_id=str(token_response.user.id),
            email=token_response.user.email,
            role=token_response.user.role
        )
        
        return token_response
        
    except HTTPException:
        logger.warning(
            "User login failed",
            email=credentials.email,
            client_ip=request.client.host
        )
        raise
    except Exception as e:
        logger.error(
            "User login error",
            error=str(e),
            email=credentials.email
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "LOGIN_FAILED",
                "message": "Failed to authenticate user"
            }
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Refresh access token using a valid refresh token"
)
async def refresh_access_token(
    token_data: TokenRefresh,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    """Refresh access token"""
    
    try:
        logger.info(
            "Token refresh attempt",
            client_ip=request.client.host
        )
        
        token_response = await auth_service.refresh_token(token_data.refresh_token)
        
        logger.info(
            "Token refreshed successfully",
            user_id=str(token_response.user.id)
        )
        
        return token_response
        
    except HTTPException:
        logger.warning(
            "Token refresh failed",
            client_ip=request.client.host
        )
        raise
    except Exception as e:
        logger.error(
            "Token refresh error",
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "REFRESH_FAILED",
                "message": "Failed to refresh token"
            }
        )


@router.post(
    "/logout",
    summary="User logout",
    description="Logout user by blacklisting access and refresh tokens"
)
async def logout_user(
    logout_data: LogoutRequest,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, str]:
    """Logout user by blacklisting tokens"""
    
    try:
        logger.info(
            "User logout attempt",
            client_ip=request.client.host
        )
        
        access_token = credentials.credentials
        refresh_token = logout_data.refresh_token
        
        await auth_service.logout_user(access_token, refresh_token)
        
        logger.info("User logged out successfully")
        
        return {
            "message": "Successfully logged out",
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "User logout error",
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "LOGOUT_FAILED",
                "message": "Failed to logout user"
            }
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get current authenticated user information"
)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> UserResponse:
    """Get current user information"""
    
    logger.info(
        "User info requested",
        user_id=str(current_user.id),
        email=current_user.email
    )
    
    return UserResponse.model_validate(current_user)


@router.post(
    "/change-password",
    summary="Change password",
    description="Change user password with current password verification"
)
async def change_password(
    password_data: PasswordChange,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, str]:
    """Change user password"""
    
    try:
        from app.core.security import verify_password, hash_password, SecurityUtils
        
        logger.info(
            "Password change attempt",
            user_id=str(current_user.id),
            client_ip=request.client.host
        )
        
        # Verify current password
        if not verify_password(password_data.current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "INVALID_PASSWORD",
                    "message": "Current password is incorrect"
                }
            )
        
        # Validate new password strength
        password_validation = SecurityUtils.validate_password_strength(password_data.new_password)
        if not password_validation["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "WEAK_PASSWORD",
                    "message": "New password does not meet security requirements",
                    "details": password_validation["errors"]
                }
            )
        
        # Update password
        current_user.password_hash = hash_password(password_data.new_password)
        await auth_service.db.commit()
        
        logger.info(
            "Password changed successfully",
            user_id=str(current_user.id)
        )
        
        return {
            "message": "Password changed successfully",
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Password change error",
            error=str(e),
            user_id=str(current_user.id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "PASSWORD_CHANGE_FAILED",
                "message": "Failed to change password"
            }
        )


@router.post(
    "/verify-token",
    summary="Verify token",
    description="Verify if the provided token is valid and not blacklisted"
)
async def verify_token(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Verify token validity"""
    
    return {
        "valid": True,
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "role": current_user.role,
            "is_active": current_user.is_active
        },
        "message": "Token is valid"
    }