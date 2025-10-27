"""Resume analysis schemas."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field, validator


class ResumeSection(BaseModel):
    """Schema for resume sections."""
    type: str = Field(..., description="Section type (contact, summary, experience, etc.)")
    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content")
    items: Optional[List[Dict[str, Any]]] = Field(default=None, description="Structured items in section")


class ContactInfo(BaseModel):
    """Schema for contact information."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None


class WorkExperience(BaseModel):
    """Schema for work experience."""
    company: str
    position: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    location: Optional[str] = None
    description: List[str] = Field(default_factory=list)
    skills_used: List[str] = Field(default_factory=list)


class Education(BaseModel):
    """Schema for education."""
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = None
    achievements: List[str] = Field(default_factory=list)


class Skill(BaseModel):
    """Schema for skills."""
    name: str
    category: str = Field(..., description="technical, soft, language, etc.")
    proficiency: Optional[str] = None
    years_experience: Optional[int] = None


class StructuredResumeData(BaseModel):
    """Schema for structured resume data."""
    contact_info: ContactInfo
    summary: Optional[str] = None
    work_experience: List[WorkExperience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    skills: List[Skill] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    projects: List[Dict[str, Any]] = Field(default_factory=list)
    sections: List[ResumeSection] = Field(default_factory=list)


class ATSAnalysis(BaseModel):
    """Schema for ATS compatibility analysis."""
    overall_score: float = Field(..., ge=0, le=100, description="Overall ATS score (0-100)")
    keyword_score: float = Field(..., ge=0, le=100, description="Keyword optimization score")
    format_score: float = Field(..., ge=0, le=100, description="Format compatibility score")
    structure_score: float = Field(..., ge=0, le=100, description="Structure score")
    
    # Detailed analysis
    missing_keywords: List[str] = Field(default_factory=list)
    keyword_density: Dict[str, float] = Field(default_factory=dict)
    format_issues: List[str] = Field(default_factory=list)
    structure_issues: List[str] = Field(default_factory=list)
    
    # Recommendations
    keyword_suggestions: List[str] = Field(default_factory=list)
    format_recommendations: List[str] = Field(default_factory=list)
    structure_recommendations: List[str] = Field(default_factory=list)


class ContentAnalysis(BaseModel):
    """Schema for content quality analysis."""
    readability_score: float = Field(..., ge=0, le=100)
    grammar_score: float = Field(..., ge=0, le=100)
    impact_score: float = Field(..., ge=0, le=100)
    
    # Issues found
    grammar_issues: List[Dict[str, str]] = Field(default_factory=list)
    weak_phrases: List[str] = Field(default_factory=list)
    missing_metrics: List[str] = Field(default_factory=list)
    
    # Suggestions
    content_suggestions: List[Dict[str, str]] = Field(default_factory=list)
    rewrite_suggestions: List[Dict[str, str]] = Field(default_factory=list)


class ResumeAnalysisResult(BaseModel):
    """Schema for complete resume analysis result."""
    ats_analysis: ATSAnalysis
    content_analysis: ContentAnalysis
    overall_score: float = Field(..., ge=0, le=100)
    industry_match_score: Optional[float] = Field(default=None, ge=0, le=100)
    
    # Summary
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    priority_improvements: List[str] = Field(default_factory=list)


class ResumeUpload(BaseModel):
    """Schema for resume upload request."""
    filename: str = Field(..., min_length=1, max_length=255)
    file_size: float = Field(..., gt=0, description="File size in MB")
    file_type: str = Field(..., pattern=r"^(pdf|doc|docx)$")


class ResumeCreate(BaseModel):
    """Schema for creating a resume record."""
    filename: str
    file_path: str
    file_size: float
    file_type: str


class ResumeResponse(BaseModel):
    """Schema for resume response."""
    id: UUID
    user_id: UUID
    filename: str
    file_size: float
    file_type: str
    ats_score: Optional[float] = None
    processing_status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ResumeAnalysisResponse(BaseModel):
    """Schema for resume analysis response."""
    id: UUID
    filename: str
    ats_score: float
    analysis_results: ResumeAnalysisResult
    suggestions: List[Dict[str, Any]]
    processing_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ResumeVersionCreate(BaseModel):
    """Schema for creating a resume version."""
    resume_id: UUID
    version_number: float
    filename: str
    file_path: str
    changes_made: Optional[Dict[str, Any]] = None


class ResumeVersionResponse(BaseModel):
    """Schema for resume version response."""
    id: UUID
    resume_id: UUID
    version_number: float
    filename: str
    ats_score: Optional[float] = None
    changes_made: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ResumeTemplateResponse(BaseModel):
    """Schema for resume template response."""
    id: UUID
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    industry: Optional[str] = None
    preview_image: Optional[str] = None
    is_premium: bool
    popularity_score: float
    ats_friendly_score: float
    
    class Config:
        from_attributes = True


class ResumeOptimizationRequest(BaseModel):
    """Schema for resume optimization request."""
    resume_id: UUID
    target_role: Optional[str] = None
    target_company: Optional[str] = None
    industry: Optional[str] = None
    optimization_focus: List[str] = Field(default_factory=list, description="ats, content, keywords, format")


class ResumeComparisonRequest(BaseModel):
    """Schema for resume comparison request."""
    resume_ids: List[UUID] = Field(..., min_items=2, max_items=5)
    comparison_criteria: List[str] = Field(default_factory=list)


class ResumeComparisonResponse(BaseModel):
    """Schema for resume comparison response."""
    resumes: List[ResumeResponse]
    comparison_matrix: Dict[str, Dict[UUID, float]]
    recommendations: List[str]
    best_practices: List[str]