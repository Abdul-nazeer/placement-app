from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, JSON, ForeignKey, Float, Index, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property
import uuid
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from app.core.database import Base


class InterviewType(str, Enum):
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    HR = "hr"
    CASE_STUDY = "case_study"
    MIXED = "mixed"


class InterviewStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class QuestionCategory(str, Enum):
    BEHAVIORAL = "behavioral"
    TECHNICAL_CODING = "technical_coding"
    TECHNICAL_SYSTEM_DESIGN = "technical_system_design"
    HR_GENERAL = "hr_general"
    COMPANY_SPECIFIC = "company_specific"
    SITUATIONAL = "situational"


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Interview configuration
    interview_type = Column(String(50), nullable=False, index=True)  # InterviewType enum
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    company_name = Column(String(200), nullable=True)
    position_title = Column(String(200), nullable=True)
    
    # Session settings
    total_duration = Column(Integer, nullable=False)  # Total duration in minutes
    question_count = Column(Integer, nullable=False, default=10)
    difficulty_level = Column(String(20), nullable=False, default=DifficultyLevel.MEDIUM)
    
    # Adaptive questioning settings
    adaptive_mode = Column(Boolean, nullable=False, default=True)
    performance_threshold = Column(Float, nullable=False, default=0.7)  # Threshold for difficulty adjustment
    
    # Question selection criteria
    question_categories = Column(ARRAY(String), nullable=False)
    company_tags = Column(ARRAY(String), nullable=True)
    topic_tags = Column(ARRAY(String), nullable=True)
    
    # Session state
    status = Column(String(50), nullable=False, default=InterviewStatus.SCHEDULED, index=True)
    current_question_index = Column(Integer, nullable=False, default=0)
    questions_asked = Column(ARRAY(UUID), nullable=False, default=list)  # Track asked questions
    
    # Timing
    scheduled_time = Column(DateTime(timezone=True), nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    pause_time = Column(DateTime(timezone=True), nullable=True)
    total_pause_duration = Column(Integer, nullable=False, default=0)  # seconds
    
    # Recording and analysis
    enable_video_recording = Column(Boolean, nullable=False, default=True)
    enable_audio_recording = Column(Boolean, nullable=False, default=True)
    video_file_url = Column(String(1000), nullable=True)
    audio_file_url = Column(String(1000), nullable=True)
    
    # Performance metrics
    overall_score = Column(Float, nullable=True)  # 0-100
    communication_score = Column(Float, nullable=True)
    technical_score = Column(Float, nullable=True)
    behavioral_score = Column(Float, nullable=True)
    
    # AI Analysis results
    ai_feedback = Column(JSON, default=dict)
    performance_analysis = Column(JSON, default=dict)
    improvement_suggestions = Column(JSON, default=list)
    
    # Session metadata
    extra_data = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="interview_sessions")
    questions = relationship("InterviewQuestion", back_populates="session", cascade="all, delete-orphan")
    responses = relationship("InterviewResponse", back_populates="session", cascade="all, delete-orphan")
    
    @hybrid_property
    def duration_minutes(self):
        """Calculate actual duration in minutes"""
        if not self.start_time or not self.end_time:
            return None
        
        duration = (self.end_time - self.start_time).total_seconds()
        duration -= self.total_pause_duration
        return max(0, duration / 60)
    
    @hybrid_property
    def progress_percentage(self):
        """Calculate progress percentage"""
        if self.question_count == 0:
            return 0
        return (self.current_question_index / self.question_count) * 100
    
    @hybrid_property
    def is_active(self):
        """Check if interview is currently active"""
        return self.status == InterviewStatus.IN_PROGRESS
    
    def start_interview(self):
        """Start the interview session"""
        if self.status == InterviewStatus.SCHEDULED:
            self.status = InterviewStatus.IN_PROGRESS
            self.start_time = datetime.now(timezone.utc)
    
    def pause_interview(self):
        """Pause the interview session"""
        if self.status == InterviewStatus.IN_PROGRESS:
            self.status = InterviewStatus.PAUSED
            self.pause_time = datetime.now(timezone.utc)
    
    def resume_interview(self):
        """Resume the interview session"""
        if self.status == InterviewStatus.PAUSED and self.pause_time:
            pause_duration = (datetime.now(timezone.utc) - self.pause_time).total_seconds()
            self.total_pause_duration += int(pause_duration)
            self.status = InterviewStatus.IN_PROGRESS
            self.pause_time = None
    
    def complete_interview(self):
        """Complete the interview session"""
        if self.status in [InterviewStatus.IN_PROGRESS, InterviewStatus.PAUSED]:
            self.status = InterviewStatus.COMPLETED
            self.end_time = datetime.now(timezone.utc)
    
    def __repr__(self):
        return f"<InterviewSession(id={self.id}, user_id={self.user_id}, type={self.interview_type}, status={self.status})>"


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Question details
    question_text = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, index=True)  # QuestionCategory enum
    difficulty_level = Column(String(20), nullable=False)
    expected_duration = Column(Integer, nullable=False)  # Expected answer duration in seconds
    
    # Question metadata
    question_order = Column(Integer, nullable=False)
    is_followup = Column(Boolean, nullable=False, default=False)
    parent_question_id = Column(UUID(as_uuid=True), ForeignKey("interview_questions.id"), nullable=True)
    
    # AI generation metadata
    generated_by_ai = Column(Boolean, nullable=False, default=True)
    generation_prompt = Column(Text, nullable=True)
    generation_context = Column(JSON, default=dict)
    
    # Question context and hints
    context_information = Column(Text, nullable=True)
    evaluation_criteria = Column(JSON, default=list)  # List of evaluation points
    sample_answers = Column(JSON, default=list)  # Sample good answers
    
    # Adaptive questioning
    difficulty_adjustment = Column(Float, nullable=True)  # Adjustment based on previous performance
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    asked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    session = relationship("InterviewSession", back_populates="questions")
    responses = relationship("InterviewResponse", back_populates="question", cascade="all, delete-orphan")
    followup_questions = relationship("InterviewQuestion", backref="parent_question", remote_side=[id])
    
    def __repr__(self):
        return f"<InterviewQuestion(id={self.id}, session_id={self.session_id}, category={self.category}, order={self.question_order})>"


class InterviewResponse(Base):
    __tablename__ = "interview_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey("interview_questions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Response content
    response_text = Column(Text, nullable=True)  # Transcribed text
    audio_file_url = Column(String(1000), nullable=True)
    video_file_url = Column(String(1000), nullable=True)
    
    # Response timing
    response_duration = Column(Integer, nullable=False)  # Duration in seconds
    thinking_time = Column(Integer, nullable=False, default=0)  # Time before starting to answer
    
    # AI Analysis
    transcript_confidence = Column(Float, nullable=True)  # Speech-to-text confidence
    sentiment_score = Column(Float, nullable=True)  # -1 to 1
    confidence_level = Column(Float, nullable=True)  # 0 to 1
    
    # Communication analysis
    speech_pace = Column(Float, nullable=True)  # Words per minute
    filler_word_count = Column(Integer, nullable=False, default=0)
    pause_count = Column(Integer, nullable=False, default=0)
    volume_consistency = Column(Float, nullable=True)  # 0 to 1
    
    # Content analysis
    content_relevance = Column(Float, nullable=True)  # 0 to 1
    technical_accuracy = Column(Float, nullable=True)  # 0 to 1 (for technical questions)
    structure_score = Column(Float, nullable=True)  # How well structured the answer is
    
    # Scoring
    overall_score = Column(Float, nullable=True)  # 0 to 100
    communication_score = Column(Float, nullable=True)
    content_score = Column(Float, nullable=True)
    
    # AI Feedback
    ai_feedback = Column(Text, nullable=True)
    improvement_suggestions = Column(JSON, default=list)
    strengths = Column(JSON, default=list)
    weaknesses = Column(JSON, default=list)
    
    # Analysis metadata
    analysis_version = Column(String(50), nullable=True)
    processing_time = Column(Float, nullable=True)  # Time taken for AI analysis
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    analyzed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    session = relationship("InterviewSession", back_populates="responses")
    question = relationship("InterviewQuestion", back_populates="responses")
    
    @hybrid_property
    def response_efficiency(self):
        """Calculate response efficiency (content vs time)"""
        if not self.response_duration or not self.response_text:
            return None
        
        word_count = len(self.response_text.split())
        if word_count == 0:
            return 0
        
        # Words per second (optimal range is 2-3 words per second)
        words_per_second = word_count / self.response_duration
        optimal_rate = 2.5
        
        return min(1.0, words_per_second / optimal_rate)
    
    def __repr__(self):
        return f"<InterviewResponse(id={self.id}, session_id={self.session_id}, question_id={self.question_id}, score={self.overall_score})>"


# Create indexes for performance
Index('idx_interview_sessions_user_status', InterviewSession.user_id, InterviewSession.status)
Index('idx_interview_sessions_type_created', InterviewSession.interview_type, InterviewSession.created_at)
Index('idx_interview_sessions_company_tags', InterviewSession.company_tags, postgresql_using='gin')

Index('idx_interview_questions_session_order', InterviewQuestion.session_id, InterviewQuestion.question_order)
Index('idx_interview_questions_category_difficulty', InterviewQuestion.category, InterviewQuestion.difficulty_level)

Index('idx_interview_responses_session_question', InterviewResponse.session_id, InterviewResponse.question_id)
Index('idx_interview_responses_analysis', InterviewResponse.overall_score, InterviewResponse.analyzed_at)