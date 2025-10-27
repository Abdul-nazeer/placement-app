"""
Aptitude Test API Endpoints

This module provides REST API endpoints for aptitude testing functionality including:
- Test session creation and management
- Answer submission with validation and scoring
- Real-time progress tracking and session state management
- Detailed result analysis and feedback generation
- Test history and performance analytics
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.models.session import TestSession, SessionStatus
from app.models.question import Question
from app.services.aptitude_engine import AptitudeTestEngine, TestConfiguration, AdaptiveAlgorithm
from app.schemas.content import (
    TestSession as TestSessionSchema,
    TestSessionCreate,
    TestSessionUpdate,
    SubmissionCreate,
    Submission as SubmissionSchema,
    Question as QuestionSchema
)

router = APIRouter()


# Pydantic models for API requests/responses
from pydantic import BaseModel, Field


class AptitudeTestConfigRequest(BaseModel):
    """Request model for creating aptitude test configuration"""
    total_questions: int = Field(default=20, ge=5, le=100)
    time_limit: Optional[int] = Field(None, gt=0, description="Total time limit in seconds")
    time_per_question: Optional[int] = Field(None, gt=0, description="Time per question in seconds")
    categories: Optional[List[str]] = Field(default=None, description="Question categories to include")
    difficulty_levels: Optional[List[int]] = Field(default=None, description="Difficulty levels (1-5)")
    company_tags: Optional[List[str]] = Field(default=None, description="Company tags to filter by")
    topic_tags: Optional[List[str]] = Field(default=None, description="Topic tags to filter by")
    adaptive_algorithm: AdaptiveAlgorithm = Field(default=AdaptiveAlgorithm.BALANCED)
    randomize_questions: bool = Field(default=True)
    randomize_options: bool = Field(default=True)
    allow_review: bool = Field(default=True)
    show_results: bool = Field(default=True)
    passing_score: float = Field(default=60.0, ge=0, le=100)
    negative_marking: bool = Field(default=False)
    negative_marking_ratio: float = Field(default=0.25, ge=0, le=1)
    difficulty_distribution: Optional[Dict[int, float]] = Field(default=None)
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = Field(None, max_length=1000)


class AnswerSubmissionRequest(BaseModel):
    """Request model for submitting an answer"""
    question_id: UUID
    user_answer: str = Field(..., min_length=1)
    time_taken: int = Field(..., gt=0, description="Time taken in seconds")


class SessionProgressResponse(BaseModel):
    """Response model for session progress"""
    session_id: UUID
    status: str
    current_question: int
    total_questions: int
    progress_percentage: float
    correct_answers: int
    incorrect_answers: int
    skipped_answers: int
    current_score: float
    accuracy_percentage: float
    time_remaining: Optional[int]
    time_limit: Optional[int]
    start_time: Optional[datetime]
    submissions_count: int
    can_pause: bool
    can_resume: bool
    allow_review: bool


class SessionResultsResponse(BaseModel):
    """Response model for session results"""
    session_id: UUID
    title: str
    test_type: str
    total_questions: int
    correct_answers: int
    incorrect_answers: int
    skipped_answers: int
    final_score: float
    max_score: float
    percentage: Optional[float]
    accuracy_percentage: float
    total_time_taken: Optional[int]
    average_time_per_question: Optional[float]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    passed: bool
    category_performance: Dict[str, Any]
    difficulty_performance: Dict[str, Any]
    time_analysis: Dict[str, Any]
    detailed_submissions: List[Dict[str, Any]]


@router.post("/sessions", response_model=TestSessionSchema)
async def create_aptitude_test_session(
    config_request: AptitudeTestConfigRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new aptitude test session with specified configuration.
    
    This endpoint creates a test session with adaptive question selection
    based on the provided configuration parameters.
    """
    try:
        # Create test configuration
        config = TestConfiguration(
            total_questions=config_request.total_questions,
            time_limit=config_request.time_limit,
            time_per_question=config_request.time_per_question,
            categories=config_request.categories,
            difficulty_levels=config_request.difficulty_levels,
            company_tags=config_request.company_tags,
            topic_tags=config_request.topic_tags,
            adaptive_algorithm=config_request.adaptive_algorithm,
            randomize_questions=config_request.randomize_questions,
            randomize_options=config_request.randomize_options,
            allow_review=config_request.allow_review,
            show_results=config_request.show_results,
            passing_score=config_request.passing_score,
            negative_marking=config_request.negative_marking,
            negative_marking_ratio=config_request.negative_marking_ratio,
            difficulty_distribution=config_request.difficulty_distribution
        )
        
        # Create test engine and session
        engine = AptitudeTestEngine(db)
        session = await engine.create_test_session(
            user_id=current_user.id,
            config=config,
            title=config_request.title,
            description=config_request.description
        )
        
        return session
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create test session"
        )


@router.post("/sessions/{session_id}/start", response_model=TestSessionSchema)
async def start_aptitude_test_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start an aptitude test session.
    
    This endpoint starts the timer and activates the test session.
    """
    try:
        engine = AptitudeTestEngine(db)
        session = await engine.start_session(session_id, current_user.id)
        return session
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start test session"
        )


@router.get("/sessions/{session_id}/current-question", response_model=Optional[QuestionSchema])
async def get_current_question(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the current question for an active test session.
    
    Returns the next question to be answered or None if session is complete.
    """
    try:
        engine = AptitudeTestEngine(db)
        question = await engine.get_current_question(session_id, current_user.id)
        return question
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get current question"
        )


@router.post("/sessions/{session_id}/submit", response_model=Dict[str, Any])
async def submit_answer(
    session_id: UUID,
    submission: AnswerSubmissionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit an answer for the current question in a test session.
    
    This endpoint processes the answer, calculates the score, and updates
    the session progress. Returns submission details and completion status.
    """
    try:
        engine = AptitudeTestEngine(db)
        submission_result, is_complete = await engine.submit_answer(
            session_id=session_id,
            user_id=current_user.id,
            question_id=submission.question_id,
            user_answer=submission.user_answer,
            time_taken=submission.time_taken
        )
        
        return {
            "submission_id": submission_result.id,
            "is_correct": submission_result.is_correct,
            "score": float(submission_result.score) if submission_result.score else 0.0,
            "max_score": float(submission_result.max_score) if submission_result.max_score else 0.0,
            "is_session_complete": is_complete,
            "feedback": submission_result.feedback,
            "time_taken": submission_result.time_taken
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit answer"
        )


@router.post("/sessions/{session_id}/pause", response_model=TestSessionSchema)
async def pause_test_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Pause an active test session.
    
    This endpoint pauses the session timer and allows the user to resume later.
    """
    try:
        engine = AptitudeTestEngine(db)
        session = await engine.pause_session(session_id, current_user.id)
        return session
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to pause test session"
        )


@router.post("/sessions/{session_id}/resume", response_model=TestSessionSchema)
async def resume_test_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Resume a paused test session.
    
    This endpoint resumes the session timer and continues the test.
    """
    try:
        engine = AptitudeTestEngine(db)
        session = await engine.resume_session(session_id, current_user.id)
        return session
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resume test session"
        )


@router.get("/sessions/{session_id}/progress", response_model=SessionProgressResponse)
async def get_session_progress(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get real-time progress information for a test session.
    
    Returns detailed progress metrics including time remaining, score,
    and completion status.
    """
    try:
        engine = AptitudeTestEngine(db)
        progress = await engine.get_session_progress(session_id, current_user.id)
        return SessionProgressResponse(**progress)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get session progress"
        )


@router.get("/sessions/{session_id}/results", response_model=SessionResultsResponse)
async def get_session_results(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive results and analysis for a completed test session.
    
    Returns detailed performance analysis including category-wise performance,
    difficulty analysis, and time metrics.
    """
    try:
        engine = AptitudeTestEngine(db)
        results = await engine.get_session_results(session_id, current_user.id)
        return SessionResultsResponse(**results)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get session results"
        )


@router.get("/sessions", response_model=List[TestSessionSchema])
async def get_user_test_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by session status"),
    test_type: Optional[str] = Query(None, description="Filter by test type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's test session history with optional filtering.
    
    Returns paginated list of test sessions with basic information.
    """
    try:
        query = db.query(TestSession).filter(TestSession.user_id == current_user.id)
        
        if status:
            query = query.filter(TestSession.status == status)
        
        if test_type:
            query = query.filter(TestSession.test_type == test_type)
        
        sessions = query.order_by(TestSession.created_at.desc()).offset(skip).limit(limit).all()
        return sessions
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get test sessions"
        )


@router.get("/analytics/performance", response_model=Dict[str, Any])
async def get_user_performance_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's performance analytics over a specified time period.
    
    Returns comprehensive analytics including trends, strengths, and areas for improvement.
    """
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import func, and_
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get completed sessions in date range
        sessions = db.query(TestSession).filter(
            and_(
                TestSession.user_id == current_user.id,
                TestSession.status == SessionStatus.COMPLETED,
                TestSession.created_at >= start_date,
                TestSession.created_at <= end_date
            )
        ).all()
        
        if not sessions:
            return {
                "total_sessions": 0,
                "average_score": 0,
                "improvement_trend": "no_data",
                "category_performance": {},
                "difficulty_performance": {},
                "time_trends": {}
            }
        
        # Calculate analytics
        total_sessions = len(sessions)
        average_score = sum(s.percentage or 0 for s in sessions) / total_sessions
        
        # Calculate improvement trend
        if total_sessions >= 2:
            first_half = sessions[:total_sessions//2]
            second_half = sessions[total_sessions//2:]
            first_avg = sum(s.percentage or 0 for s in first_half) / len(first_half)
            second_avg = sum(s.percentage or 0 for s in second_half) / len(second_half)
            
            if second_avg > first_avg + 5:
                trend = "improving"
            elif second_avg < first_avg - 5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        # Category performance
        category_stats = {}
        for session in sessions:
            for category in session.categories or []:
                if category not in category_stats:
                    category_stats[category] = {"sessions": 0, "total_score": 0}
                category_stats[category]["sessions"] += 1
                category_stats[category]["total_score"] += session.percentage or 0
        
        for category, stats in category_stats.items():
            stats["average_score"] = stats["total_score"] / stats["sessions"]
        
        return {
            "total_sessions": total_sessions,
            "average_score": round(average_score, 2),
            "improvement_trend": trend,
            "category_performance": category_stats,
            "sessions_over_time": [
                {
                    "date": s.created_at.date().isoformat(),
                    "score": s.percentage,
                    "duration": s.total_time_taken
                }
                for s in sessions
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get performance analytics"
        )


@router.get("/available-filters", response_model=Dict[str, List[str]])
async def get_available_test_filters(
    db: Session = Depends(get_db)
):
    """
    Get available filter options for creating aptitude tests.
    
    Returns lists of available categories, companies, and topics.
    """
    try:
        from sqlalchemy import distinct
        
        # Get distinct values from questions
        categories = db.query(distinct(Question.category)).filter(
            Question.type == "aptitude",
            Question.is_active == True
        ).all()
        
        company_tags = db.query(func.unnest(Question.company_tags).label('tag')).filter(
            Question.type == "aptitude",
            Question.is_active == True
        ).distinct().all()
        
        topic_tags = db.query(func.unnest(Question.topic_tags).label('tag')).filter(
            Question.type == "aptitude",
            Question.is_active == True
        ).distinct().all()
        
        return {
            "categories": [cat[0] for cat in categories if cat[0]],
            "company_tags": [tag[0] for tag in company_tags if tag[0]],
            "topic_tags": [tag[0] for tag in topic_tags if tag[0]],
            "difficulty_levels": [1, 2, 3, 4, 5],
            "adaptive_algorithms": [algo.value for algo in AdaptiveAlgorithm]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available filters"
        )