"""Resume analysis models."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Text, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Resume(Base):
    """Resume model for storing uploaded resumes and analysis results."""
    
    __tablename__ = "resumes"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Float, nullable=False)  # in MB
    file_type = Column(String(50), nullable=False)  # pdf, doc, docx
    
    # Extracted content
    raw_text = Column(Text)
    structured_data = Column(JSON)  # Parsed sections, contact info, etc.
    
    # Analysis results
    ats_score = Column(Float)  # 0-100 score
    analysis_results = Column(JSON)  # Detailed analysis data
    suggestions = Column(JSON)  # Improvement suggestions
    
    # Processing status
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    processing_error = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="resumes")
    versions = relationship("ResumeVersion", back_populates="resume", cascade="all, delete-orphan")


class ResumeVersion(Base):
    """Resume version model for tracking resume iterations."""
    
    __tablename__ = "resume_versions"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    resume_id = Column(PGUUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False)
    version_number = Column(Float, nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    
    # Version-specific analysis
    ats_score = Column(Float)
    analysis_results = Column(JSON)
    changes_made = Column(JSON)  # What was changed from previous version
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    resume = relationship("Resume", back_populates="versions")


class ResumeTemplate(Base):
    """Resume template model for professional templates."""
    
    __tablename__ = "resume_templates"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # modern, classic, creative, ats-friendly
    industry = Column(String(100))  # tech, finance, healthcare, etc.
    
    # Template data
    template_data = Column(JSON, nullable=False)  # Structure and styling
    preview_image = Column(String(500))  # URL to preview image
    
    # Metadata
    is_premium = Column(Boolean, default=False)
    popularity_score = Column(Float, default=0.0)
    ats_friendly_score = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class ResumeAnalysisJob(Base):
    """Background job tracking for resume analysis."""
    
    __tablename__ = "resume_analysis_jobs"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    resume_id = Column(PGUUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False)
    job_type = Column(String(50), nullable=False)  # parse, analyze, optimize
    status = Column(String(50), default="queued")  # queued, processing, completed, failed
    
    # Job details
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    result_data = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    resume = relationship("Resume")