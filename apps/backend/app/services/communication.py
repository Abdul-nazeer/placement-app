"""Communication assessment service."""

import logging
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from uuid import UUID

import aiofiles
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models.communication import (
    CommunicationAnalysis,
    CommunicationProgress,
    CommunicationPrompt,
    CommunicationRecording,
    CommunicationSession,
)
from app.schemas.communication import (
    CommunicationAnalysisCreate,
    CommunicationDashboard,
    CommunicationFeedback,
    CommunicationProgressUpdate,
    CommunicationPromptCreate,
    CommunicationPromptUpdate,
    CommunicationSessionCreate,
    CommunicationSessionUpdate,
)
from app.services.speech_processing import speech_processor

logger = logging.getLogger(__name__)


class CommunicationService:
    """Service for managing communication assessment functionality."""
    
    def __init__(self):
        """Initialize communication service."""
        self.upload_dir = Path(settings.UPLOAD_DIR) / "communication"
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Prompt Management
    async def create_prompt(
        self, 
        db: AsyncSession, 
        prompt_data: CommunicationPromptCreate
    ) -> CommunicationPrompt:
        """Create a new communication prompt."""
        try:
            prompt = CommunicationPrompt(**prompt_data.model_dump())
            db.add(prompt)
            await db.commit()
            await db.refresh(prompt)
            
            logger.info(f"Created communication prompt: {prompt.id}")
            return prompt
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating communication prompt: {e}")
            raise
    
    async def get_prompts(
        self,
        db: AsyncSession,
        category: Optional[str] = None,
        difficulty_level: Optional[int] = None,
        tags: Optional[List[str]] = None,
        is_active: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[CommunicationPrompt]:
        """Get communication prompts with filtering."""
        try:
            query = select(CommunicationPrompt)
            
            # Apply filters
            if is_active:
                query = query.where(CommunicationPrompt.is_active == "true")
            
            if category:
                query = query.where(CommunicationPrompt.category == category)
            
            if difficulty_level:
                query = query.where(CommunicationPrompt.difficulty_level == difficulty_level)
            
            if tags:
                # Filter by tags (PostgreSQL array contains)
                for tag in tags:
                    query = query.where(CommunicationPrompt.tags.contains([tag]))
            
            query = query.offset(skip).limit(limit).order_by(CommunicationPrompt.created_at.desc())
            
            result = await db.execute(query)
            prompts = result.scalars().all()
            
            logger.info(f"Retrieved {len(prompts)} communication prompts")
            return prompts
            
        except Exception as e:
            logger.error(f"Error retrieving communication prompts: {e}")
            raise
    
    async def get_prompt_by_id(self, db: AsyncSession, prompt_id: UUID) -> Optional[CommunicationPrompt]:
        """Get a communication prompt by ID."""
        try:
            query = select(CommunicationPrompt).where(CommunicationPrompt.id == prompt_id)
            result = await db.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error retrieving communication prompt {prompt_id}: {e}")
            raise
    
    async def update_prompt(
        self,
        db: AsyncSession,
        prompt_id: UUID,
        prompt_data: CommunicationPromptUpdate
    ) -> Optional[CommunicationPrompt]:
        """Update a communication prompt."""
        try:
            prompt = await self.get_prompt_by_id(db, prompt_id)
            if not prompt:
                return None
            
            update_data = prompt_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(prompt, field, value)
            
            prompt.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(prompt)
            
            logger.info(f"Updated communication prompt: {prompt_id}")
            return prompt
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating communication prompt {prompt_id}: {e}")
            raise
    
    # Session Management
    async def create_session(
        self,
        db: AsyncSession,
        user_id: UUID,
        session_data: CommunicationSessionCreate
    ) -> CommunicationSession:
        """Create a new communication session."""
        try:
            session = CommunicationSession(
                user_id=user_id,
                **session_data.model_dump()
            )
            
            db.add(session)
            await db.commit()
            await db.refresh(session)
            
            logger.info(f"Created communication session: {session.id} for user: {user_id}")
            return session
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating communication session: {e}")
            raise
    
    async def get_session_by_id(
        self, 
        db: AsyncSession, 
        session_id: UUID,
        user_id: Optional[UUID] = None
    ) -> Optional[CommunicationSession]:
        """Get a communication session by ID."""
        try:
            query = select(CommunicationSession).options(
                selectinload(CommunicationSession.prompt),
                selectinload(CommunicationSession.recordings)
            ).where(CommunicationSession.id == session_id)
            
            if user_id:
                query = query.where(CommunicationSession.user_id == user_id)
            
            result = await db.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error retrieving communication session {session_id}: {e}")
            raise
    
    async def update_session(
        self,
        db: AsyncSession,
        session_id: UUID,
        session_data: CommunicationSessionUpdate,
        user_id: Optional[UUID] = None
    ) -> Optional[CommunicationSession]:
        """Update a communication session."""
        try:
            session = await self.get_session_by_id(db, session_id, user_id)
            if not session:
                return None
            
            update_data = session_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(session, field, value)
            
            if session_data.status == "completed" and not session.end_time:
                session.end_time = datetime.utcnow()
            
            session.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(session)
            
            logger.info(f"Updated communication session: {session_id}")
            return session
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating communication session {session_id}: {e}")
            raise
    
    async def get_user_sessions(
        self,
        db: AsyncSession,
        user_id: UUID,
        session_type: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[CommunicationSession]:
        """Get user's communication sessions."""
        try:
            query = select(CommunicationSession).options(
                selectinload(CommunicationSession.prompt)
            ).where(CommunicationSession.user_id == user_id)
            
            if session_type:
                query = query.where(CommunicationSession.session_type == session_type)
            
            if status:
                query = query.where(CommunicationSession.status == status)
            
            query = query.offset(skip).limit(limit).order_by(CommunicationSession.created_at.desc())
            
            result = await db.execute(query)
            sessions = result.scalars().all()
            
            logger.info(f"Retrieved {len(sessions)} sessions for user: {user_id}")
            return sessions
            
        except Exception as e:
            logger.error(f"Error retrieving sessions for user {user_id}: {e}")
            raise
    
    # Audio Processing
    async def save_audio_file(self, audio_data: bytes, session_id: UUID, file_extension: str = "wav") -> str:
        """Save uploaded audio file and return file path."""
        try:
            # Create session-specific directory
            session_dir = self.upload_dir / str(session_id)
            session_dir.mkdir(exist_ok=True)
            
            # Generate unique filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.{file_extension}"
            file_path = session_dir / filename
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(audio_data)
            
            logger.info(f"Saved audio file: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error saving audio file: {e}")
            raise
    
    async def create_recording(
        self,
        db: AsyncSession,
        session_id: UUID,
        audio_file_path: str,
        duration: Optional[float] = None,
        file_size: Optional[int] = None
    ) -> CommunicationRecording:
        """Create a new communication recording entry."""
        try:
            recording = CommunicationRecording(
                session_id=session_id,
                audio_file_path=audio_file_path,
                duration=duration,
                file_size=file_size
            )
            
            db.add(recording)
            await db.commit()
            await db.refresh(recording)
            
            logger.info(f"Created communication recording: {recording.id}")
            return recording
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating communication recording: {e}")
            raise
    
    async def process_audio_recording(
        self,
        db: AsyncSession,
        recording_id: UUID,
        prompt_text: str = ""
    ) -> CommunicationRecording:
        """Process audio recording with speech analysis."""
        try:
            # Get recording
            query = select(CommunicationRecording).where(CommunicationRecording.id == recording_id)
            result = await db.execute(query)
            recording = result.scalar_one_or_none()
            
            if not recording:
                raise ValueError(f"Recording not found: {recording_id}")
            
            # Update status to processing
            recording.processing_status = "processing"
            await db.commit()
            
            # Transcribe audio
            transcript, confidence, detailed_results = await speech_processor.transcribe_audio(
                recording.audio_file_path
            )
            
            # Update recording with transcript
            recording.transcript = transcript
            recording.confidence_score = confidence
            recording.analysis_results = detailed_results
            
            # Generate comprehensive analysis
            word_timestamps = detailed_results.get("word_timestamps", [])
            analysis_data = await speech_processor.generate_comprehensive_analysis(
                transcript, word_timestamps, prompt_text
            )
            
            # Create analysis record
            analysis = CommunicationAnalysis(
                recording_id=recording_id,
                **analysis_data
            )
            
            db.add(analysis)
            
            # Update recording status
            recording.processing_status = "completed"
            recording.processed_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(recording)
            
            logger.info(f"Processed audio recording: {recording_id}")
            return recording
            
        except Exception as e:
            # Update status to failed
            if recording:
                recording.processing_status = "failed"
                await db.commit()
            
            logger.error(f"Error processing audio recording {recording_id}: {e}")
            raise
    
    async def get_recording_analysis(
        self,
        db: AsyncSession,
        recording_id: UUID
    ) -> Optional[CommunicationAnalysis]:
        """Get analysis for a recording."""
        try:
            query = select(CommunicationAnalysis).where(
                CommunicationAnalysis.recording_id == recording_id
            )
            result = await db.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error retrieving analysis for recording {recording_id}: {e}")
            raise
    
    # Progress Tracking
    async def update_user_progress(
        self,
        db: AsyncSession,
        user_id: UUID,
        skill_category: str,
        session_score: float,
        practice_time: int
    ) -> CommunicationProgress:
        """Update user's communication progress."""
        try:
            # Get existing progress or create new
            query = select(CommunicationProgress).where(
                and_(
                    CommunicationProgress.user_id == user_id,
                    CommunicationProgress.skill_category == skill_category
                )
            )
            result = await db.execute(query)
            progress = result.scalar_one_or_none()
            
            if not progress:
                progress = CommunicationProgress(
                    user_id=user_id,
                    skill_category=skill_category,
                    current_level=session_score,
                    sessions_completed=1,
                    total_practice_time=practice_time,
                    last_session_date=datetime.utcnow()
                )
                db.add(progress)
            else:
                # Calculate improvement rate
                old_level = progress.current_level
                new_level = (progress.current_level * progress.sessions_completed + session_score) / (progress.sessions_completed + 1)
                improvement_rate = (new_level - old_level) if progress.sessions_completed > 0 else 0
                
                # Update progress
                progress.current_level = new_level
                progress.sessions_completed += 1
                progress.total_practice_time += practice_time
                progress.last_session_date = datetime.utcnow()
                progress.improvement_rate = improvement_rate
                progress.updated_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(progress)
            
            logger.info(f"Updated progress for user {user_id}, skill: {skill_category}")
            return progress
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating user progress: {e}")
            raise
    
    async def get_user_progress(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> List[CommunicationProgress]:
        """Get user's communication progress across all skills."""
        try:
            query = select(CommunicationProgress).where(
                CommunicationProgress.user_id == user_id
            ).order_by(CommunicationProgress.skill_category)
            
            result = await db.execute(query)
            progress_list = result.scalars().all()
            
            logger.info(f"Retrieved progress for user: {user_id}")
            return progress_list
            
        except Exception as e:
            logger.error(f"Error retrieving user progress {user_id}: {e}")
            raise
    
    # Dashboard and Analytics
    async def get_user_dashboard(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> CommunicationDashboard:
        """Get comprehensive dashboard data for user."""
        try:
            # Get basic stats
            sessions_query = select(func.count(CommunicationSession.id)).where(
                CommunicationSession.user_id == user_id
            )
            sessions_result = await db.execute(sessions_query)
            total_sessions = sessions_result.scalar() or 0
            
            # Get total practice time
            time_query = select(func.sum(CommunicationSession.overall_score)).where(
                and_(
                    CommunicationSession.user_id == user_id,
                    CommunicationSession.status == "completed"
                )
            )
            time_result = await db.execute(time_query)
            
            # Calculate average score
            score_query = select(func.avg(CommunicationSession.overall_score)).where(
                and_(
                    CommunicationSession.user_id == user_id,
                    CommunicationSession.overall_score.isnot(None)
                )
            )
            score_result = await db.execute(score_query)
            average_score = score_result.scalar()
            
            # Get skill progress
            skill_progress = await self.get_user_progress(db, user_id)
            
            # Get recent sessions
            recent_sessions = await self.get_user_sessions(db, user_id, limit=5)
            
            # Generate recommendations (simplified)
            strengths, areas_for_improvement, recommended_exercises = await self._generate_recommendations(
                db, user_id, skill_progress
            )
            
            dashboard = CommunicationDashboard(
                user_id=user_id,
                total_sessions=total_sessions,
                total_practice_time=0,  # Calculate from session durations
                average_score=float(average_score) if average_score else None,
                skill_progress=skill_progress,
                recent_sessions=recent_sessions,
                strengths=strengths,
                areas_for_improvement=areas_for_improvement,
                recommended_exercises=recommended_exercises
            )
            
            logger.info(f"Generated dashboard for user: {user_id}")
            return dashboard
            
        except Exception as e:
            logger.error(f"Error generating dashboard for user {user_id}: {e}")
            raise
    
    async def _generate_recommendations(
        self,
        db: AsyncSession,
        user_id: UUID,
        skill_progress: List[CommunicationProgress]
    ) -> tuple[List[str], List[str], List[str]]:
        """Generate personalized recommendations based on user progress."""
        try:
            strengths = []
            areas_for_improvement = []
            recommended_exercises = []
            
            # Analyze skill levels
            for progress in skill_progress:
                if progress.current_level >= 0.8:
                    strengths.append(f"Excellent {progress.skill_category} skills")
                elif progress.current_level >= 0.6:
                    strengths.append(f"Good {progress.skill_category} abilities")
                elif progress.current_level < 0.4:
                    areas_for_improvement.append(f"{progress.skill_category} needs attention")
                    recommended_exercises.append(f"Practice {progress.skill_category} exercises daily")
            
            # Default recommendations if no specific data
            if not strengths:
                strengths.append("Keep practicing to build your communication skills")
            
            if not areas_for_improvement:
                areas_for_improvement.append("Continue developing advanced communication techniques")
            
            if not recommended_exercises:
                recommended_exercises.extend([
                    "Practice daily speaking exercises",
                    "Record yourself and analyze your speech patterns",
                    "Work on reducing filler words"
                ])
            
            return strengths, areas_for_improvement, recommended_exercises
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return [], [], []


# Global instance
communication_service = CommunicationService()