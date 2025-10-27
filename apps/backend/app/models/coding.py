"""
Coding challenge models for the PlacementPrep system.
"""
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class DifficultyLevel(enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class LanguageType(enum.Enum):
    PYTHON = "python"
    JAVA = "java"
    CPP = "cpp"
    JAVASCRIPT = "javascript"


class ExecutionStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    MEMORY_EXCEEDED = "memory_exceeded"


class CodingChallenge(Base):
    """Coding challenge problems."""
    __tablename__ = "coding_challenges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(SQLEnum(DifficultyLevel), nullable=False)
    category = Column(String(100), nullable=False)
    topic_tags = Column(ARRAY(String), default=[])
    company_tags = Column(ARRAY(String), default=[])
    
    # Problem constraints
    time_limit = Column(Integer, default=5000)  # milliseconds
    memory_limit = Column(Integer, default=256)  # MB
    
    # Template code for different languages
    template_code = Column(JSON, default={})  # {"python": "def solution():", "java": "class Solution {}"}
    
    # Solution and hints
    solution_approach = Column(Text)
    hints = Column(ARRAY(String), default=[])
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    test_cases = relationship("TestCase", back_populates="challenge", cascade="all, delete-orphan")
    submissions = relationship("CodeSubmission", back_populates="challenge")
    creator = relationship("User", foreign_keys=[created_by])


class TestCase(Base):
    """Test cases for coding challenges."""
    __tablename__ = "test_cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    challenge_id = Column(UUID(as_uuid=True), ForeignKey("coding_challenges.id"), nullable=False)
    
    # Test case data
    input_data = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    is_sample = Column(Boolean, default=False)  # Whether this is shown to users
    is_hidden = Column(Boolean, default=True)   # Whether this is used for final evaluation
    
    # Metadata
    weight = Column(Float, default=1.0)  # Weight for scoring
    explanation = Column(Text)  # Explanation for sample test cases
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    challenge = relationship("CodingChallenge", back_populates="test_cases")


class CodeSubmission(Base):
    """Code submissions for challenges."""
    __tablename__ = "code_submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    challenge_id = Column(UUID(as_uuid=True), ForeignKey("coding_challenges.id"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("test_sessions.id"), nullable=True)
    
    # Submission details
    language = Column(SQLEnum(LanguageType), nullable=False)
    code = Column(Text, nullable=False)
    
    # Execution results
    status = Column(SQLEnum(ExecutionStatus), default=ExecutionStatus.PENDING)
    score = Column(Float, default=0.0)
    total_test_cases = Column(Integer, default=0)
    passed_test_cases = Column(Integer, default=0)
    
    # Performance metrics
    execution_time = Column(Float)  # seconds
    memory_usage = Column(Float)    # MB
    
    # Detailed results
    test_results = Column(JSON, default=[])  # Array of test case results
    compilation_error = Column(Text)
    runtime_error = Column(Text)
    
    # Metadata
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    executed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User")
    challenge = relationship("CodingChallenge", back_populates="submissions")
    session = relationship("TestSession", foreign_keys=[session_id])


class CodeExecution(Base):
    """Individual code execution records for monitoring and debugging."""
    __tablename__ = "code_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("code_submissions.id"), nullable=False)
    
    # Execution environment
    container_id = Column(String(255))
    language = Column(SQLEnum(LanguageType), nullable=False)
    
    # Resource usage
    cpu_time = Column(Float)
    wall_time = Column(Float)
    memory_peak = Column(Float)
    
    # Security and limits
    security_violations = Column(JSON, default=[])
    resource_violations = Column(JSON, default=[])
    
    # Execution details
    stdout = Column(Text)
    stderr = Column(Text)
    exit_code = Column(Integer)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    submission = relationship("CodeSubmission")