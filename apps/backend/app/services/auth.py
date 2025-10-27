from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException, status
import uuid

from app.models.user import User, UserProfile, TokenBlacklist, UserRole
from app.schemas.auth import UserRegistration, UserLogin, UserResponse, TokenResponse
from app.core.security import SecurityUtils, hash_password, verify_password, create_access_token, create_refresh_token
from app.core.config import settings


class AuthService:
    """Authentication service for user management and JWT tokens"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def register_user(self, user_data: UserRegistration) -> UserResponse:
        """Register a new user with validation"""
        
        # Validate email format
        email_validation = SecurityUtils.validate_email_format(user_data.email)
        if not email_validation["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "INVALID_EMAIL",
                    "message": "Invalid email format",
                    "details": email_validation["errors"]
                }
            )
        
        # Validate password strength
        password_validation = SecurityUtils.validate_password_strength(user_data.password)
        if not password_validation["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "WEAK_PASSWORD",
                    "message": "Password does not meet security requirements",
                    "details": password_validation["errors"]
                }
            )
        
        # Check if user already exists
        existing_user = await self.db.execute(
            select(User).where(User.email == email_validation["normalized_email"])
        )
        if existing_user.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "USER_EXISTS",
                    "message": "User with this email already exists"
                }
            )
        
        # Create new user
        hashed_password = hash_password(user_data.password)
        new_user = User(
            email=email_validation["normalized_email"],
            name=user_data.name.strip(),
            password_hash=hashed_password,
            role=user_data.role.value,
            is_active=True
        )
        
        self.db.add(new_user)
        await self.db.flush()  # Get the user ID
        
        # Create user profile
        user_profile = UserProfile(
            user_id=new_user.id,
            target_companies=[],
            preferred_roles=[],
            skill_levels={}
        )
        
        self.db.add(user_profile)
        await self.db.commit()
        await self.db.refresh(new_user)
        await self.db.refresh(user_profile)
        
        # Set the profile relationship
        new_user.profile = user_profile
        
        return UserResponse.model_validate(new_user)
    
    async def authenticate_user(self, credentials: UserLogin) -> TokenResponse:
        """Authenticate user and return JWT tokens"""
        
        # Find user by email
        result = await self.db.execute(
            select(User).where(
                and_(
                    User.email == credentials.email.lower(),
                    User.is_active == True
                )
            )
        )
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "INVALID_CREDENTIALS",
                    "message": "Invalid email or password"
                }
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        await self.db.commit()
        
        # Generate tokens
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        # Load user profile
        await self.db.refresh(user)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user)
        )
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token"""
        
        # Validate refresh token
        token_data = SecurityUtils.decode_jwt_token(refresh_token)
        if not token_data["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "INVALID_TOKEN",
                    "message": token_data["error"]
                }
            )
        
        payload = token_data["payload"]
        
        # Check if token is refresh type
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "INVALID_TOKEN_TYPE",
                    "message": "Token is not a refresh token"
                }
            )
        
        # Check if token is blacklisted
        token_jti = payload.get("jti")
        if await self.is_token_blacklisted(token_jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "TOKEN_BLACKLISTED",
                    "message": "Token has been revoked"
                }
            )
        
        # Get user
        user_id = payload.get("sub")
        result = await self.db.execute(
            select(User).where(
                and_(
                    User.id == uuid.UUID(user_id),
                    User.is_active == True
                )
            )
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "USER_NOT_FOUND",
                    "message": "User not found or inactive"
                }
            )
        
        # Generate new tokens
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role
        }
        
        new_access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token({"sub": str(user.id)})
        
        # Blacklist old refresh token
        await self.blacklist_token(token_jti, user.id, payload.get("exp"))
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user)
        )
    
    async def logout_user(self, access_token: str, refresh_token: Optional[str] = None) -> bool:
        """Logout user by blacklisting tokens"""
        
        tokens_to_blacklist = []
        
        # Process access token
        access_token_data = SecurityUtils.decode_jwt_token(access_token)
        if access_token_data["is_valid"]:
            payload = access_token_data["payload"]
            user_id = uuid.UUID(payload.get("sub"))
            tokens_to_blacklist.append((payload.get("jti"), user_id, payload.get("exp")))
        
        # Process refresh token if provided
        if refresh_token:
            refresh_token_data = SecurityUtils.decode_jwt_token(refresh_token)
            if refresh_token_data["is_valid"]:
                payload = refresh_token_data["payload"]
                user_id = uuid.UUID(payload.get("sub"))
                tokens_to_blacklist.append((payload.get("jti"), user_id, payload.get("exp")))
        
        # Blacklist tokens
        for jti, user_id, exp in tokens_to_blacklist:
            if jti:
                await self.blacklist_token(jti, user_id, exp)
        
        return True
    
    async def blacklist_token(self, jti: str, user_id: uuid.UUID, expires_at: int) -> None:
        """Add token to blacklist"""
        
        blacklisted_token = TokenBlacklist(
            token_jti=jti,
            user_id=user_id,
            expires_at=datetime.fromtimestamp(expires_at)
        )
        
        self.db.add(blacklisted_token)
        await self.db.commit()
    
    async def is_token_blacklisted(self, jti: str) -> bool:
        """Check if token is blacklisted"""
        
        if not jti:
            return False
        
        result = await self.db.execute(
            select(TokenBlacklist).where(
                and_(
                    TokenBlacklist.token_jti == jti,
                    TokenBlacklist.expires_at > datetime.utcnow()
                )
            )
        )
        
        return result.scalar_one_or_none() is not None
    
    async def get_current_user(self, token: str) -> User:
        """Get current user from JWT token"""
        
        # Decode token
        token_data = SecurityUtils.decode_jwt_token(token)
        if not token_data["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "INVALID_TOKEN",
                    "message": token_data["error"]
                }
            )
        
        payload = token_data["payload"]
        
        # Check if token is access type
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "INVALID_TOKEN_TYPE",
                    "message": "Token is not an access token"
                }
            )
        
        # Check if token is blacklisted
        token_jti = payload.get("jti")
        if await self.is_token_blacklisted(token_jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "TOKEN_BLACKLISTED",
                    "message": "Token has been revoked"
                }
            )
        
        # Get user
        user_id = payload.get("sub")
        result = await self.db.execute(
            select(User).where(
                and_(
                    User.id == uuid.UUID(user_id),
                    User.is_active == True
                )
            )
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "USER_NOT_FOUND",
                    "message": "User not found or inactive"
                }
            )
        
        return user
    
    async def cleanup_expired_tokens(self) -> int:
        """Clean up expired blacklisted tokens"""
        
        from sqlalchemy import delete
        
        result = await self.db.execute(
            delete(TokenBlacklist).where(
                TokenBlacklist.expires_at <= datetime.utcnow()
            )
        )
        
        await self.db.commit()
        return result.rowcount