from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, JSON, ForeignKey, Float, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property
import uuid
from enum import Enum
from typing import Dict, Any, Optional

from app.core.database import Base


class SubmissionType(str, Enum):
    APTITUDE = "aptitude"
    CODE = "code"
    COMMUNICATION = "communication"
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"


class SubmissionStatus(str, Enum):
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    EVALUATED = "evaluated"
    FAILED = "failed"
    PENDING_REVIEW = "pending_review"


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("test_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Submission details
    submission_type = Column(String(50), nullable=False, index=True)  # SubmissionType enum
    user_answer = Column(Text, nullable=False)
    
    # Evaluation results
    is_correct = Column(Boolean, nullable=True)
    score = Column(Float, nullable=True)  # Normalized score (0-100)
    max_score = Column(Float, nullable=True)  # Maximum possible score
    
    # Timing and performance
    time_taken = Column(Integer, nullable=False)  # seconds
    time_limit = Column(Integer, nullable=True)  # Time limit for this question
    
    # Status and processing
    status = Column(String(50), nullable=False, default=SubmissionStatus.SUBMITTED, index=True)
    evaluation_attempts = Column(Integer, nullable=False, default=0)
    
    # Type-specific data (polymorphic design)
    extra_data = Column(JSON, default=dict)  # Additional data like execution results, analysis, etc.
    
    # Feedback and analysis
    feedback = Column(Text, nullable=True)
    detailed_analysis = Column(JSON, default=dict)  # Detailed breakdown of performance
    
    # Administrative
    evaluated_by = Column(String(50), nullable=True)  # System, AI, or human evaluator
    evaluation_time = Column(Float, nullable=True)  # Time taken to evaluate in seconds
    
    # Timestamps
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    evaluated_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="submissions")
    session = relationship("TestSession", back_populates="submissions")
    question = relationship("Question", back_populates="submissions")
    
    @hybrid_property
    def percentage_score(self):
        """Calculate percentage score"""
        if self.score is None or self.max_score is None or self.max_score == 0:
            return None
        return (self.score / self.max_score) * 100
    
    @hybrid_property
    def is_within_time_limit(self):
        """Check if submission was within time limit"""
        if self.time_limit is None:
            return True
        return self.time_taken <= self.time_limit
    
    @hybrid_property
    def efficiency_score(self):
        """Calculate efficiency based on time taken vs time limit"""
        if self.time_limit is None or self.time_taken == 0:
            return None
        
        if self.time_taken > self.time_limit:
            return 0  # Over time limit
        
        # Higher score for faster completion
        return max(0, 100 - ((self.time_taken / self.time_limit) * 50))
    
    def set_correct(self, score: float = 100.0):
        """Mark submission as correct"""
        self.is_correct = True
        self.score = score
        self.status = SubmissionStatus.EVALUATED
        self.evaluated_at = func.now()
    
    def set_incorrect(self, score: float = 0.0):
        """Mark submission as incorrect"""
        self.is_correct = False
        self.score = score
        self.status = SubmissionStatus.EVALUATED
        self.evaluated_at = func.now()
    
    def set_partial_credit(self, score: float, max_score: float = 100.0):
        """Set partial credit score"""
        self.score = score
        self.max_score = max_score
        self.is_correct = score >= (max_score * 0.5)  # 50% threshold for "correct"
        self.status = SubmissionStatus.EVALUATED
        self.evaluated_at = func.now()
    
    def add_feedback(self, feedback: str, analysis: Dict[str, Any] = None):
        """Add feedback and detailed analysis"""
        self.feedback = feedback
        if analysis:
            self.detailed_analysis = analysis
    
    def update_metadata(self, key: str, value: Any):
        """Update specific metadata field"""
        if self.extra_data is None:
            self.extra_data = {}
        self.extra_data[key] = value
    
    def get_metadata(self, key: str, default: Any = None):
        """Get specific metadata field"""
        if self.extra_data is None:
            return default
        return self.extra_data.get(key, default)
    
    def __repr__(self):
        return f"<Submission(id={self.id}, user_id={self.user_id}, question_id={self.question_id}, type={self.submission_type}, score={self.score}, status={self.status})>"


# Create indexes for performance and analytics
Index('idx_submissions_user_session', Submission.user_id, Submission.session_id)
Index('idx_submissions_question_type', Submission.question_id, Submission.submission_type)
Index('idx_submissions_evaluation', Submission.status, Submission.evaluated_at)
Index('idx_submissions_performance', Submission.score, Submission.time_taken, Submission.is_correct)
Index('idx_submissions_analytics', Submission.submission_type, Submission.is_correct, Submission.submitted_at)