from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum

from app.models.interview import InterviewType, InterviewStatus, QuestionCategory, DifficultyLevel


class InterviewSessionCreate(BaseModel):
    """Schema for creating interview sessions."""
    interview_type: InterviewType
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    company_name: Optional[str] = Field(None, max_length=200)
    position_title: Optional[str] = Field(None, max_length=200)
    
    total_duration: int = Field(..., ge=5, le=180)  # 5 minutes to 3 hours
    question_count: int = Field(10, ge=1, le=50)
    difficulty_level: DifficultyLevel = DifficultyLevel.MEDIUM
    
    adaptive_mode: bool = True
    performance_threshold: float = Field(0.7, ge=0.1, le=1.0)
    
    question_categories: List[QuestionCategory]
    company_tags: Optional[List[str]] = Field(None, max_items=10)
    topic_tags: Optional[List[str]] = Field(None, max_items=20)
    
    enable_video_recording: bool = True
    enable_audio_recording: bool = True
    
    scheduled_time: Optional[datetime] = None
    
    @validator('question_categories')
    def validate_categories(cls, v):
        if not v:
            raise ValueError('At least one question category must be specified')
        return v


class InterviewSessionUpdate(BaseModel):
    """Schema for updating interview sessions."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    company_name: Optional[str] = Field(None, max_length=200)
    position_title: Optional[str] = Field(None, max_length=200)
    
    total_duration: Optional[int] = Field(None, ge=5, le=180)
    question_count: Optional[int] = Field(None, ge=1, le=50)
    difficulty_level: Optional[DifficultyLevel] = None
    
    adaptive_mode: Optional[bool] = None
    performance_threshold: Optional[float] = Field(None, ge=0.1, le=1.0)
    
    question_categories: Optional[List[QuestionCategory]] = None
    company_tags: Optional[List[str]] = Field(None, max_items=10)
    topic_tags: Optional[List[str]] = Field(None, max_items=20)
    
    enable_video_recording: Optional[bool] = None
    enable_audio_recording: Optional[bool] = None
    
    scheduled_time: Optional[datetime] = None


class InterviewSessionResponse(BaseModel):
    """Schema for interview session responses."""
    id: UUID
    user_id: UUID
    interview_type: InterviewType
    title: str
    description: Optional[str]
    company_name: Optional[str]
    position_title: Optional[str]
    
    total_duration: int
    question_count: int
    difficulty_level: DifficultyLevel
    
    adaptive_mode: bool
    performance_threshold: float
    
    question_categories: List[QuestionCategory]
    company_tags: Optional[List[str]]
    topic_tags: Optional[List[str]]
    
    status: InterviewStatus
    current_question_index: int
    questions_asked: List[UUID]
    
    scheduled_time: Optional[datetime]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    total_pause_duration: int
    
    enable_video_recording: bool
    enable_audio_recording: bool
    video_file_url: Optional[str]
    audio_file_url: Optional[str]
    
    overall_score: Optional[float]
    communication_score: Optional[float]
    technical_score: Optional[float]
    behavioral_score: Optional[float]
    
    ai_feedback: Dict[str, Any]
    performance_analysis: Dict[str, Any]
    improvement_suggestions: List[str]
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InterviewQuestionCreate(BaseModel):
    """Schema for creating interview questions."""
    question_text: str = Field(..., min_length=10, max_length=5000)
    category: QuestionCategory
    difficulty_level: DifficultyLevel
    expected_duration: int = Field(..., ge=30, le=1800)  # 30 seconds to 30 minutes
    
    question_order: int = Field(..., ge=1)
    is_followup: bool = False
    parent_question_id: Optional[UUID] = None
    
    context_information: Optional[str] = Field(None, max_length=2000)
    evaluation_criteria: List[str] = Field(default_factory=list, max_items=10)
    sample_answers: List[str] = Field(default_factory=list, max_items=5)
    
    generation_prompt: Optional[str] = Field(None, max_length=2000)
    generation_context: Dict[str, Any] = Field(default_factory=dict)


class InterviewQuestionResponse(BaseModel):
    """Schema for interview question responses."""
    id: UUID
    session_id: UUID
    question_text: str
    category: QuestionCategory
    difficulty_level: DifficultyLevel
    expected_duration: int
    
    question_order: int
    is_followup: bool
    parent_question_id: Optional[UUID]
    
    generated_by_ai: bool
    generation_prompt: Optional[str]
    generation_context: Dict[str, Any]
    
    context_information: Optional[str]
    evaluation_criteria: List[str]
    sample_answers: List[str]
    
    difficulty_adjustment: Optional[float]
    
    created_at: datetime
    asked_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class InterviewResponseCreate(BaseModel):
    """Schema for creating interview responses."""
    response_text: Optional[str] = Field(None, max_length=10000)
    response_duration: int = Field(..., ge=1)  # Duration in seconds
    thinking_time: int = Field(0, ge=0)
    
    # File uploads will be handled separately
    audio_file_url: Optional[str] = None
    video_file_url: Optional[str] = None


class InterviewResponseUpdate(BaseModel):
    """Schema for updating interview responses with analysis."""
    transcript_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0)
    confidence_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    speech_pace: Optional[float] = Field(None, ge=0.0)
    filler_word_count: int = Field(0, ge=0)
    pause_count: int = Field(0, ge=0)
    volume_consistency: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    content_relevance: Optional[float] = Field(None, ge=0.0, le=1.0)
    technical_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0)
    structure_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    overall_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    communication_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    content_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    
    ai_feedback: Optional[str] = Field(None, max_length=5000)
    improvement_suggestions: List[str] = Field(default_factory=list, max_items=10)
    strengths: List[str] = Field(default_factory=list, max_items=10)
    weaknesses: List[str] = Field(default_factory=list, max_items=10)
    
    analysis_version: Optional[str] = Field(None, max_length=50)
    processing_time: Optional[float] = Field(None, ge=0.0)


class InterviewResponseResponse(BaseModel):
    """Schema for interview response responses."""
    id: UUID
    session_id: UUID
    question_id: UUID
    
    response_text: Optional[str]
    audio_file_url: Optional[str]
    video_file_url: Optional[str]
    
    response_duration: int
    thinking_time: int
    
    transcript_confidence: Optional[float]
    sentiment_score: Optional[float]
    confidence_level: Optional[float]
    
    speech_pace: Optional[float]
    filler_word_count: int
    pause_count: int
    volume_consistency: Optional[float]
    
    content_relevance: Optional[float]
    technical_accuracy: Optional[float]
    structure_score: Optional[float]
    
    overall_score: Optional[float]
    communication_score: Optional[float]
    content_score: Optional[float]
    
    ai_feedback: Optional[str]
    improvement_suggestions: List[str]
    strengths: List[str]
    weaknesses: List[str]
    
    analysis_version: Optional[str]
    processing_time: Optional[float]
    
    created_at: datetime
    analyzed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class InterviewSessionSummary(BaseModel):
    """Schema for interview session summary."""
    id: UUID
    title: str
    interview_type: InterviewType
    company_name: Optional[str]
    position_title: Optional[str]
    status: InterviewStatus
    
    total_duration: int
    actual_duration: Optional[float]  # in minutes
    question_count: int
    questions_answered: int
    
    overall_score: Optional[float]
    communication_score: Optional[float]
    technical_score: Optional[float]
    behavioral_score: Optional[float]
    
    created_at: datetime
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    
    class Config:
        from_attributes = True


class InterviewAnalytics(BaseModel):
    """Schema for interview analytics."""
    total_interviews: int
    completed_interviews: int
    average_score: Optional[float]
    average_duration: Optional[float]  # in minutes
    
    score_distribution: Dict[str, int]  # Score ranges and counts
    category_performance: Dict[QuestionCategory, float]  # Average scores by category
    improvement_trends: List[Dict[str, Any]]  # Time-series data
    
    strengths: List[str]
    areas_for_improvement: List[str]
    recommendations: List[str]


class QuestionGenerationRequest(BaseModel):
    """Schema for AI question generation requests."""
    interview_type: InterviewType
    category: QuestionCategory
    difficulty_level: DifficultyLevel
    company_name: Optional[str] = None
    position_title: Optional[str] = None
    topic_tags: Optional[List[str]] = Field(None, max_items=10)
    
    previous_questions: Optional[List[str]] = Field(None, max_items=20)
    user_performance: Optional[Dict[str, float]] = None
    context: Optional[str] = Field(None, max_length=1000)
    
    count: int = Field(1, ge=1, le=10)


class QuestionGenerationResponse(BaseModel):
    """Schema for AI question generation responses."""
    questions: List[Dict[str, Any]]
    generation_metadata: Dict[str, Any]
    processing_time: float