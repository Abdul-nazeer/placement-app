"""Interview API endpoints."""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
import json
import asyncio

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_user_websocket
from app.models.user import User
from app.models.interview import InterviewType, InterviewStatus, DifficultyLevel
from app.schemas.interview import (
    InterviewSessionCreate, InterviewSessionResponse, InterviewSessionUpdate,
    InterviewQuestionResponse, InterviewResponseCreate, InterviewResponseResponse,
    InterviewSessionSummary, InterviewAnalytics, QuestionGenerationRequest
)
from app.services.interview_engine import InterviewEngine
from app.services.ai_interviewer import AIInterviewer
from app.services.performance_analyzer import PerformanceAnalyzer
from app.core.config import settings
import aiofiles
import os
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter()

# WebSocket connection manager for real-time interview sessions
class InterviewConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_connections: Dict[UUID, List[str]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: UUID, user_id: UUID):
        await websocket.accept()
        connection_id = f"{user_id}_{session_id}"
        self.active_connections[connection_id] = websocket
        
        if session_id not in self.session_connections:
            self.session_connections[session_id] = []
        self.session_connections[session_id].append(connection_id)
        
        logger.info(f"WebSocket connected: {connection_id}")
    
    def disconnect(self, session_id: UUID, user_id: UUID):
        connection_id = f"{user_id}_{session_id}"
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        if session_id in self.session_connections:
            if connection_id in self.session_connections[session_id]:
                self.session_connections[session_id].remove(connection_id)
            if not self.session_connections[session_id]:
                del self.session_connections[session_id]
        
        logger.info(f"WebSocket disconnected: {connection_id}")
    
    async def send_personal_message(self, message: dict, session_id: UUID, user_id: UUID):
        connection_id = f"{user_id}_{session_id}"
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to {connection_id}: {e}")
                self.disconnect(session_id, user_id)

manager = InterviewConnectionManager()


@router.post("/sessions", response_model=InterviewSessionResponse)
async def create_interview_session(
    session_data: InterviewSessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new interview session."""
    
    try:
        engine = InterviewEngine(db)
        session = await engine.create_interview_session(current_user.id, session_data)
        return session
    except Exception as e:
        logger.error(f"Error creating interview session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create interview session"
        )


@router.post("/sessions/scenario/{interview_type}", response_model=InterviewSessionResponse)
async def create_scenario_interview(
    interview_type: InterviewType,
    company_name: Optional[str] = None,
    position_title: Optional[str] = None,
    difficulty_level: DifficultyLevel = DifficultyLevel.MEDIUM,
    duration_minutes: int = 45,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a scenario-based interview session."""
    
    try:
        engine = InterviewEngine(db)
        session = await engine.create_scenario_based_interview(
            user_id=current_user.id,
            interview_type=interview_type,
            company_name=company_name,
            position_title=position_title,
            difficulty_level=difficulty_level,
            duration_minutes=duration_minutes
        )
        return session
    except Exception as e:
        logger.error(f"Error creating scenario interview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create scenario interview"
        )


@router.get("/sessions", response_model=List[InterviewSessionSummary])
async def get_user_interview_sessions(
    skip: int = 0,
    limit: int = 20,
    status_filter: Optional[InterviewStatus] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's interview sessions."""
    
    try:
        from sqlalchemy import select, and_
        from app.models.interview import InterviewSession
        
        query = select(InterviewSession).where(InterviewSession.user_id == current_user.id)
        
        if status_filter:
            query = query.where(InterviewSession.status == status_filter)
        
        query = query.order_by(InterviewSession.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        sessions = result.scalars().all()
        
        # Convert to summary format
        summaries = []
        for session in sessions:
            summary = InterviewSessionSummary(
                id=session.id,
                title=session.title,
                interview_type=session.interview_type,
                company_name=session.company_name,
                position_title=session.position_title,
                status=session.status,
                total_duration=session.total_duration,
                actual_duration=session.duration_minutes,
                question_count=session.question_count,
                questions_answered=session.current_question_index,
                overall_score=session.overall_score,
                communication_score=session.communication_score,
                technical_score=session.technical_score,
                behavioral_score=session.behavioral_score,
                created_at=session.created_at,
                start_time=session.start_time,
                end_time=session.end_time
            )
            summaries.append(summary)
        
        return summaries
        
    except Exception as e:
        logger.error(f"Error fetching interview sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch interview sessions"
        )


@router.get("/sessions/{session_id}", response_model=InterviewSessionResponse)
async def get_interview_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific interview session details."""
    
    try:
        engine = InterviewEngine(db)
        session = await engine._get_session(session_id, current_user.id, include_questions=True)
        return session
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error fetching interview session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch interview session"
        )


@router.post("/sessions/{session_id}/start", response_model=InterviewSessionResponse)
async def start_interview_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start an interview session."""
    
    try:
        engine = InterviewEngine(db)
        session = await engine.start_interview(session_id, current_user.id)
        return session
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error starting interview session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start interview session"
        )


@router.get("/sessions/{session_id}/next-question", response_model=Optional[InterviewQuestionResponse])
async def get_next_question(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the next question in the interview."""
    
    try:
        engine = InterviewEngine(db)
        question = await engine.get_next_question(session_id, current_user.id)
        return question
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting next question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get next question"
        )


@router.post("/sessions/{session_id}/questions/{question_id}/respond", response_model=InterviewResponseResponse)
async def submit_interview_response(
    session_id: UUID,
    question_id: UUID,
    response_text: Optional[str] = Form(None),
    response_duration: int = Form(...),
    thinking_time: int = Form(0),
    audio_file: Optional[UploadFile] = File(None),
    video_file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit response to an interview question."""
    
    try:
        # Save uploaded files
        audio_file_path = None
        video_file_path = None
        
        if audio_file:
            audio_file_path = await _save_uploaded_file(
                audio_file, "audio", session_id, question_id
            )
        
        if video_file:
            video_file_path = await _save_uploaded_file(
                video_file, "video", session_id, question_id
            )
        
        # Create response data
        response_data = InterviewResponseCreate(
            response_text=response_text,
            response_duration=response_duration,
            thinking_time=thinking_time
        )
        
        # Submit response
        engine = InterviewEngine(db)
        response = await engine.submit_response(
            session_id=session_id,
            question_id=question_id,
            user_id=current_user.id,
            response_data=response_data,
            audio_file_path=audio_file_path,
            video_file_path=video_file_path
        )
        
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error submitting interview response: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit interview response"
        )


@router.post("/sessions/{session_id}/pause", response_model=InterviewSessionResponse)
async def pause_interview_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Pause an active interview session."""
    
    try:
        engine = InterviewEngine(db)
        session = await engine.pause_interview(session_id, current_user.id)
        return session
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error pausing interview session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to pause interview session"
        )


@router.post("/sessions/{session_id}/resume", response_model=InterviewSessionResponse)
async def resume_interview_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Resume a paused interview session."""
    
    try:
        engine = InterviewEngine(db)
        session = await engine.resume_interview(session_id, current_user.id)
        return session
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error resuming interview session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resume interview session"
        )


@router.post("/sessions/{session_id}/complete", response_model=InterviewSessionResponse)
async def complete_interview_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Complete an interview session."""
    
    try:
        engine = InterviewEngine(db)
        session = await engine.complete_interview(session_id, current_user.id)
        return session
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error completing interview session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete interview session"
        )


@router.get("/analytics", response_model=InterviewAnalytics)
async def get_interview_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's interview analytics and performance insights."""
    
    try:
        from sqlalchemy import select, func
        from app.models.interview import InterviewSession, InterviewResponse
        
        # Get session statistics
        session_stats = await db.execute(
            select(
                func.count(InterviewSession.id).label("total"),
                func.count().filter(InterviewSession.status == InterviewStatus.COMPLETED).label("completed"),
                func.avg(InterviewSession.overall_score).label("avg_score"),
                func.avg(InterviewSession.duration_minutes).label("avg_duration")
            ).where(InterviewSession.user_id == current_user.id)
        )
        stats = session_stats.first()
        
        # Get score distribution
        score_ranges = {
            "0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0
        }
        
        completed_sessions = await db.execute(
            select(InterviewSession.overall_score)
            .where(
                InterviewSession.user_id == current_user.id,
                InterviewSession.status == InterviewStatus.COMPLETED,
                InterviewSession.overall_score.isnot(None)
            )
        )
        
        for score in completed_sessions.scalars():
            if score <= 20:
                score_ranges["0-20"] += 1
            elif score <= 40:
                score_ranges["21-40"] += 1
            elif score <= 60:
                score_ranges["41-60"] += 1
            elif score <= 80:
                score_ranges["61-80"] += 1
            else:
                score_ranges["81-100"] += 1
        
        # Basic analytics response
        analytics = InterviewAnalytics(
            total_interviews=stats.total or 0,
            completed_interviews=stats.completed or 0,
            average_score=float(stats.avg_score) if stats.avg_score else None,
            average_duration=float(stats.avg_duration) if stats.avg_duration else None,
            score_distribution=score_ranges,
            category_performance={},  # TODO: Implement category-specific performance
            improvement_trends=[],    # TODO: Implement trend analysis
            strengths=["Communication", "Technical Knowledge"],  # TODO: Extract from AI feedback
            areas_for_improvement=["Time Management", "Confidence"],  # TODO: Extract from AI feedback
            recommendations=[
                "Practice more behavioral questions using the STAR method",
                "Work on speaking pace and reducing filler words",
                "Focus on providing specific examples in responses"
            ]
        )
        
        return analytics
        
    except Exception as e:
        logger.error(f"Error generating interview analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate interview analytics"
        )


@router.websocket("/sessions/{session_id}/realtime")
async def websocket_interview_session(
    websocket: WebSocket,
    session_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Real-time WebSocket connection for AI interviewer interaction."""
    
    try:
        # Get user from WebSocket (implement token validation)
        user = await get_current_user_websocket(websocket, db)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Connect to session
        await manager.connect(websocket, session_id, user.id)
        
        # Initialize AI interviewer
        ai_interviewer = AIInterviewer(db)
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                message_type = message.get("type")
                
                if message_type == "start_interview":
                    # Start the interview session
                    engine = InterviewEngine(db)
                    session = await engine.start_interview(session_id, user.id)
                    
                    # Get first question
                    question = await engine.get_next_question(session_id, user.id)
                    
                    if question:
                        # Generate AI interviewer introduction
                        intro = await ai_interviewer.generate_introduction(session, question)
                        
                        response = {
                            "type": "interview_started",
                            "session": {
                                "id": str(session.id),
                                "status": session.status,
                                "current_question_index": session.current_question_index
                            },
                            "ai_introduction": intro,
                            "question": {
                                "id": str(question.id),
                                "text": question.question_text,
                                "category": question.category,
                                "expected_duration": question.expected_duration,
                                "context": question.context_information
                            }
                        }
                        
                        await manager.send_personal_message(response, session_id, user.id)
                
                elif message_type == "submit_response":
                    # Handle response submission
                    question_id = UUID(message.get("question_id"))
                    response_text = message.get("response_text", "")
                    response_duration = message.get("response_duration", 0)
                    thinking_time = message.get("thinking_time", 0)
                    
                    # Submit response
                    engine = InterviewEngine(db)
                    response_data = InterviewResponseCreate(
                        response_text=response_text,
                        response_duration=response_duration,
                        thinking_time=thinking_time
                    )
                    
                    interview_response = await engine.submit_response(
                        session_id=session_id,
                        question_id=question_id,
                        user_id=user.id,
                        response_data=response_data
                    )
                    
                    # Generate AI feedback
                    ai_feedback = await ai_interviewer.generate_immediate_feedback(
                        interview_response, session_id
                    )
                    
                    # Get next question
                    next_question = await engine.get_next_question(session_id, user.id)
                    
                    response_msg = {
                        "type": "response_processed",
                        "response_id": str(interview_response.id),
                        "ai_feedback": ai_feedback,
                        "scores": {
                            "overall": interview_response.overall_score,
                            "communication": interview_response.communication_score,
                            "content": interview_response.content_score
                        }
                    }
                    
                    if next_question:
                        # Generate AI transition to next question
                        transition = await ai_interviewer.generate_question_transition(
                            interview_response, next_question
                        )
                        
                        response_msg.update({
                            "next_question": {
                                "id": str(next_question.id),
                                "text": next_question.question_text,
                                "category": next_question.category,
                                "expected_duration": next_question.expected_duration,
                                "context": next_question.context_information
                            },
                            "ai_transition": transition
                        })
                    else:
                        # Interview completed
                        session = await engine.complete_interview(session_id, user.id)
                        completion_summary = await ai_interviewer.generate_completion_summary(session)
                        
                        response_msg.update({
                            "interview_completed": True,
                            "final_scores": {
                                "overall": session.overall_score,
                                "communication": session.communication_score,
                                "technical": session.technical_score,
                                "behavioral": session.behavioral_score
                            },
                            "ai_summary": completion_summary
                        })
                    
                    await manager.send_personal_message(response_msg, session_id, user.id)
                
                elif message_type == "request_hint":
                    # Provide AI-generated hint for current question
                    question_id = UUID(message.get("question_id"))
                    
                    hint = await ai_interviewer.generate_hint(question_id, session_id)
                    
                    response_msg = {
                        "type": "hint_provided",
                        "question_id": str(question_id),
                        "hint": hint
                    }
                    
                    await manager.send_personal_message(response_msg, session_id, user.id)
                
                elif message_type == "pause_interview":
                    # Pause the interview
                    engine = InterviewEngine(db)
                    session = await engine.pause_interview(session_id, user.id)
                    
                    response_msg = {
                        "type": "interview_paused",
                        "session_status": session.status
                    }
                    
                    await manager.send_personal_message(response_msg, session_id, user.id)
                
                elif message_type == "resume_interview":
                    # Resume the interview
                    engine = InterviewEngine(db)
                    session = await engine.resume_interview(session_id, user.id)
                    
                    response_msg = {
                        "type": "interview_resumed",
                        "session_status": session.status
                    }
                    
                    await manager.send_personal_message(response_msg, session_id, user.id)
        
        except WebSocketDisconnect:
            manager.disconnect(session_id, user.id)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            await manager.send_personal_message({
                "type": "error",
                "message": "An error occurred during the interview session"
            }, session_id, user.id)
    
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)


@router.post("/sessions/{session_id}/generate-questions", response_model=List[InterviewQuestionResponse])
async def generate_additional_questions(
    session_id: UUID,
    request: QuestionGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate additional questions for an interview session using AI."""
    
    try:
        engine = InterviewEngine(db)
        session = await engine._get_session(session_id, current_user.id)
        
        # Generate questions using AI
        ai_interviewer = AIInterviewer(db)
        questions = await ai_interviewer.generate_adaptive_questions(
            session=session,
            request=request
        )
        
        # Add questions to session
        for question in questions:
            question.session_id = session_id
            db.add(question)
        
        await db.commit()
        
        # Refresh questions to get IDs
        for question in questions:
            await db.refresh(question)
        
        return questions
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating additional questions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate additional questions"
        )


@router.get("/sessions/{session_id}/performance-analysis", response_model=Dict[str, Any])
async def get_comprehensive_performance_analysis(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive performance analysis for a completed interview session."""
    
    try:
        engine = InterviewEngine(db)
        session = await engine._get_session(session_id, current_user.id, include_responses=True)
        
        if session.status != InterviewStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Interview session must be completed for performance analysis"
            )
        
        # Generate comprehensive analysis
        analyzer = PerformanceAnalyzer(db)
        analysis = await analyzer.generate_comprehensive_analysis(session)
        
        return analysis
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating performance analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate performance analysis"
        )


@router.get("/sessions/{session_id}/improvement-plan", response_model=Dict[str, Any])
async def get_personalized_improvement_plan(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate personalized improvement plan based on interview performance."""
    
    try:
        engine = InterviewEngine(db)
        session = await engine._get_session(session_id, current_user.id, include_responses=True)
        
        if session.status != InterviewStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Interview session must be completed for improvement plan"
            )
        
        # Generate improvement plan
        analyzer = PerformanceAnalyzer(db)
        improvement_plan = await analyzer.generate_improvement_plan(session, current_user)
        
        return improvement_plan
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating improvement plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate improvement plan"
        )


@router.get("/sessions/{session_id}/progress-tracking", response_model=Dict[str, Any])
async def get_real_time_progress(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get real-time progress information for an active interview session."""
    
    try:
        engine = InterviewEngine(db)
        session = await engine._get_session(session_id, current_user.id, include_responses=True)
        
        # Calculate progress metrics
        progress_percentage = (session.current_question_index / session.question_count) * 100
        time_elapsed = 0
        estimated_remaining = 0
        
        if session.start_time:
            from datetime import datetime, timezone
            current_time = datetime.now(timezone.utc)
            time_elapsed = (current_time - session.start_time).total_seconds() / 60  # minutes
            
            if session.current_question_index > 0:
                avg_time_per_question = time_elapsed / session.current_question_index
                remaining_questions = session.question_count - session.current_question_index
                estimated_remaining = avg_time_per_question * remaining_questions
        
        # Calculate current performance metrics
        current_scores = {
            "overall": 0,
            "communication": 0,
            "content": 0
        }
        
        if session.responses:
            valid_responses = [r for r in session.responses if r.overall_score is not None]
            if valid_responses:
                current_scores["overall"] = sum(r.overall_score for r in valid_responses) / len(valid_responses)
                
                comm_scores = [r.communication_score for r in valid_responses if r.communication_score is not None]
                if comm_scores:
                    current_scores["communication"] = sum(comm_scores) / len(comm_scores)
                
                content_scores = [r.content_score for r in valid_responses if r.content_score is not None]
                if content_scores:
                    current_scores["content"] = sum(content_scores) / len(content_scores)
        
        return {
            "session_id": str(session_id),
            "status": session.status,
            "progress": {
                "percentage": round(progress_percentage, 1),
                "questions_answered": session.current_question_index,
                "total_questions": session.question_count,
                "time_elapsed_minutes": round(time_elapsed, 1),
                "estimated_remaining_minutes": round(estimated_remaining, 1)
            },
            "current_performance": current_scores,
            "session_metadata": {
                "interview_type": session.interview_type,
                "difficulty_level": session.difficulty_level,
                "adaptive_mode": session.adaptive_mode
            }
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting progress tracking: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get progress tracking"
        )


async def _save_uploaded_file(
    file: UploadFile, 
    file_type: str, 
    session_id: UUID, 
    question_id: UUID
) -> str:
    """Save uploaded file and return the file path."""
    
    # Create upload directory structure
    upload_dir = Path(settings.UPLOAD_DIR) / "interviews" / str(session_id) / file_type
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix if file.filename else ""
    filename = f"{question_id}{file_extension}"
    file_path = upload_dir / filename
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    return str(file_path)