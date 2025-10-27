from sqlalchemy import Column, String, Integer, Text, JSON, DateTime, Boolean, Float, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY, TSVECTOR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property
import uuid
from enum import Enum
from typing import List, Optional

from app.core.database import Base


class QuestionType(str, Enum):
    APTITUDE = "aptitude"
    CODING = "coding"
    COMMUNICATION = "communication"
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"


class DifficultyLevel(int, Enum):
    BEGINNER = 1
    EASY = 2
    MEDIUM = 3
    HARD = 4
    EXPERT = 5


class QuestionStatus(str, Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Core question properties
    type = Column(String(50), nullable=False, index=True)  # QuestionType enum
    category = Column(String(100), nullable=False, index=True)
    subcategory = Column(String(100), nullable=True, index=True)
    difficulty = Column(Integer, nullable=False, index=True)  # DifficultyLevel enum
    
    # Content and answers
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)  # For multiple choice questions
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    hints = Column(JSON, nullable=True)  # Array of hints
    
    # Metadata and organization
    company_tags = Column(ARRAY(String), default=list, index=True)
    topic_tags = Column(ARRAY(String), default=list, index=True)
    skill_tags = Column(ARRAY(String), default=list, index=True)
    
    # Question-specific metadata (polymorphic design)
    extra_data = Column(JSON, default=dict)  # Type-specific data
    
    # Content management
    status = Column(String(50), nullable=False, default=QuestionStatus.DRAFT, index=True)
    version = Column(Integer, nullable=False, default=1)
    parent_question_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # For versioning
    
    # Analytics and performance
    usage_count = Column(Integer, nullable=False, default=0)
    success_rate = Column(Float, nullable=True)  # Percentage of correct answers
    average_time = Column(Float, nullable=True)  # Average time to solve in seconds
    
    # Administrative
    created_by = Column(UUID(as_uuid=True), nullable=True, index=True)  # User who created
    reviewed_by = Column(UUID(as_uuid=True), nullable=True, index=True)  # User who reviewed
    is_active = Column(Boolean, nullable=False, default=True)
    is_premium = Column(Boolean, nullable=False, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Full-text search vector
    search_vector = Column(TSVECTOR)
    
    # Relationships
    submissions = relationship("Submission", back_populates="question", cascade="all, delete-orphan")
    
    @hybrid_property
    def difficulty_name(self):
        """Get human-readable difficulty name"""
        difficulty_map = {
            1: "Beginner",
            2: "Easy", 
            3: "Medium",
            4: "Hard",
            5: "Expert"
        }
        return difficulty_map.get(self.difficulty, "Unknown")
    
    @hybrid_property
    def all_tags(self):
        """Get all tags combined"""
        tags = []
        if self.company_tags:
            tags.extend(self.company_tags)
        if self.topic_tags:
            tags.extend(self.topic_tags)
        if self.skill_tags:
            tags.extend(self.skill_tags)
        return list(set(tags))
    
    def increment_usage(self):
        """Increment usage count"""
        self.usage_count += 1
    
    def update_analytics(self, is_correct: bool, time_taken: float):
        """Update question analytics based on submission"""
        # Update success rate
        if self.success_rate is None:
            self.success_rate = 100.0 if is_correct else 0.0
        else:
            # Simple moving average approximation
            total_attempts = self.usage_count
            if total_attempts > 0:
                current_correct = (self.success_rate / 100.0) * total_attempts
                if is_correct:
                    current_correct += 1
                self.success_rate = (current_correct / (total_attempts + 1)) * 100.0
        
        # Update average time
        if self.average_time is None:
            self.average_time = time_taken
        else:
            # Simple moving average
            total_attempts = self.usage_count
            if total_attempts > 0:
                self.average_time = ((self.average_time * total_attempts) + time_taken) / (total_attempts + 1)
    
    def __repr__(self):
        return f"<Question(id={self.id}, type={self.type}, category={self.category}, difficulty={self.difficulty}, status={self.status})>"


# Create indexes for full-text search and performance
Index('idx_questions_search_vector', Question.search_vector, postgresql_using='gin')
Index('idx_questions_compound_filter', Question.type, Question.category, Question.difficulty, Question.status)
Index('idx_questions_company_tags', Question.company_tags, postgresql_using='gin')
Index('idx_questions_topic_tags', Question.topic_tags, postgresql_using='gin')
Index('idx_questions_skill_tags', Question.skill_tags, postgresql_using='gin')
Index('idx_questions_analytics', Question.success_rate, Question.average_time, Question.usage_count)