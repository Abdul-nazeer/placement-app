"""Communication assessment models."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class CommunicationSession(Base):
    """Communication practice session model."""
    
    __tablename__ = "communication_sessions"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_type = Column(String(50), nullable=False)  # hr_interview, behavioral, presentation
    prompt_id = Column(PGUUID(as_uuid=True), ForeignKey("communication_prompts.id"))
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime)
    status = Column(String(20), nullable=False, default="active")  # active, completed, abandoned
    overall_score = Column(Float)
    feedback = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="communication_sessions")
    prompt = relationship("CommunicationPrompt", back_populates="sessions")
    recordings = relationship("CommunicationRecording", back_populates="session", cascade="all, delete-orphan")


class CommunicationPrompt(Base):
    """Communication practice prompts and scenarios."""
    
    __tablename__ = "communication_prompts"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    prompt_text = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # hr_interview, behavioral, presentation
    difficulty_level = Column(Integer, nullable=False, default=1)  # 1-5
    time_limit = Column(Integer)  # seconds
    evaluation_criteria = Column(JSON)  # List of criteria to evaluate
    tags = Column(JSON)  # List of tags for filtering
    is_active = Column(String(10), nullable=False, default="true")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sessions = relationship("CommunicationSession", back_populates="prompt")


class CommunicationRecording(Base):
    """Audio recordings and their analysis results."""
    
    __tablename__ = "communication_recordings"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(PGUUID(as_uuid=True), ForeignKey("communication_sessions.id"), nullable=False)
    audio_file_path = Column(String(500), nullable=False)
    duration = Column(Float)  # seconds
    file_size = Column(Integer)  # bytes
    transcript = Column(Text)
    confidence_score = Column(Float)  # ASR confidence
    processing_status = Column(String(20), nullable=False, default="pending")  # pending, processing, completed, failed
    analysis_results = Column(JSON)  # Detailed analysis metrics
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    
    # Relationships
    session = relationship("CommunicationSession", back_populates="recordings")


class CommunicationAnalysis(Base):
    """Detailed communication analysis results."""
    
    __tablename__ = "communication_analyses"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    recording_id = Column(PGUUID(as_uuid=True), ForeignKey("communication_recordings.id"), nullable=False)
    
    # Speech metrics
    words_per_minute = Column(Float)
    pause_frequency = Column(Float)  # pauses per minute
    average_pause_duration = Column(Float)  # seconds
    filler_word_count = Column(Integer)
    filler_word_percentage = Column(Float)
    
    # Language metrics
    grammar_score = Column(Float)  # 0-1
    vocabulary_complexity = Column(Float)  # 0-1
    sentence_structure_score = Column(Float)  # 0-1
    clarity_score = Column(Float)  # 0-1
    
    # Content metrics
    relevance_score = Column(Float)  # 0-1
    completeness_score = Column(Float)  # 0-1
    coherence_score = Column(Float)  # 0-1
    
    # Overall metrics
    fluency_score = Column(Float)  # 0-1
    confidence_score = Column(Float)  # 0-1
    overall_score = Column(Float)  # 0-1
    
    # Detailed analysis
    strengths = Column(JSON)  # List of identified strengths
    weaknesses = Column(JSON)  # List of areas for improvement
    suggestions = Column(JSON)  # List of improvement suggestions
    filler_words_detected = Column(JSON)  # List of filler words with timestamps
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    recording = relationship("CommunicationRecording")


class CommunicationProgress(Base):
    """User progress tracking for communication skills."""
    
    __tablename__ = "communication_progress"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    skill_category = Column(String(50), nullable=False)  # fluency, grammar, vocabulary, etc.
    current_level = Column(Float, nullable=False, default=0.0)  # 0-1
    sessions_completed = Column(Integer, nullable=False, default=0)
    total_practice_time = Column(Integer, nullable=False, default=0)  # seconds
    last_session_date = Column(DateTime)
    improvement_rate = Column(Float)  # rate of improvement per session
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="communication_progress")