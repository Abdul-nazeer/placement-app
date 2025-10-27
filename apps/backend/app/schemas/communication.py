"""Communication assessment schemas."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class CommunicationPromptBase(BaseModel):
    """Base schema for communication prompts."""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    prompt_text: str = Field(..., min_length=1)
    category: str = Field(..., pattern="^(hr_interview|behavioral|presentation)$")
    difficulty_level: int = Field(..., ge=1, le=5)
    time_limit: Optional[int] = Field(None, ge=30, le=1800)  # 30 seconds to 30 minutes
    evaluation_criteria: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class CommunicationPromptCreate(CommunicationPromptBase):
    """Schema for creating communication prompts."""
    pass


class CommunicationPromptUpdate(BaseModel):
    """Schema for updating communication prompts."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    prompt_text: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, pattern="^(hr_interview|behavioral|presentation)$")
    difficulty_level: Optional[int] = Field(None, ge=1, le=5)
    time_limit: Optional[int] = Field(None, ge=30, le=1800)
    evaluation_criteria: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    is_active: Optional[str] = Field(None, pattern="^(true|false)$")


class CommunicationPrompt(CommunicationPromptBase):
    """Schema for communication prompt response."""
    id: UUID
    is_active: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommunicationSessionCreate(BaseModel):
    """Schema for creating communication sessions."""
    session_type: str = Field(..., pattern="^(hr_interview|behavioral|presentation)$")
    prompt_id: Optional[UUID] = None


class CommunicationSessionUpdate(BaseModel):
    """Schema for updating communication sessions."""
    status: Optional[str] = Field(None, pattern="^(active|completed|abandoned)$")
    overall_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    feedback: Optional[str] = None


class CommunicationSession(BaseModel):
    """Schema for communication session response."""
    id: UUID
    user_id: UUID
    session_type: str
    prompt_id: Optional[UUID]
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    overall_score: Optional[float]
    feedback: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommunicationSessionWithPrompt(CommunicationSession):
    """Communication session with prompt details."""
    prompt: Optional[CommunicationPrompt] = None


class AudioUploadRequest(BaseModel):
    """Schema for audio upload metadata."""
    session_id: UUID
    duration: Optional[float] = Field(None, ge=0.1, le=1800)  # 0.1 seconds to 30 minutes


class CommunicationRecording(BaseModel):
    """Schema for communication recording response."""
    id: UUID
    session_id: UUID
    audio_file_path: str
    duration: Optional[float]
    file_size: Optional[int]
    transcript: Optional[str]
    confidence_score: Optional[float]
    processing_status: str
    analysis_results: Optional[Dict] = None
    created_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True


class SpeechMetrics(BaseModel):
    """Schema for speech analysis metrics."""
    words_per_minute: Optional[float] = Field(None, ge=0)
    pause_frequency: Optional[float] = Field(None, ge=0)
    average_pause_duration: Optional[float] = Field(None, ge=0)
    filler_word_count: Optional[int] = Field(None, ge=0)
    filler_word_percentage: Optional[float] = Field(None, ge=0, le=100)


class LanguageMetrics(BaseModel):
    """Schema for language analysis metrics."""
    grammar_score: Optional[float] = Field(None, ge=0, le=1)
    vocabulary_complexity: Optional[float] = Field(None, ge=0, le=1)
    sentence_structure_score: Optional[float] = Field(None, ge=0, le=1)
    clarity_score: Optional[float] = Field(None, ge=0, le=1)


class ContentMetrics(BaseModel):
    """Schema for content analysis metrics."""
    relevance_score: Optional[float] = Field(None, ge=0, le=1)
    completeness_score: Optional[float] = Field(None, ge=0, le=1)
    coherence_score: Optional[float] = Field(None, ge=0, le=1)


class CommunicationAnalysisCreate(BaseModel):
    """Schema for creating communication analysis."""
    recording_id: UUID
    speech_metrics: Optional[SpeechMetrics] = None
    language_metrics: Optional[LanguageMetrics] = None
    content_metrics: Optional[ContentMetrics] = None
    fluency_score: Optional[float] = Field(None, ge=0, le=1)
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    overall_score: Optional[float] = Field(None, ge=0, le=1)
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None
    filler_words_detected: Optional[List[Dict]] = None


class CommunicationAnalysis(BaseModel):
    """Schema for communication analysis response."""
    id: UUID
    recording_id: UUID
    
    # Speech metrics
    words_per_minute: Optional[float]
    pause_frequency: Optional[float]
    average_pause_duration: Optional[float]
    filler_word_count: Optional[int]
    filler_word_percentage: Optional[float]
    
    # Language metrics
    grammar_score: Optional[float]
    vocabulary_complexity: Optional[float]
    sentence_structure_score: Optional[float]
    clarity_score: Optional[float]
    
    # Content metrics
    relevance_score: Optional[float]
    completeness_score: Optional[float]
    coherence_score: Optional[float]
    
    # Overall metrics
    fluency_score: Optional[float]
    confidence_score: Optional[float]
    overall_score: Optional[float]
    
    # Detailed analysis
    strengths: Optional[List[str]]
    weaknesses: Optional[List[str]]
    suggestions: Optional[List[str]]
    filler_words_detected: Optional[List[Dict]]
    
    created_at: datetime

    class Config:
        from_attributes = True


class CommunicationProgress(BaseModel):
    """Schema for communication progress response."""
    id: UUID
    user_id: UUID
    skill_category: str
    current_level: float
    sessions_completed: int
    total_practice_time: int
    last_session_date: Optional[datetime]
    improvement_rate: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommunicationProgressUpdate(BaseModel):
    """Schema for updating communication progress."""
    current_level: Optional[float] = Field(None, ge=0, le=1)
    sessions_completed: Optional[int] = Field(None, ge=0)
    total_practice_time: Optional[int] = Field(None, ge=0)
    improvement_rate: Optional[float] = None


class CommunicationFeedback(BaseModel):
    """Schema for comprehensive communication feedback."""
    session_id: UUID
    overall_score: float = Field(..., ge=0, le=1)
    analysis: CommunicationAnalysis
    recording: CommunicationRecording
    recommendations: List[str]
    next_steps: List[str]
    progress_comparison: Optional[Dict] = None


class CommunicationDashboard(BaseModel):
    """Schema for communication dashboard data."""
    user_id: UUID
    total_sessions: int
    total_practice_time: int  # seconds
    average_score: Optional[float]
    skill_progress: List[CommunicationProgress]
    recent_sessions: List[CommunicationSession]
    strengths: List[str]
    areas_for_improvement: List[str]
    recommended_exercises: List[str]