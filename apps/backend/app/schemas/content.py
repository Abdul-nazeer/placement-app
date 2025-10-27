from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from uuid import UUID
from enum import Enum

from app.models.question import QuestionType, DifficultyLevel, QuestionStatus
from app.models.session import TestType, SessionStatus
from app.models.submission import SubmissionType, SubmissionStatus
from app.models.content import CategoryType


# Base schemas
class TimestampMixin(BaseModel):
    created_at: datetime
    updated_at: datetime


# Category schemas
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    type: CategoryType
    parent_id: Optional[UUID] = None
    level: int = Field(default=0, ge=0)
    sort_order: int = Field(default=0, ge=0)
    icon: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    sort_order: Optional[int] = Field(None, ge=0)
    icon: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    is_active: Optional[bool] = None


class Category(CategoryBase, TimestampMixin):
    id: UUID
    question_count: int = 0
    children: List['Category'] = []

    class Config:
        from_attributes = True


# Tag schemas
class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    type: str = Field(..., min_length=1, max_length=50)
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    is_active: bool = True


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    is_active: Optional[bool] = None


class Tag(TagBase, TimestampMixin):
    id: UUID
    usage_count: int = 0

    class Config:
        from_attributes = True


# Company schemas
class CompanyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    industry: Optional[str] = Field(None, max_length=100)
    size: Optional[str] = Field(None, max_length=50)
    headquarters: Optional[str] = Field(None, max_length=200)
    website: Optional[str] = Field(None, max_length=500)
    logo_url: Optional[str] = Field(None, max_length=500)
    is_active: bool = True
    is_featured: bool = False


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    industry: Optional[str] = Field(None, max_length=100)
    size: Optional[str] = Field(None, max_length=50)
    headquarters: Optional[str] = Field(None, max_length=200)
    website: Optional[str] = Field(None, max_length=500)
    logo_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None


class Company(CompanyBase, TimestampMixin):
    id: UUID
    question_count: int = 0
    popularity_score: int = 0

    class Config:
        from_attributes = True


# Question Collection schemas
class QuestionCollectionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    type: str = Field(..., min_length=1, max_length=50)
    difficulty_level: Optional[int] = Field(None, ge=1, le=5)
    estimated_time: Optional[int] = Field(None, gt=0)  # minutes
    company_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    is_public: bool = True
    is_premium: bool = False
    is_active: bool = True


class QuestionCollectionCreate(QuestionCollectionBase):
    created_by: Optional[UUID] = None


class QuestionCollectionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    difficulty_level: Optional[int] = Field(None, ge=1, le=5)
    estimated_time: Optional[int] = Field(None, gt=0)
    company_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    is_public: Optional[bool] = None
    is_premium: Optional[bool] = None
    is_active: Optional[bool] = None


class QuestionCollection(QuestionCollectionBase, TimestampMixin):
    id: UUID
    question_count: int = 0
    usage_count: int = 0
    average_score: Optional[int] = None
    created_by: Optional[UUID] = None
    company: Optional[Company] = None
    category: Optional[Category] = None

    class Config:
        from_attributes = True


# Enhanced Question schemas
class QuestionBase(BaseModel):
    type: QuestionType
    category: str = Field(..., min_length=1, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    difficulty: DifficultyLevel
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    options: Optional[List[str]] = None
    correct_answer: str = Field(..., min_length=1)
    explanation: Optional[str] = None
    hints: Optional[List[str]] = None
    company_tags: List[str] = []
    topic_tags: List[str] = []
    skill_tags: List[str] = []
    extra_data: Dict[str, Any] = {}
    is_premium: bool = False

    @validator('options')
    def validate_options(cls, v, values):
        if values.get('type') in [QuestionType.APTITUDE] and v is None:
            raise ValueError('Options are required for aptitude questions')
        return v


class QuestionCreate(QuestionBase):
    status: QuestionStatus = QuestionStatus.DRAFT
    created_by: Optional[UUID] = None


class QuestionUpdate(BaseModel):
    type: Optional[QuestionType] = None
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    difficulty: Optional[DifficultyLevel] = None
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = Field(None, min_length=1)
    explanation: Optional[str] = None
    hints: Optional[List[str]] = None
    company_tags: Optional[List[str]] = None
    topic_tags: Optional[List[str]] = None
    skill_tags: Optional[List[str]] = None
    extra_data: Optional[Dict[str, Any]] = None
    status: Optional[QuestionStatus] = None
    is_premium: Optional[bool] = None


class Question(QuestionBase, TimestampMixin):
    id: UUID
    status: QuestionStatus
    version: int = 1
    parent_question_id: Optional[UUID] = None
    usage_count: int = 0
    success_rate: Optional[float] = None
    average_time: Optional[float] = None
    created_by: Optional[UUID] = None
    reviewed_by: Optional[UUID] = None
    is_active: bool = True
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Enhanced Test Session schemas
class TestSessionBase(BaseModel):
    test_type: TestType
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = Field(None, max_length=1000)
    configuration: Dict[str, Any] = {}
    time_limit: Optional[int] = Field(None, gt=0)  # seconds
    time_per_question: Optional[int] = Field(None, gt=0)  # seconds
    allow_review: bool = True
    show_results: bool = True
    randomize_questions: bool = False
    randomize_options: bool = False
    categories: Optional[List[str]] = None
    difficulty_levels: Optional[List[int]] = None
    company_tags: Optional[List[str]] = None
    topic_tags: Optional[List[str]] = None
    extra_data: Dict[str, Any] = {}


class TestSessionCreate(TestSessionBase):
    question_ids: List[UUID] = []


class TestSessionUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = Field(None, max_length=1000)
    current_question_index: Optional[int] = Field(None, ge=0)
    status: Optional[SessionStatus] = None
    pause_time: Optional[datetime] = None
    total_pause_duration: Optional[int] = Field(None, ge=0)


class TestSession(TestSessionBase, TimestampMixin):
    id: UUID
    user_id: UUID
    question_ids: List[UUID] = []
    current_question_index: int = 0
    total_questions: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    pause_time: Optional[datetime] = None
    total_pause_duration: int = 0
    status: SessionStatus = SessionStatus.CREATED
    score: Optional[float] = None
    max_score: Optional[float] = None
    percentage: Optional[float] = None
    correct_answers: int = 0
    incorrect_answers: int = 0
    skipped_answers: int = 0
    total_time_taken: Optional[int] = None

    class Config:
        from_attributes = True


# Enhanced Submission schemas
class SubmissionBase(BaseModel):
    submission_type: SubmissionType
    user_answer: str = Field(..., min_length=1)
    time_taken: int = Field(..., gt=0)  # seconds
    time_limit: Optional[int] = Field(None, gt=0)
    extra_data: Dict[str, Any] = {}


class SubmissionCreate(SubmissionBase):
    session_id: UUID
    question_id: UUID


class SubmissionUpdate(BaseModel):
    is_correct: Optional[bool] = None
    score: Optional[float] = Field(None, ge=0)
    max_score: Optional[float] = Field(None, ge=0)
    status: Optional[SubmissionStatus] = None
    feedback: Optional[str] = None
    detailed_analysis: Optional[Dict[str, Any]] = None
    evaluated_by: Optional[str] = None
    evaluation_time: Optional[float] = Field(None, ge=0)


class Submission(SubmissionBase, TimestampMixin):
    id: UUID
    user_id: UUID
    session_id: UUID
    question_id: UUID
    is_correct: Optional[bool] = None
    score: Optional[float] = None
    max_score: Optional[float] = None
    status: SubmissionStatus = SubmissionStatus.SUBMITTED
    evaluation_attempts: int = 0
    feedback: Optional[str] = None
    detailed_analysis: Dict[str, Any] = {}
    evaluated_by: Optional[str] = None
    evaluation_time: Optional[float] = None
    submitted_at: datetime
    evaluated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Search and filtering schemas
class QuestionFilters(BaseModel):
    type: Optional[QuestionType] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    difficulty: Optional[List[DifficultyLevel]] = None
    company_tags: Optional[List[str]] = None
    topic_tags: Optional[List[str]] = None
    skill_tags: Optional[List[str]] = None
    status: Optional[List[QuestionStatus]] = None
    is_active: Optional[bool] = None
    is_premium: Optional[bool] = None
    search: Optional[str] = None  # Full-text search
    created_by: Optional[UUID] = None
    min_success_rate: Optional[float] = Field(None, ge=0, le=100)
    max_success_rate: Optional[float] = Field(None, ge=0, le=100)
    min_usage_count: Optional[int] = Field(None, ge=0)


class QuestionSearchResult(BaseModel):
    questions: List[Question]
    total: int
    page: int
    size: int
    pages: int


# Bulk operations schemas
class BulkQuestionCreate(BaseModel):
    questions: List[QuestionCreate]


class BulkQuestionUpdate(BaseModel):
    question_ids: List[UUID]
    updates: QuestionUpdate


class BulkOperationResult(BaseModel):
    success_count: int
    error_count: int
    errors: List[Dict[str, Any]] = []


# Analytics schemas
class QuestionAnalytics(BaseModel):
    question_id: UUID
    usage_count: int
    success_rate: Optional[float]
    average_time: Optional[float]
    difficulty_rating: Optional[float]
    user_feedback_score: Optional[float]


class ContentAnalytics(BaseModel):
    total_questions: int
    questions_by_type: Dict[str, int]
    questions_by_difficulty: Dict[str, int]
    questions_by_status: Dict[str, int]
    top_companies: List[Dict[str, Union[str, int]]]
    top_topics: List[Dict[str, Union[str, int]]]
    average_success_rate: Optional[float]
    total_submissions: int


# Update forward references
Category.model_rebuild()