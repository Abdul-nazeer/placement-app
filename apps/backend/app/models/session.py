from sqlalchemy import Column, String, DateTime, JSON, Numeric, ForeignKey, Integer, Boolean, Float, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property
import uuid
from enum import Enum
from typing import List, Optional, Dict, Any

from app.core.database import Base


class TestType(str, Enum):
    APTITUDE = "aptitude"
    CODING = "coding"
    COMMUNICATION = "communication"
    MOCK_INTERVIEW = "mock_interview"
    MIXED = "mixed"
    CUSTOM = "custom"


class SessionStatus(str, Enum):
    CREATED = "created"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    EXPIRED = "expired"


class TestSession(Base):
    __tablename__ = "test_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Test configuration
    test_type = Column(String(50), nullable=False, index=True)  # TestType enum
    title = Column(String(500), nullable=True)
    description = Column(String(1000), nullable=True)
    configuration = Column(JSON, nullable=False)  # Test settings, filters, etc.
    
    # Question selection and management
    question_ids = Column(ARRAY(UUID), nullable=False)  # Ordered list of question IDs
    current_question_index = Column(Integer, nullable=False, default=0)
    total_questions = Column(Integer, nullable=False)
    
    # Timing and constraints
    time_limit = Column(Integer, nullable=True)  # Total time limit in seconds
    time_per_question = Column(Integer, nullable=True)  # Time per question in seconds
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    pause_time = Column(DateTime(timezone=True), nullable=True)
    total_pause_duration = Column(Integer, nullable=False, default=0)  # Total paused time in seconds
    
    # Session state and results
    status = Column(String(50), nullable=False, default=SessionStatus.CREATED, index=True)
    score = Column(Numeric(5, 2), nullable=True)
    max_score = Column(Numeric(5, 2), nullable=True)
    percentage = Column(Float, nullable=True)
    
    # Analytics and metadata
    correct_answers = Column(Integer, nullable=False, default=0)
    incorrect_answers = Column(Integer, nullable=False, default=0)
    skipped_answers = Column(Integer, nullable=False, default=0)
    total_time_taken = Column(Integer, nullable=True)  # Actual time taken in seconds
    
    # Session settings
    allow_review = Column(Boolean, nullable=False, default=True)
    show_results = Column(Boolean, nullable=False, default=True)
    randomize_questions = Column(Boolean, nullable=False, default=False)
    randomize_options = Column(Boolean, nullable=False, default=False)
    
    # Filtering and categorization
    categories = Column(ARRAY(String), nullable=True)
    difficulty_levels = Column(ARRAY(Integer), nullable=True)
    company_tags = Column(ARRAY(String), nullable=True)
    topic_tags = Column(ARRAY(String), nullable=True)
    
    # Additional metadata
    extra_data = Column(JSON, default=dict)  # Session-specific data
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="test_sessions")
    submissions = relationship("Submission", back_populates="session", cascade="all, delete-orphan")
    
    @hybrid_property
    def is_active(self):
        """Check if session is currently active"""
        return self.status == SessionStatus.ACTIVE
    
    @hybrid_property
    def is_completed(self):
        """Check if session is completed"""
        return self.status == SessionStatus.COMPLETED
    
    @hybrid_property
    def time_remaining(self):
        """Calculate remaining time in seconds"""
        if not self.time_limit or not self.start_time:
            return None
        
        if self.status == SessionStatus.COMPLETED:
            return 0
        
        from datetime import datetime, timezone
        elapsed = (datetime.now(timezone.utc) - self.start_time).total_seconds()
        elapsed -= self.total_pause_duration
        
        return max(0, self.time_limit - int(elapsed))
    
    @hybrid_property
    def progress_percentage(self):
        """Calculate progress percentage"""
        if self.total_questions == 0:
            return 0
        return (self.current_question_index / self.total_questions) * 100
    
    @hybrid_property
    def accuracy_percentage(self):
        """Calculate accuracy percentage"""
        total_answered = self.correct_answers + self.incorrect_answers
        if total_answered == 0:
            return 0
        return (self.correct_answers / total_answered) * 100
    
    def start_session(self):
        """Start the test session"""
        if self.status == SessionStatus.CREATED:
            self.status = SessionStatus.ACTIVE
            self.start_time = func.now()
    
    def pause_session(self):
        """Pause the test session"""
        if self.status == SessionStatus.ACTIVE:
            self.status = SessionStatus.PAUSED
            self.pause_time = func.now()
    
    def resume_session(self):
        """Resume the test session"""
        if self.status == SessionStatus.PAUSED and self.pause_time:
            from datetime import datetime, timezone
            pause_duration = (datetime.now(timezone.utc) - self.pause_time).total_seconds()
            self.total_pause_duration += int(pause_duration)
            self.status = SessionStatus.ACTIVE
            self.pause_time = None
    
    def complete_session(self):
        """Complete the test session"""
        if self.status in [SessionStatus.ACTIVE, SessionStatus.PAUSED]:
            self.status = SessionStatus.COMPLETED
            self.end_time = func.now()
            
            # Calculate final metrics
            if self.total_questions > 0:
                self.percentage = (self.correct_answers / self.total_questions) * 100
    
    def abandon_session(self):
        """Abandon the test session"""
        if self.status in [SessionStatus.ACTIVE, SessionStatus.PAUSED]:
            self.status = SessionStatus.ABANDONED
            self.end_time = func.now()
    
    def update_score(self, submission_score: float):
        """Update session score based on submission"""
        if self.score is None:
            self.score = submission_score
        else:
            self.score += submission_score
    
    def __repr__(self):
        return f"<TestSession(id={self.id}, user_id={self.user_id}, type={self.test_type}, status={self.status}, progress={self.current_question_index}/{self.total_questions})>"


# Create indexes for performance
Index('idx_test_sessions_user_type', TestSession.user_id, TestSession.test_type)
Index('idx_test_sessions_status_created', TestSession.status, TestSession.created_at)
Index('idx_test_sessions_company_tags', TestSession.company_tags, postgresql_using='gin')
Index('idx_test_sessions_topic_tags', TestSession.topic_tags, postgresql_using='gin')