from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any
import structlog
import uuid

from app.core.database import get_db
from app.core.deps import get_current_active_user, get_current_admin
from app.schemas.auth import UserResponse, UserProfileUpdate, UserProfileResponse
from app.models.user import User, UserProfile
from app.services.auth import AuthService

logger = structlog.get_logger()

router = APIRouter()


@router.get(
    "/profile",
    response_model=UserProfileResponse,
    summary="Get user profile",
    description="Get current user's profile information"
)
async def get_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> UserProfileResponse:
    """Get current user's profile"""
    
    try:
        # Load user profile if not already loaded
        if not current_user.profile:
            result = await db.execute(
                select(UserProfile).where(UserProfile.user_id == current_user.id)
            )
            profile = result.scalar_one_or_none()
            
            if not profile:
                # Create default profile if it doesn't exist
                profile = UserProfile(
                    user_id=current_user.id,
                    target_companies=[],
                    preferred_roles=[],
                    skill_levels={}
                )
                db.add(profile)
                await db.commit()
                await db.refresh(profile)
        else:
            profile = current_user.profile
        
        logger.info(
            "User profile retrieved",
            user_id=str(current_user.id)
        )
        
        return UserProfileResponse.model_validate(profile)
        
    except Exception as e:
        logger.error(
            "Failed to get user profile",
            error=str(e),
            user_id=str(current_user.id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "PROFILE_FETCH_FAILED",
                "message": "Failed to retrieve user profile"
            }
        )


@router.put(
    "/profile",
    response_model=UserProfileResponse,
    summary="Update user profile",
    description="Update current user's profile information"
)
async def update_user_profile(
    profile_data: UserProfileUpdate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> UserProfileResponse:
    """Update current user's profile"""
    
    try:
        logger.info(
            "User profile update attempt",
            user_id=str(current_user.id),
            client_ip=request.client.host
        )
        
        # Get or create user profile
        result = await db.execute(
            select(UserProfile).where(UserProfile.user_id == current_user.id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            profile = UserProfile(
                user_id=current_user.id,
                target_companies=[],
                preferred_roles=[],
                skill_levels={}
            )
            db.add(profile)
        
        # Update profile fields
        update_data = profile_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)
        
        await db.commit()
        await db.refresh(profile)
        
        logger.info(
            "User profile updated successfully",
            user_id=str(current_user.id)
        )
        
        return UserProfileResponse.model_validate(profile)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to update user profile",
            error=str(e),
            user_id=str(current_user.id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "PROFILE_UPDATE_FAILED",
                "message": "Failed to update user profile"
            }
        )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Get user information by ID (admin only)"
)
async def get_user_by_id(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Get user by ID (admin only)"""
    
    try:
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "USER_NOT_FOUND",
                    "message": "User not found"
                }
            )
        
        logger.info(
            "User retrieved by admin",
            admin_id=str(current_user.id),
            target_user_id=str(user_id)
        )
        
        return UserResponse.model_validate(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get user by ID",
            error=str(e),
            user_id=str(user_id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "USER_FETCH_FAILED",
                "message": "Failed to retrieve user"
            }
        )


@router.patch(
    "/{user_id}/status",
    summary="Update user status",
    description="Activate or deactivate user account (admin only)"
)
async def update_user_status(
    user_id: uuid.UUID,
    is_active: bool,
    request: Request,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Update user active status (admin only)"""
    
    try:
        logger.info(
            "User status update attempt",
            admin_id=str(current_user.id),
            target_user_id=str(user_id),
            new_status=is_active,
            client_ip=request.client.host
        )
        
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "USER_NOT_FOUND",
                    "message": "User not found"
                }
            )
        
        # Prevent admin from deactivating themselves
        if user.id == current_user.id and not is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "CANNOT_DEACTIVATE_SELF",
                    "message": "Cannot deactivate your own account"
                }
            )
        
        user.is_active = is_active
        await db.commit()
        
        logger.info(
            "User status updated successfully",
            admin_id=str(current_user.id),
            target_user_id=str(user_id),
            new_status=is_active
        )
        
        return {
            "message": f"User {'activated' if is_active else 'deactivated'} successfully",
            "user_id": str(user_id),
            "is_active": is_active
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to update user status",
            error=str(e),
            user_id=str(user_id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "STATUS_UPDATE_FAILED",
                "message": "Failed to update user status"
            }
        )