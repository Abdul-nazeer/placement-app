"""Communication assessment API endpoints."""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.communication import (
    CommunicationDashboard,
    CommunicationFeedback,
    CommunicationPrompt,
    CommunicationPromptCreate,
    CommunicationPromptUpdate,
    CommunicationProgress,
    CommunicationRecording,
    CommunicationSession,
    CommunicationSessionCreate,
    CommunicationSessionUpdate,
    CommunicationSessionWithPrompt,
)
from app.services.communication import communication_service

logger = logging.getLogger(__name__)

router = APIRouter()


# Prompt Management
@router.get("/prompts", response_model=List[CommunicationPrompt])
async def get_communication_prompts(
    category: Optional[str] = None,
    difficulty_level: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get communication prompts with filtering."""
    try:
        prompts = await communication_service.get_prompts(
            db=db,
            category=category,
            difficulty_level=difficulty_level,
            skip=skip,
            limit=limit
        )
        return prompts
    except Exception as e:
        logger.error(f"Error retrieving communication prompts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve communication prompts"
        )


@router.get("/prompts/{prompt_id}", response_model=CommunicationPrompt)
async def get_communication_prompt(
    prompt_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific communication prompt."""
    try:
        prompt = await communication_service.get_prompt_by_id(db, prompt_id)
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Communication prompt not found"
            )
        return prompt
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving communication prompt {prompt_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve communication prompt"
        )


@router.post("/prompts", response_model=CommunicationPrompt)
async def create_communication_prompt(
    prompt_data: CommunicationPromptCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new communication prompt (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create prompts"
        )
    
    try:
        prompt = await communication_service.create_prompt(db, prompt_data)
        return prompt
    except Exception as e:
        logger.error(f"Error creating communication prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create communication prompt"
        )


# Session Management
@router.post("/sessions", response_model=CommunicationSession)
async def create_communication_session(
    session_data: CommunicationSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new communication practice session."""
    try:
        session = await communication_service.create_session(
            db=db,
            user_id=current_user.id,
            session_data=session_data
        )
        return session
    except Exception as e:
        logger.error(f"Error creating communication session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create communication session"
        )


@router.get("/sessions", response_model=List[CommunicationSessionWithPrompt])
async def get_user_sessions(
    session_type: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's communication sessions."""
    try:
        sessions = await communication_service.get_user_sessions(
            db=db,
            user_id=current_user.id,
            session_type=session_type,
            status=status,
            skip=skip,
            limit=limit
        )
        return sessions
    except Exception as e:
        logger.error(f"Error retrieving user sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve communication sessions"
        )


@router.get("/sessions/{session_id}", response_model=CommunicationSessionWithPrompt)
async def get_communication_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific communication session."""
    try:
        session = await communication_service.get_session_by_id(
            db=db,
            session_id=session_id,
            user_id=current_user.id
        )
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Communication session not found"
            )
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving communication session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve communication session"
        )


@router.put("/sessions/{session_id}", response_model=CommunicationSession)
async def update_communication_session(
    session_id: UUID,
    session_data: CommunicationSessionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a communication session."""
    try:
        session = await communication_service.update_session(
            db=db,
            session_id=session_id,
            session_data=session_data,
            user_id=current_user.id
        )
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Communication session not found"
            )
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating communication session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update communication session"
        )


# Audio Recording and Processing
@router.post("/sessions/{session_id}/upload-audio", response_model=CommunicationRecording)
async def upload_audio_recording(
    session_id: UUID,
    audio_file: UploadFile = File(...),
    duration: Optional[float] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload audio recording for a communication session."""
    try:
        # Verify session belongs to user
        session = await communication_service.get_session_by_id(
            db=db,
            session_id=session_id,
            user_id=current_user.id
        )
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Communication session not found"
            )
        
        # Validate file type
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Please upload an audio file."
            )
        
        # Read and save audio file
        audio_data = await audio_file.read()
        file_extension = audio_file.filename.split('.')[-1] if audio_file.filename else 'wav'
        
        audio_file_path = await communication_service.save_audio_file(
            audio_data=audio_data,
            session_id=session_id,
            file_extension=file_extension
        )
        
        # Create recording entry
        recording = await communication_service.create_recording(
            db=db,
            session_id=session_id,
            audio_file_path=audio_file_path,
            duration=duration,
            file_size=len(audio_data)
        )
        
        # Start background processing
        prompt_text = session.prompt.prompt_text if session.prompt else ""
        processed_recording = await communication_service.process_audio_recording(
            db=db,
            recording_id=recording.id,
            prompt_text=prompt_text
        )
        
        return processed_recording
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading audio recording: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload audio recording"
        )


@router.get("/recordings/{recording_id}/analysis")
async def get_recording_analysis(
    recording_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get analysis results for a recording."""
    try:
        analysis = await communication_service.get_recording_analysis(db, recording_id)
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving recording analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recording analysis"
        )


# Progress and Analytics
@router.get("/progress", response_model=List[CommunicationProgress])
async def get_communication_progress(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's communication progress."""
    try:
        progress = await communication_service.get_user_progress(db, current_user.id)
        return progress
    except Exception as e:
        logger.error(f"Error retrieving communication progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve communication progress"
        )


@router.get("/dashboard", response_model=CommunicationDashboard)
async def get_communication_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive communication dashboard data."""
    try:
        dashboard = await communication_service.get_user_dashboard(db, current_user.id)
        return dashboard
    except Exception as e:
        logger.error(f"Error retrieving communication dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve communication dashboard"
        )