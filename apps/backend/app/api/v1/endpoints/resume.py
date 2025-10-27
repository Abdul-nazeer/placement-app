"""Resume analysis API endpoints."""

import os
import tempfile
import logging
from typing import List, Optional
from uuid import UUID
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.models.resume import Resume, ResumeVersion, ResumeTemplate
from app.schemas.resume import (
    ResumeResponse, ResumeAnalysisResponse, ResumeVersionResponse,
    ResumeTemplateResponse, ResumeOptimizationRequest, ResumeComparisonRequest,
    ResumeComparisonResponse
)
from app.services.resume_processing import ResumeProcessor
from app.services.ats_analyzer import ATSCompatibilityAnalyzer
from app.services.skill_extraction import SkillExtractor

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
resume_processor = ResumeProcessor()
ats_analyzer = ATSCompatibilityAnalyzer()
skill_extractor = SkillExtractor()

# File upload configuration
ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    target_role: Optional[str] = Form(None),
    target_industry: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and process a resume file."""
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file_ext} not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
    
    try:
        # Create resume record
        resume = Resume(
            user_id=current_user.id,
            filename=file.filename,
            file_path="",  # Will be set after saving file
            file_size=len(file_content) / (1024 * 1024),  # Convert to MB
            file_type=file_ext[1:],  # Remove the dot
            processing_status="pending"
        )
        
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        # Save file to storage
        upload_dir = Path("uploads/resumes")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / f"{resume.id}_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Update file path in database
        resume.file_path = str(file_path)
        db.commit()
        
        # Queue background processing
        background_tasks.add_task(
            process_resume_analysis,
            resume.id,
            str(file_path),
            file_ext[1:],
            target_role,
            target_industry,
            db
        )
        
        return ResumeResponse.from_orm(resume)
        
    except Exception as e:
        logger.error(f"Error uploading resume: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to upload resume")


@router.get("/", response_model=List[ResumeResponse])
async def get_user_resumes(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's uploaded resumes."""
    
    resumes = db.query(Resume).filter(
        Resume.user_id == current_user.id,
        Resume.is_active == True
    ).order_by(desc(Resume.created_at)).offset(skip).limit(limit).all()
    
    return [ResumeResponse.from_orm(resume) for resume in resumes]


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific resume."""
    
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id,
        Resume.is_active == True
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return ResumeResponse.from_orm(resume)


@router.get("/{resume_id}/analysis", response_model=ResumeAnalysisResponse)
async def get_resume_analysis(
    resume_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed resume analysis results."""
    
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id,
        Resume.is_active == True
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    if resume.processing_status != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Resume analysis not ready. Status: {resume.processing_status}"
        )
    
    return ResumeAnalysisResponse(
        id=resume.id,
        filename=resume.filename,
        ats_score=resume.ats_score or 0,
        analysis_results=resume.analysis_results,
        suggestions=resume.suggestions or [],
        processing_status=resume.processing_status,
        created_at=resume.created_at
    )


@router.post("/{resume_id}/reanalyze")
async def reanalyze_resume(
    resume_id: UUID,
    background_tasks: BackgroundTasks,
    target_role: Optional[str] = Form(None),
    target_industry: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reanalyze an existing resume with new parameters."""
    
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id,
        Resume.is_active == True
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Update processing status
    resume.processing_status = "pending"
    db.commit()
    
    # Queue reanalysis
    background_tasks.add_task(
        process_resume_analysis,
        resume.id,
        resume.file_path,
        resume.file_type,
        target_role,
        target_industry,
        db
    )
    
    return {"message": "Resume reanalysis queued", "resume_id": resume_id}


@router.post("/optimize", response_model=ResumeAnalysisResponse)
async def optimize_resume(
    request: ResumeOptimizationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get optimization recommendations for a resume."""
    
    resume = db.query(Resume).filter(
        Resume.id == request.resume_id,
        Resume.user_id == current_user.id,
        Resume.is_active == True
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    if not resume.structured_data:
        raise HTTPException(status_code=400, detail="Resume not yet processed")
    
    try:
        # Generate optimization recommendations
        optimization_results = await generate_optimization_recommendations(
            resume, request.target_role, request.target_company, 
            request.industry, request.optimization_focus
        )
        
        # Update resume with optimization results
        resume.suggestions = optimization_results.get("suggestions", [])
        db.commit()
        
        return ResumeAnalysisResponse(
            id=resume.id,
            filename=resume.filename,
            ats_score=resume.ats_score or 0,
            analysis_results=optimization_results,
            suggestions=resume.suggestions,
            processing_status=resume.processing_status,
            created_at=resume.created_at
        )
        
    except Exception as e:
        logger.error(f"Error optimizing resume: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to optimize resume")


@router.post("/compare", response_model=ResumeComparisonResponse)
async def compare_resumes(
    request: ResumeComparisonRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Compare multiple resumes and provide benchmarking insights."""
    
    # Validate resume ownership
    resumes = db.query(Resume).filter(
        Resume.id.in_(request.resume_ids),
        Resume.user_id == current_user.id,
        Resume.is_active == True
    ).all()
    
    if len(resumes) != len(request.resume_ids):
        raise HTTPException(status_code=404, detail="One or more resumes not found")
    
    # Check all resumes are processed
    unprocessed = [r for r in resumes if r.processing_status != "completed"]
    if unprocessed:
        raise HTTPException(
            status_code=400, 
            detail=f"Some resumes are not yet processed: {[r.filename for r in unprocessed]}"
        )
    
    try:
        # Generate comparison analysis
        comparison_results = await generate_resume_comparison(resumes, request.comparison_criteria)
        
        return ResumeComparisonResponse(
            resumes=[ResumeResponse.from_orm(r) for r in resumes],
            comparison_matrix=comparison_results["comparison_matrix"],
            recommendations=comparison_results["recommendations"],
            best_practices=comparison_results["best_practices"]
        )
        
    except Exception as e:
        logger.error(f"Error comparing resumes: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to compare resumes")


@router.get("/templates/", response_model=List[ResumeTemplateResponse])
async def get_resume_templates(
    category: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    ats_friendly: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get available resume templates."""
    
    query = db.query(ResumeTemplate).filter(ResumeTemplate.is_active == True)
    
    if category:
        query = query.filter(ResumeTemplate.category == category)
    if industry:
        query = query.filter(ResumeTemplate.industry == industry)
    if ats_friendly is not None:
        score_threshold = 80.0 if ats_friendly else 0.0
        query = query.filter(ResumeTemplate.ats_friendly_score >= score_threshold)
    
    templates = query.order_by(desc(ResumeTemplate.popularity_score)).offset(skip).limit(limit).all()
    
    return [ResumeTemplateResponse.from_orm(template) for template in templates]


@router.get("/{resume_id}/versions", response_model=List[ResumeVersionResponse])
async def get_resume_versions(
    resume_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all versions of a resume."""
    
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id,
        Resume.is_active == True
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    versions = db.query(ResumeVersion).filter(
        ResumeVersion.resume_id == resume_id
    ).order_by(desc(ResumeVersion.version_number)).all()
    
    return [ResumeVersionResponse.from_orm(version) for version in versions]


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a resume (soft delete)."""
    
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id,
        Resume.is_active == True
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Soft delete
    resume.is_active = False
    db.commit()
    
    return {"message": "Resume deleted successfully"}


# Background processing functions

async def process_resume_analysis(
    resume_id: UUID,
    file_path: str,
    file_type: str,
    target_role: Optional[str],
    target_industry: Optional[str],
    db: Session
):
    """Background task to process resume analysis."""
    
    try:
        # Update status to processing
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            return
        
        resume.processing_status = "processing"
        db.commit()
        
        # Extract text from file
        raw_text = await resume_processor.extract_text_from_file(file_path, file_type)
        
        # Parse structured data
        structured_data = resume_processor.parse_resume_structure(raw_text)
        
        # Perform ATS analysis
        ats_analysis = ats_analyzer.analyze_ats_compatibility(
            structured_data, raw_text, target_industry, target_role
        )
        
        # Perform content analysis
        content_analysis = resume_processor.analyze_content_quality(structured_data)
        
        # Generate complete analysis
        complete_analysis = await resume_processor.generate_complete_analysis(
            structured_data, target_role
        )
        
        # Extract skills
        extracted_skills = skill_extractor.extract_skills(raw_text)
        
        # Generate suggestions
        suggestions = await generate_improvement_suggestions(
            complete_analysis, extracted_skills, target_role, target_industry
        )
        
        # Update resume with results
        resume.raw_text = raw_text
        resume.structured_data = structured_data.dict()
        resume.ats_score = complete_analysis.overall_score
        resume.analysis_results = complete_analysis.dict()
        resume.suggestions = suggestions
        resume.processing_status = "completed"
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Error processing resume {resume_id}: {str(e)}")
        
        # Update status to failed
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if resume:
            resume.processing_status = "failed"
            resume.processing_error = str(e)
            db.commit()


async def generate_optimization_recommendations(
    resume: Resume,
    target_role: Optional[str],
    target_company: Optional[str],
    industry: Optional[str],
    optimization_focus: List[str]
) -> dict:
    """Generate optimization recommendations for a resume."""
    
    structured_data = resume.structured_data
    raw_text = resume.raw_text
    
    recommendations = {
        "ats_optimization": [],
        "content_optimization": [],
        "keyword_optimization": [],
        "format_optimization": [],
        "industry_specific": []
    }
    
    # ATS optimization
    if "ats" in optimization_focus or not optimization_focus:
        ats_analysis = ats_analyzer.analyze_ats_compatibility(
            structured_data, raw_text, industry, target_role
        )
        recommendations["ats_optimization"] = ats_analysis.format_recommendations + ats_analysis.structure_recommendations
    
    # Keyword optimization
    if "keywords" in optimization_focus or not optimization_focus:
        extracted_skills = skill_extractor.extract_skills(raw_text)
        skill_suggestions = skill_extractor.suggest_skill_improvements(extracted_skills, target_role)
        recommendations["keyword_optimization"] = [s["suggestion"] for s in skill_suggestions]
    
    # Content optimization
    if "content" in optimization_focus or not optimization_focus:
        content_analysis = resume_processor.analyze_content_quality(structured_data)
        recommendations["content_optimization"] = [s["suggestion"] for s in content_analysis.content_suggestions]
    
    # Industry-specific recommendations
    if industry:
        industry_recommendations = await generate_industry_specific_recommendations(
            structured_data, industry, target_role
        )
        recommendations["industry_specific"] = industry_recommendations
    
    return {
        "recommendations": recommendations,
        "priority_score": calculate_priority_scores(recommendations),
        "estimated_improvement": estimate_score_improvement(recommendations)
    }


async def generate_resume_comparison(resumes: List[Resume], criteria: List[str]) -> dict:
    """Generate comparison analysis between multiple resumes."""
    
    comparison_matrix = {}
    
    # Default criteria if none provided
    if not criteria:
        criteria = ["ats_score", "keyword_density", "content_quality", "structure_score"]
    
    for criterion in criteria:
        comparison_matrix[criterion] = {}
        
        for resume in resumes:
            if criterion == "ats_score":
                comparison_matrix[criterion][resume.id] = resume.ats_score or 0
            elif criterion == "keyword_density":
                analysis = resume.analysis_results or {}
                ats_data = analysis.get("ats_analysis", {})
                keyword_density = ats_data.get("keyword_density", {})
                avg_density = sum(keyword_density.values()) / len(keyword_density) if keyword_density else 0
                comparison_matrix[criterion][resume.id] = avg_density
            elif criterion == "content_quality":
                analysis = resume.analysis_results or {}
                content_data = analysis.get("content_analysis", {})
                content_score = (
                    content_data.get("readability_score", 0) +
                    content_data.get("grammar_score", 0) +
                    content_data.get("impact_score", 0)
                ) / 3
                comparison_matrix[criterion][resume.id] = content_score
            elif criterion == "structure_score":
                analysis = resume.analysis_results or {}
                ats_data = analysis.get("ats_analysis", {})
                comparison_matrix[criterion][resume.id] = ats_data.get("structure_score", 0)
    
    # Generate recommendations
    recommendations = generate_comparison_recommendations(comparison_matrix, resumes)
    
    # Generate best practices
    best_practices = [
        "Use consistent formatting across all resume versions",
        "Tailor keywords to specific job descriptions",
        "Quantify achievements with specific metrics",
        "Keep resume length appropriate for your experience level",
        "Use action verbs to start bullet points"
    ]
    
    return {
        "comparison_matrix": comparison_matrix,
        "recommendations": recommendations,
        "best_practices": best_practices
    }


async def generate_improvement_suggestions(
    analysis_result,
    extracted_skills: dict,
    target_role: Optional[str],
    target_industry: Optional[str]
) -> List[dict]:
    """Generate comprehensive improvement suggestions."""
    
    suggestions = []
    
    # ATS suggestions
    ats_analysis = analysis_result.ats_analysis
    if ats_analysis.overall_score < 80:
        suggestions.extend([
            {
                "type": "ats_improvement",
                "priority": "high",
                "suggestion": rec,
                "impact": "Improves ATS compatibility"
            }
            for rec in ats_analysis.format_recommendations[:3]
        ])
    
    # Content suggestions
    content_analysis = analysis_result.content_analysis
    if content_analysis.impact_score < 70:
        suggestions.extend([
            {
                "type": "content_improvement",
                "priority": "medium",
                "suggestion": "Add quantifiable achievements and metrics",
                "impact": "Increases impact and credibility"
            }
        ])
    
    # Skill suggestions
    skill_suggestions = skill_extractor.suggest_skill_improvements(extracted_skills, target_role)
    suggestions.extend([
        {
            "type": "skill_improvement",
            "priority": s.get("priority", "medium"),
            "suggestion": s["suggestion"],
            "impact": "Enhances technical profile"
        }
        for s in skill_suggestions[:3]
    ])
    
    return suggestions


async def generate_industry_specific_recommendations(
    structured_data: dict,
    industry: str,
    target_role: Optional[str]
) -> List[str]:
    """Generate industry-specific recommendations."""
    
    recommendations = []
    
    industry_guidelines = {
        "technology": [
            "Include GitHub profile and portfolio links",
            "Highlight specific programming languages and frameworks",
            "Mention open-source contributions",
            "Include technical project details"
        ],
        "finance": [
            "Emphasize analytical and quantitative skills",
            "Include relevant certifications (CFA, FRM, etc.)",
            "Highlight experience with financial modeling",
            "Mention regulatory compliance experience"
        ],
        "healthcare": [
            "Include relevant licenses and certifications",
            "Highlight patient care experience",
            "Mention compliance with healthcare regulations",
            "Include continuing education activities"
        ],
        "marketing": [
            "Include portfolio of campaigns and results",
            "Highlight digital marketing skills",
            "Mention analytics and ROI achievements",
            "Include social media and content creation experience"
        ]
    }
    
    return industry_guidelines.get(industry.lower(), [])


def calculate_priority_scores(recommendations: dict) -> dict:
    """Calculate priority scores for different recommendation categories."""
    
    priority_scores = {}
    
    for category, recs in recommendations.items():
        if recs:
            priority_scores[category] = len(recs) * 10  # Simple scoring
        else:
            priority_scores[category] = 0
    
    return priority_scores


def estimate_score_improvement(recommendations: dict) -> dict:
    """Estimate potential score improvement from recommendations."""
    
    improvements = {}
    
    for category, recs in recommendations.items():
        if category == "ats_optimization":
            improvements[category] = min(len(recs) * 5, 20)  # Up to 20 points
        elif category == "content_optimization":
            improvements[category] = min(len(recs) * 3, 15)  # Up to 15 points
        elif category == "keyword_optimization":
            improvements[category] = min(len(recs) * 4, 18)  # Up to 18 points
        else:
            improvements[category] = min(len(recs) * 2, 10)  # Up to 10 points
    
    return improvements


def generate_comparison_recommendations(comparison_matrix: dict, resumes: List[Resume]) -> List[str]:
    """Generate recommendations based on resume comparison."""
    
    recommendations = []
    
    for criterion, scores in comparison_matrix.items():
        if not scores:
            continue
        
        best_score = max(scores.values())
        worst_score = min(scores.values())
        
        if best_score - worst_score > 20:  # Significant difference
            best_resume = next(r for r in resumes if scores.get(r.id) == best_score)
            recommendations.append(
                f"Consider adopting the {criterion} approach from {best_resume.filename} "
                f"which scored {best_score:.1f} compared to the lowest score of {worst_score:.1f}"
            )
    
    return recommendations