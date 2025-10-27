"""
Pydantic schemas for coding challenge system.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum
import uuid


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class LanguageType(str, Enum):
    PYTHON = "python"
    JAVA = "java"
    CPP = "cpp"
    JAVASCRIPT = "javascript"


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    MEMORY_EXCEEDED = "memory_exceeded"


# Test Case Schemas
class TestCaseBase(BaseModel):
    input_data: str = Field(..., description="Input data for the test case")
    expected_output: str = Field(..., description="Expected output for the test case")
    is_sample: bool = Field(default=False, description="Whether this is a sample test case shown to users")
    is_hidden: bool = Field(default=True, description="Whether this is used for final evaluation")
    weight: float = Field(default=1.0, ge=0.0, description="Weight for scoring")
    explanation: Optional[str] = Field(None, description="Explanation for sample test cases")


class TestCaseCreate(TestCaseBase):
    pass


class TestCaseUpdate(BaseModel):
    input_data: Optional[str] = None
    expected_output: Optional[str] = None
    is_sample: Optional[bool] = None
    is_hidden: Optional[bool] = None
    weight: Optional[float] = Field(None, ge=0.0)
    explanation: Optional[str] = None


class TestCase(TestCaseBase):
    id: uuid.UUID
    challenge_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Coding Challenge Schemas
class CodingChallengeBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Challenge title")
    description: str = Field(..., min_length=1, description="Challenge description")
    difficulty: DifficultyLevel = Field(..., description="Difficulty level")
    category: str = Field(..., min_length=1, max_length=100, description="Challenge category")
    topic_tags: List[str] = Field(default=[], description="Topic tags for categorization")
    company_tags: List[str] = Field(default=[], description="Company tags")
    time_limit: int = Field(default=5000, ge=1000, le=30000, description="Time limit in milliseconds")
    memory_limit: int = Field(default=256, ge=64, le=1024, description="Memory limit in MB")
    template_code: Dict[str, str] = Field(default={}, description="Template code for different languages")
    solution_approach: Optional[str] = Field(None, description="Solution approach explanation")
    hints: List[str] = Field(default=[], description="Hints for solving the problem")
    is_active: bool = Field(default=True, description="Whether the challenge is active")


class CodingChallengeCreate(CodingChallengeBase):
    test_cases: List[TestCaseCreate] = Field(..., min_items=1, description="Test cases for the challenge")

    @validator('test_cases')
    def validate_test_cases(cls, v):
        if not any(tc.is_sample for tc in v):
            raise ValueError("At least one test case must be marked as sample")
        return v


class CodingChallengeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    difficulty: Optional[DifficultyLevel] = None
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    topic_tags: Optional[List[str]] = None
    company_tags: Optional[List[str]] = None
    time_limit: Optional[int] = Field(None, ge=1000, le=30000)
    memory_limit: Optional[int] = Field(None, ge=64, le=1024)
    template_code: Optional[Dict[str, str]] = None
    solution_approach: Optional[str] = None
    hints: Optional[List[str]] = None
    is_active: Optional[bool] = None


class CodingChallenge(CodingChallengeBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: uuid.UUID
    test_cases: List[TestCase] = []

    class Config:
        from_attributes = True


class CodingChallengeList(BaseModel):
    id: uuid.UUID
    title: str
    difficulty: DifficultyLevel
    category: str
    topic_tags: List[str]
    company_tags: List[str]
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# Code Submission Schemas
class CodeSubmissionBase(BaseModel):
    language: LanguageType = Field(..., description="Programming language")
    code: str = Field(..., min_length=1, description="Source code")


class CodeSubmissionCreate(CodeSubmissionBase):
    challenge_id: uuid.UUID = Field(..., description="Challenge ID")
    session_id: Optional[uuid.UUID] = Field(None, description="Optional test session ID")


class CodeSubmissionUpdate(BaseModel):
    status: Optional[ExecutionStatus] = None
    score: Optional[float] = Field(None, ge=0.0, le=100.0)
    total_test_cases: Optional[int] = Field(None, ge=0)
    passed_test_cases: Optional[int] = Field(None, ge=0)
    execution_time: Optional[float] = Field(None, ge=0.0)
    memory_usage: Optional[float] = Field(None, ge=0.0)
    test_results: Optional[List[Dict[str, Any]]] = None
    compilation_error: Optional[str] = None
    runtime_error: Optional[str] = None
    executed_at: Optional[datetime] = None


class TestCaseResult(BaseModel):
    test_case_id: uuid.UUID
    passed: bool
    execution_time: float
    memory_usage: float
    actual_output: Optional[str] = None
    error_message: Optional[str] = None


class CodeSubmission(CodeSubmissionBase):
    id: uuid.UUID
    user_id: uuid.UUID
    challenge_id: uuid.UUID
    session_id: Optional[uuid.UUID]
    status: ExecutionStatus
    score: float
    total_test_cases: int
    passed_test_cases: int
    execution_time: Optional[float]
    memory_usage: Optional[float]
    test_results: List[Dict[str, Any]]
    compilation_error: Optional[str]
    runtime_error: Optional[str]
    submitted_at: datetime
    executed_at: Optional[datetime]

    class Config:
        from_attributes = True


# Code Execution Schemas
class CodeExecutionResult(BaseModel):
    submission_id: uuid.UUID
    status: ExecutionStatus
    score: float
    total_test_cases: int
    passed_test_cases: int
    execution_time: Optional[float]
    memory_usage: Optional[float]
    test_results: List[TestCaseResult]
    compilation_error: Optional[str]
    runtime_error: Optional[str]


# Challenge Filters and Search
class CodingChallengeFilters(BaseModel):
    difficulty: Optional[List[DifficultyLevel]] = None
    category: Optional[List[str]] = None
    topic_tags: Optional[List[str]] = None
    company_tags: Optional[List[str]] = None
    is_active: Optional[bool] = True
    search: Optional[str] = Field(None, description="Search in title and description")
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class CodingChallengeSearchResult(BaseModel):
    challenges: List[CodingChallengeList]
    total: int
    limit: int
    offset: int


# Analytics Schemas
class CodingChallengeAnalytics(BaseModel):
    challenge_id: uuid.UUID
    title: str
    total_submissions: int
    successful_submissions: int
    average_score: float
    average_execution_time: Optional[float]
    difficulty_rating: float
    popular_languages: Dict[str, int]


class UserCodingStats(BaseModel):
    user_id: uuid.UUID
    total_submissions: int
    successful_submissions: int
    average_score: float
    challenges_solved: int
    favorite_language: Optional[str]
    difficulty_breakdown: Dict[str, int]
    recent_submissions: List[CodeSubmission]


# Bulk Operations
class BulkChallengeCreate(BaseModel):
    challenges: List[CodingChallengeCreate] = Field(..., min_items=1, max_items=50)


class BulkOperationResult(BaseModel):
    success_count: int
    error_count: int
    errors: List[Dict[str, Any]] = []
    created_ids: List[uuid.UUID] = []


# Code Quality Analysis
class CodeQualityMetrics(BaseModel):
    submission_id: uuid.UUID
    complexity_score: float
    readability_score: float
    efficiency_score: float
    best_practices_score: float
    suggestions: List[str]
    code_smells: List[str]


# Plagiarism Detection
class PlagiarismResult(BaseModel):
    submission_id: uuid.UUID
    similarity_score: float
    similar_submissions: List[Dict[str, Any]]
    is_suspicious: bool
    confidence_level: float