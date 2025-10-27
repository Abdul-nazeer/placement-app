"""
Coding challenge API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
import uuid

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_admin_user
from app.models.user import User
from app.services.coding import CodingService
from app.schemas.coding import (
    CodingChallenge, CodingChallengeCreate, CodingChallengeUpdate, CodingChallengeList,
    CodingChallengeFilters, CodingChallengeSearchResult, CodingChallengeAnalytics,
    CodeSubmission, CodeSubmissionCreate, CodeExecutionResult,
    UserCodingStats, CodeQualityMetrics, PlagiarismResult,
    DifficultyLevel, LanguageType, BulkChallengeCreate, BulkOperationResult
)

logger = structlog.get_logger()

router = APIRouter()


# Challenge Management Endpoints

@router.post("/challenges", response_model=CodingChallenge, status_code=status.HTTP_201_CREATED)
async def create_challenge(
    challenge_data: CodingChallengeCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new coding challenge (Admin only)."""
    try:
        service = CodingService(db)
        challenge = await service.create_challenge(challenge_data, current_user.id)
        return challenge
    except Exception as e:
        logger.error("Failed to create challenge", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create challenge"
        )


@router.get("/challenges", response_model=CodingChallengeSearchResult)
async def get_challenges(
    difficulty: Optional[List[DifficultyLevel]] = Query(None),
    category: Optional[List[str]] = Query(None),
    topic_tags: Optional[List[str]] = Query(None),
    company_tags: Optional[List[str]] = Query(None),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(True),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get coding challenges with filtering and pagination."""
    try:
        filters = CodingChallengeFilters(
            difficulty=difficulty,
            category=category,
            topic_tags=topic_tags,
            company_tags=company_tags,
            search=search,
            is_active=is_active,
            limit=limit,
            offset=offset
        )
        
        service = CodingService(db)
        challenges, total = await service.get_challenges(filters, current_user.id)
        
        # Convert to list format for response
        challenge_list = [
            CodingChallengeList(
                id=c.id,
                title=c.title,
                difficulty=c.difficulty,
                category=c.category,
                topic_tags=c.topic_tags,
                company_tags=c.company_tags,
                created_at=c.created_at,
                is_active=c.is_active
            ) for c in challenges
        ]
        
        return CodingChallengeSearchResult(
            challenges=challenge_list,
            total=total,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        logger.error("Failed to get challenges", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve challenges"
        )


@router.get("/challenges/{challenge_id}", response_model=CodingChallenge)
async def get_challenge(
    challenge_id: uuid.UUID = Path(..., description="Challenge ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific coding challenge by ID."""
    try:
        service = CodingService(db)
        challenge = await service.get_challenge(challenge_id)
        
        if not challenge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Challenge not found"
            )
        
        return challenge
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get challenge", challenge_id=challenge_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve challenge"
        )


@router.put("/challenges/{challenge_id}", response_model=CodingChallenge)
async def update_challenge(
    challenge_id: uuid.UUID,
    update_data: CodingChallengeUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a coding challenge (Admin only)."""
    try:
        service = CodingService(db)
        challenge = await service.update_challenge(challenge_id, update_data)
        
        if not challenge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Challenge not found"
            )
        
        return challenge
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update challenge", challenge_id=challenge_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update challenge"
        )


@router.delete("/challenges/{challenge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_challenge(
    challenge_id: uuid.UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a coding challenge (Admin only)."""
    try:
        service = CodingService(db)
        success = await service.delete_challenge(challenge_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Challenge not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete challenge", challenge_id=challenge_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete challenge"
        )


# Code Submission Endpoints

@router.post("/submissions", response_model=CodeSubmission, status_code=status.HTTP_201_CREATED)
async def submit_code(
    submission_data: CodeSubmissionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit code for a challenge."""
    try:
        service = CodingService(db)
        
        # Verify challenge exists
        challenge = await service.get_challenge(submission_data.challenge_id)
        if not challenge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Challenge not found"
            )
        
        if not challenge.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Challenge is not active"
            )
        
        submission = await service.submit_code(submission_data, current_user.id)
        return submission
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to submit code", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit code"
        )


@router.get("/submissions/{submission_id}", response_model=CodeSubmission)
async def get_submission(
    submission_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific code submission."""
    try:
        service = CodingService(db)
        submission = await service.get_submission(submission_id)
        
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )
        
        # Users can only view their own submissions (unless admin)
        if submission.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return submission
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get submission", submission_id=submission_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve submission"
        )


@router.get("/submissions", response_model=List[CodeSubmission])
async def get_user_submissions(
    challenge_id: Optional[uuid.UUID] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's code submissions."""
    try:
        service = CodingService(db)
        submissions, total = await service.get_user_submissions(
            current_user.id, challenge_id, limit, offset
        )
        return submissions
    except Exception as e:
        logger.error("Failed to get user submissions", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve submissions"
        )


# Analytics Endpoints

@router.get("/challenges/{challenge_id}/analytics", response_model=CodingChallengeAnalytics)
async def get_challenge_analytics(
    challenge_id: uuid.UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics for a specific challenge (Admin only)."""
    try:
        service = CodingService(db)
        analytics = await service.get_challenge_analytics(challenge_id)
        
        if not analytics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Challenge not found"
            )
        
        return analytics
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get challenge analytics", challenge_id=challenge_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics"
        )


@router.get("/users/{user_id}/stats", response_model=UserCodingStats)
async def get_user_coding_stats(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get coding statistics for a user."""
    try:
        # Users can only view their own stats (unless admin)
        if user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        service = CodingService(db)
        stats = await service.get_user_coding_stats(user_id)
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get user stats", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user statistics"
        )


@router.get("/users/me/stats", response_model=UserCodingStats)
async def get_my_coding_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's coding statistics."""
    try:
        service = CodingService(db)
        stats = await service.get_user_coding_stats(current_user.id)
        return stats
    except Exception as e:
        logger.error("Failed to get user stats", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics"
        )


# Code Quality and Analysis Endpoints

@router.get("/submissions/{submission_id}/quality", response_model=CodeQualityMetrics)
async def analyze_code_quality(
    submission_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Analyze code quality metrics for a submission."""
    try:
        service = CodingService(db)
        
        # Verify submission exists and user has access
        submission = await service.get_submission(submission_id)
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )
        
        if submission.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        quality_metrics = await service.analyze_code_quality(submission_id)
        if not quality_metrics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quality analysis not available"
            )
        
        return quality_metrics
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to analyze code quality", submission_id=submission_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze code quality"
        )


@router.get("/submissions/{submission_id}/plagiarism", response_model=PlagiarismResult)
async def detect_plagiarism(
    submission_id: uuid.UUID,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Detect potential plagiarism for a submission (Admin only)."""
    try:
        service = CodingService(db)
        
        plagiarism_result = await service.detect_plagiarism(submission_id)
        if not plagiarism_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )
        
        return plagiarism_result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to detect plagiarism", submission_id=submission_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze plagiarism"
        )


# Bulk Operations

@router.post("/challenges/bulk", response_model=BulkOperationResult)
async def bulk_create_challenges(
    bulk_data: BulkChallengeCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Bulk create coding challenges (Admin only)."""
    try:
        service = CodingService(db)
        success_count = 0
        error_count = 0
        errors = []
        created_ids = []
        
        for i, challenge_data in enumerate(bulk_data.challenges):
            try:
                challenge = await service.create_challenge(challenge_data, current_user.id)
                success_count += 1
                created_ids.append(challenge.id)
            except Exception as e:
                error_count += 1
                errors.append({
                    "index": i,
                    "title": challenge_data.title,
                    "error": str(e)
                })
        
        return BulkOperationResult(
            success_count=success_count,
            error_count=error_count,
            errors=errors,
            created_ids=created_ids
        )
    except Exception as e:
        logger.error("Failed to bulk create challenges", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to bulk create challenges"
        )


# Utility Endpoints

@router.get("/categories", response_model=List[str])
async def get_challenge_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all available challenge categories."""
    try:
        # This would typically come from a database query
        # For now, return common categories
        categories = [
            "Array", "String", "Linked List", "Tree", "Graph", "Dynamic Programming",
            "Sorting", "Searching", "Hash Table", "Stack", "Queue", "Heap",
            "Greedy", "Backtracking", "Bit Manipulation", "Math", "Two Pointers",
            "Sliding Window", "Binary Search", "Recursion"
        ]
        return categories
    except Exception as e:
        logger.error("Failed to get categories", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve categories"
        )


@router.get("/languages", response_model=List[str])
async def get_supported_languages(
    current_user: User = Depends(get_current_user)
):
    """Get all supported programming languages."""
    return [lang.value for lang in LanguageType]


@router.get("/difficulties", response_model=List[str])
async def get_difficulty_levels(
    current_user: User = Depends(get_current_user)
):
    """Get all difficulty levels."""
    return [diff.value for diff in DifficultyLevel]