from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from uuid import UUID
import structlog
import io

from app.core.database import get_db
from app.core.deps import get_current_active_user, get_current_admin, get_content_service
from app.services.content import ContentService
from app.schemas.content import (
    # Question schemas
    Question, QuestionCreate, QuestionUpdate, QuestionFilters, QuestionSearchResult,
    BulkQuestionCreate, BulkQuestionUpdate, BulkOperationResult,
    QuestionAnalytics, ContentAnalytics,
    # Category schemas
    Category, CategoryCreate, CategoryUpdate,
    # Tag schemas
    Tag, TagCreate, TagUpdate,
    # Company schemas
    Company, CompanyCreate, CompanyUpdate,
    # Collection schemas
    QuestionCollection, QuestionCollectionCreate, QuestionCollectionUpdate
)
from app.models.user import User
from app.models.question import QuestionType, DifficultyLevel, QuestionStatus

logger = structlog.get_logger()

router = APIRouter()


# Question Management Endpoints
@router.post(
    "/questions",
    response_model=Question,
    status_code=status.HTTP_201_CREATED,
    summary="Create question",
    description="Create a new question (admin/trainer only)"
)
async def create_question(
    question_data: QuestionCreate,
    request: Request,
    current_user: User = Depends(get_current_admin),
    content_service: ContentService = Depends(get_content_service)
) -> Question:
    """Create a new question"""
    
    try:
        logger.info(
            "Question creation attempt",
            user_id=str(current_user.id),
            type=question_data.type,
            category=question_data.category,
            client_ip=request.client.host
        )
        
        question = await content_service.create_question(
            question_data=question_data,
            created_by=current_user.id
        )
        
        logger.info(
            "Question created successfully",
            question_id=str(question.id),
            created_by=str(current_user.id)
        )
        
        return question
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to create question",
            error=str(e),
            user_id=str(current_user.id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "QUESTION_CREATION_FAILED",
                "message": "Failed to create question"
            }
        )


@router.get(
    "/questions/search",
    response_model=QuestionSearchResult,
    summary="Search questions",
    description="Search questions with advanced filtering and pagination"
)
async def search_questions(
    request: Request,
    # Query parameters for filtering
    type: Optional[QuestionType] = Query(None, description="Question type filter"),
    category: Optional[str] = Query(None, description="Category filter"),
    subcategory: Optional[str] = Query(None, description="Subcategory filter"),
    difficulty: Optional[List[DifficultyLevel]] = Query(None, description="Difficulty levels filter"),
    company_tags: Optional[List[str]] = Query(None, description="Company tags filter"),
    topic_tags: Optional[List[str]] = Query(None, description="Topic tags filter"),
    skill_tags: Optional[List[str]] = Query(None, description="Skill tags filter"),
    status: Optional[List[QuestionStatus]] = Query(None, description="Status filter"),
    is_active: Optional[bool] = Query(None, description="Active status filter"),
    is_premium: Optional[bool] = Query(None, description="Premium status filter"),
    search: Optional[str] = Query(None, description="Full-text search query"),
    min_success_rate: Optional[float] = Query(None, ge=0, le=100, description="Minimum success rate"),
    max_success_rate: Optional[float] = Query(None, ge=0, le=100, description="Maximum success rate"),
    min_usage_count: Optional[int] = Query(None, ge=0, description="Minimum usage count"),
    # Pagination parameters
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    # Sorting parameters
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    current_user: User = Depends(get_current_active_user),
    content_service: ContentService = Depends(get_content_service)
) -> QuestionSearchResult:
    """Search questions with advanced filtering"""
    
    try:
        # Build filters
        filters = QuestionFilters(
            type=type,
            category=category,
            subcategory=subcategory,
            difficulty=difficulty,
            company_tags=company_tags,
            topic_tags=topic_tags,
            skill_tags=skill_tags,
            status=status,
            is_active=is_active,
            is_premium=is_premium,
            search=search,
            min_success_rate=min_success_rate,
            max_success_rate=max_success_rate,
            min_usage_count=min_usage_count
        )
        
        logger.info(
            "Question search attempt",
            user_id=str(current_user.id),
            filters=filters.model_dump(exclude_unset=True),
            page=page,
            size=size
        )
        
        result = await content_service.search_questions(
            filters=filters,
            page=page,
            size=size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        logger.info(
            "Question search completed",
            user_id=str(current_user.id),
            total=result.total,
            returned=len(result.questions)
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to search questions",
            error=str(e),
            user_id=str(current_user.id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "QUESTION_SEARCH_FAILED",
                "message": "Failed to search questions"
            }
        )


@router.get(
    "/questions/{question_id}",
    response_model=Question,
    summary="Get question",
    description="Get question by ID"
)
async def get_question(
    question_id: UUID,
    current_user: User = Depends(get_current_active_user),
    content_service: ContentService = Depends(get_content_service)
) -> Question:
    """Get question by ID"""
    
    try:
        question = await content_service.get_question(question_id)
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "QUESTION_NOT_FOUND",
                    "message": "Question not found"
                }
            )
        
        logger.info(
            "Question retrieved",
            question_id=str(question_id),
            user_id=str(current_user.id)
        )
        
        return question
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get question",
            error=str(e),
            question_id=str(question_id),
            user_id=str(current_user.id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "QUESTION_FETCH_FAILED",
                "message": "Failed to retrieve question"
            }
        )


@router.put(
    "/questions/{question_id}",
    response_model=Question,
    summary="Update question",
    description="Update question by ID (admin/trainer only)"
)
async def update_question(
    question_id: UUID,
    question_data: QuestionUpdate,
    request: Request,
    current_user: User = Depends(get_current_admin),
    content_service: ContentService = Depends(get_content_service)
) -> Question:
    """Update question by ID"""
    
    try:
        logger.info(
            "Question update attempt",
            question_id=str(question_id),
            user_id=str(current_user.id),
            client_ip=request.client.host
        )
        
        question = await content_service.update_question(
            question_id=question_id,
            question_data=question_data,
            updated_by=current_user.id
        )
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "QUESTION_NOT_FOUND",
                    "message": "Question not found"
                }
            )
        
        logger.info(
            "Question updated successfully",
            question_id=str(question_id),
            updated_by=str(current_user.id)
        )
        
        return question
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to update question",
            error=str(e),
            question_id=str(question_id),
            user_id=str(current_user.id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "QUESTION_UPDATE_FAILED",
                "message": "Failed to update question"
            }
        )


@router.delete(
    "/questions/{question_id}",
    summary="Delete question",
    description="Soft delete question by ID (admin only)"
)
async def delete_question(
    question_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_admin),
    content_service: ContentService = Depends(get_content_service)
) -> Dict[str, Any]:
    """Soft delete question by ID"""
    
    try:
        logger.info(
            "Question deletion attempt",
            question_id=str(question_id),
            user_id=str(current_user.id),
            client_ip=request.client.host
        )
        
        success = await content_service.delete_question(question_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "QUESTION_NOT_FOUND",
                    "message": "Question not found"
                }
            )
        
        logger.info(
            "Question deleted successfully",
            question_id=str(question_id),
            deleted_by=str(current_user.id)
        )
        
        return {
            "message": "Question deleted successfully",
            "question_id": str(question_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to delete question",
            error=str(e),
            question_id=str(question_id),
            user_id=str(current_user.id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "QUESTION_DELETION_FAILED",
                "message": "Failed to delete question"
            }
        )


# Bulk Operations
@router.post(
    "/questions/bulk",
    response_model=BulkOperationResult,
    summary="Bulk create questions",
    description="Create multiple questions in bulk (admin/trainer only)"
)
async def bulk_create_questions(
    bulk_data: BulkQuestionCreate,
    request: Request,
    current_user: User = Depends(get_current_admin),
    content_service: ContentService = Depends(get_content_service)
) -> BulkOperationResult:
    """Bulk create questions"""
    
    try:
        logger.info(
            "Bulk question creation attempt",
            user_id=str(current_user.id),
            question_count=len(bulk_data.questions),
            client_ip=request.client.host
        )
        
        result = await content_service.bulk_create_questions(
            bulk_data=bulk_data,
            created_by=current_user.id
        )
        
        logger.info(
            "Bulk question creation completed",
            user_id=str(current_user.id),
            success_count=result.success_count,
            error_count=result.error_count
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to bulk create questions",
            error=str(e),
            user_id=str(current_user.id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "BULK_CREATION_FAILED",
                "message": "Failed to bulk create questions"
            }
        )


@router.patch(
    "/questions/bulk",
    response_model=BulkOperationResult,
    summary="Bulk update questions",
    description="Update multiple questions in bulk (admin/trainer only)"
)
async def bulk_update_questions(
    bulk_data: BulkQuestionUpdate,
    request: Request,
    current_user: User = Depends(get_current_admin),
    content_service: ContentService = Depends(get_content_service)
) -> BulkOperationResult:
    """Bulk update questions"""
    
    try:
        logger.info(
            "Bulk question update attempt",
            user_id=str(current_user.id),
            question_count=len(bulk_data.question_ids),
            client_ip=request.client.host
        )
        
        result = await content_service.bulk_update_questions(
            bulk_data=bulk_data,
            updated_by=current_user.id
        )
        
        logger.info(
            "Bulk question update completed",
            user_id=str(current_user.id),
            success_count=result.success_count,
            error_count=result.error_count
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to bulk update questions",
            error=str(e),
            user_id=str(current_user.id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "BULK_UPDATE_FAILED",
                "message": "Failed to bulk update questions"
            }
        )


# Import/Export Operations
@router.get(
    "/questions/export/csv",
    summary="Export questions to CSV",
    description="Export questions to CSV format (admin/trainer only)"
)
async def export_questions_csv(
    request: Request,
    # Optional filters for export
    type: Optional[QuestionType] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[List[QuestionStatus]] = Query(None),
    is_active: Optional[bool] = Query(True),
    current_user: User = Depends(get_current_admin),
    content_service: ContentService = Depends(get_content_service)
):
    """Export questions to CSV format"""
    
    try:
        logger.info(
            "Question CSV export attempt",
            user_id=str(current_user.id),
            client_ip=request.client.host
        )
        
        # Build filters if provided
        filters = None
        if any([type, category, status, is_active is not None]):
            filters = QuestionFilters(
                type=type,
                category=category,
                status=status,
                is_active=is_active
            )
        
        csv_content = await content_service.export_questions_csv(filters)
        
        # Create streaming response
        def generate():
            yield csv_content
        
        logger.info(
            "Question CSV export completed",
            user_id=str(current_user.id)
        )
        
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=questions_export.csv"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to export questions to CSV",
            error=str(e),
            user_id=str(current_user.id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "CSV_EXPORT_FAILED",
                "message": "Failed to export questions to CSV"
            }
        )


@router.post(
    "/questions/import/csv",
    response_model=BulkOperationResult,
    summary="Import questions from CSV",
    description="Import questions from CSV file (admin/trainer only)"
)
async def import_questions_csv(
    file: UploadFile = File(..., description="CSV file containing questions"),
    request: Request = None,
    current_user: User = Depends(get_current_admin),
    content_service: ContentService = Depends(get_content_service)
) -> BulkOperationResult:
    """Import questions from CSV file"""
    
    try:
        logger.info(
            "Question CSV import attempt",
            user_id=str(current_user.id),
            filename=file.filename,
            client_ip=request.client.host if request else None
        )
        
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "INVALID_FILE_TYPE",
                    "message": "Only CSV files are supported"
                }
            )
        
        # Read file content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        result = await content_service.import_questions_csv(
            csv_content=csv_content,
            created_by=current_user.id
        )
        
        logger.info(
            "Question CSV import completed",
            user_id=str(current_user.id),
            success_count=result.success_count,
            error_count=result.error_count
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to import questions from CSV",
            error=str(e),
            user_id=str(current_user.id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "CSV_IMPORT_FAILED",
                "message": "Failed to import questions from CSV"
            }
        )


# Content Approval Workflow
@router.post(
    "/questions/{question_id}/approve",
    response_model=Question,
    summary="Approve question",
    description="Approve a question for publication (admin only)"
)
async def approve_question(
    question_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_admin),
    content_service: ContentService = Depends(get_content_service)
) -> Question:
    """Approve a question"""
    
    try:
        logger.info(
            "Question approval attempt",
            question_id=str(question_id),
            user_id=str(current_user.id),
            client_ip=request.client.host
        )
        
        question = await content_service.approve_question(
            question_id=question_id,
            approved_by=current_user.id
        )
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "QUESTION_NOT_FOUND",
                    "message": "Question not found"
                }
            )
        
        logger.info(
            "Question approved successfully",
            question_id=str(question_id),
            approved_by=str(current_user.id)
        )
        
        return question
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to approve question",
            error=str(e),
            question_id=str(question_id),
            user_id=str(current_user.id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "QUESTION_APPROVAL_FAILED",
                "message": "Failed to approve question"
            }
        )


@router.post(
    "/questions/{question_id}/reject",
    response_model=Question,
    summary="Reject question",
    description="Reject a question with optional reason (admin only)"
)
async def reject_question(
    question_id: UUID,
    reason: Optional[str] = Query(None, description="Rejection reason"),
    request: Request = None,
    current_user: User = Depends(get_current_admin),
    content_service: ContentService = Depends(get_content_service)
) -> Question:
    """Reject a question"""
    
    try:
        logger.info(
            "Question rejection attempt",
            question_id=str(question_id),
            user_id=str(current_user.id),
            reason=reason,
            client_ip=request.client.host if request else None
        )
        
        question = await content_service.reject_question(
            question_id=question_id,
            rejected_by=current_user.id,
            reason=reason
        )
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "QUESTION_NOT_FOUND",
                    "message": "Question not found"
                }
            )
        
        logger.info(
            "Question rejected successfully",
            question_id=str(question_id),
            rejected_by=str(current_user.id)
        )
        
        return question
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to reject question",
            error=str(e),
            question_id=str(question_id),
            user_id=str(current_user.id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "QUESTION_REJECTION_FAILED",
                "message": "Failed to reject question"
            }
        )


# Analytics Endpoints
@router.get(
    "/questions/{question_id}/analytics",
    response_model=QuestionAnalytics,
    summary="Get question analytics",
    description="Get analytics for a specific question (admin/trainer only)"
)
async def get_question_analytics(
    question_id: UUID,
    current_user: User = Depends(get_current_admin),
    content_service: ContentService = Depends(get_content_service)
) -> QuestionAnalytics:
    """Get analytics for a specific question"""
    
    try:
        analytics = await content_service.get_question_analytics(question_id)
        
        if not analytics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "QUESTION_NOT_FOUND",
                    "message": "Question not found"
                }
            )
        
        logger.info(
            "Question analytics retrieved",
            question_id=str(question_id),
            user_id=str(current_user.id)
        )
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get question analytics",
            error=str(e),
            question_id=str(question_id),
            user_id=str(current_user.id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "ANALYTICS_FETCH_FAILED",
                "message": "Failed to retrieve question analytics"
            }
        )


@router.get(
    "/analytics",
    response_model=ContentAnalytics,
    summary="Get content analytics",
    description="Get overall content analytics (admin/trainer only)"
)
async def get_content_analytics(
    current_user: User = Depends(get_current_admin),
    content_service: ContentService = Depends(get_content_service)
) -> ContentAnalytics:
    """Get overall content analytics"""
    
    try:
        analytics = await content_service.get_content_analytics()
        
        logger.info(
            "Content analytics retrieved",
            user_id=str(current_user.id)
        )
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get content analytics",
            error=str(e),
            user_id=str(current_user.id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "ANALYTICS_FETCH_FAILED",
                "message": "Failed to retrieve content analytics"
            }
        )


# Category Management Endpoints
@router.post(
    "/categories",
    response_model=Category,
    status_code=status.HTTP_201_CREATED,
    summary="Create category",
    description="Create a new category (admin only)"
)
async def create_category(
    category_data: CategoryCreate,
    request: Request,
    current_user: User = Depends(get_current_admin),
    content_service: ContentService = Depends(get_content_service)
) -> Category:
    """Create a new category"""
    
    try:
        category = await content_service.create_category(category_data)
        
        logger.info(
            "Category created successfully",
            category_id=str(category.id),
            name=category.name,
            created_by=str(current_user.id)
        )
        
        return category
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to create category",
            error=str(e),
            user_id=str(current_user.id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "CATEGORY_CREATION_FAILED",
                "message": "Failed to create category"
            }
        )


@router.get(
    "/categories",
    response_model=List[Category],
    summary="Get categories",
    description="Get categories with optional filtering"
)
async def get_categories(
    type_filter: Optional[str] = Query(None, description="Category type filter"),
    parent_id: Optional[UUID] = Query(None, description="Parent category ID filter"),
    is_active: bool = Query(True, description="Active status filter"),
    current_user: User = Depends(get_current_active_user),
    content_service: ContentService = Depends(get_content_service)
) -> List[Category]:
    """Get categories with optional filtering"""
    
    try:
        categories = await content_service.get_categories(
            type_filter=type_filter,
            parent_id=parent_id,
            is_active=is_active
        )
        
        logger.info(
            "Categories retrieved",
            count=len(categories),
            user_id=str(current_user.id)
        )
        
        return categories
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get categories",
            error=str(e),
            user_id=str(current_user.id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "CATEGORIES_FETCH_FAILED",
                "message": "Failed to retrieve categories"
            }
        )


# Tag Management Endpoints
@router.post(
    "/tags",
    response_model=Tag,
    status_code=status.HTTP_201_CREATED,
    summary="Create tag",
    description="Create a new tag (admin only)"
)
async def create_tag(
    tag_data: TagCreate,
    request: Request,
    current_user: User = Depends(get_current_admin),
    content_service: ContentService = Depends(get_content_service)
) -> Tag:
    """Create a new tag"""
    
    try:
        tag = await content_service.create_tag(tag_data)
        
        logger.info(
            "Tag created successfully",
            tag_id=str(tag.id),
            name=tag.name,
            created_by=str(current_user.id)
        )
        
        return tag
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to create tag",
            error=str(e),
            user_id=str(current_user.id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "TAG_CREATION_FAILED",
                "message": "Failed to create tag"
            }
        )


@router.get(
    "/tags",
    response_model=List[Tag],
    summary="Get tags",
    description="Get tags with optional filtering"
)
async def get_tags(
    type_filter: Optional[str] = Query(None, description="Tag type filter"),
    is_active: bool = Query(True, description="Active status filter"),
    current_user: User = Depends(get_current_active_user),
    content_service: ContentService = Depends(get_content_service)
) -> List[Tag]:
    """Get tags with optional filtering"""
    
    try:
        tags = await content_service.get_tags(
            type_filter=type_filter,
            is_active=is_active
        )
        
        logger.info(
            "Tags retrieved",
            count=len(tags),
            user_id=str(current_user.id)
        )
        
        return tags
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get tags",
            error=str(e),
            user_id=str(current_user.id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "TAGS_FETCH_FAILED",
                "message": "Failed to retrieve tags"
            }
        )


# Company Management Endpoints
@router.post(
    "/companies",
    response_model=Company,
    status_code=status.HTTP_201_CREATED,
    summary="Create company",
    description="Create a new company (admin only)"
)
async def create_company(
    company_data: CompanyCreate,
    request: Request,
    current_user: User = Depends(get_current_admin),
    content_service: ContentService = Depends(get_content_service)
) -> Company:
    """Create a new company"""
    
    try:
        company = await content_service.create_company(company_data)
        
        logger.info(
            "Company created successfully",
            company_id=str(company.id),
            name=company.name,
            created_by=str(current_user.id)
        )
        
        return company
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to create company",
            error=str(e),
            user_id=str(current_user.id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "COMPANY_CREATION_FAILED",
                "message": "Failed to create company"
            }
        )


@router.get(
    "/companies",
    response_model=List[Company],
    summary="Get companies",
    description="Get companies with optional filtering"
)
async def get_companies(
    is_active: bool = Query(True, description="Active status filter"),
    is_featured: Optional[bool] = Query(None, description="Featured status filter"),
    current_user: User = Depends(get_current_active_user),
    content_service: ContentService = Depends(get_content_service)
) -> List[Company]:
    """Get companies with optional filtering"""
    
    try:
        companies = await content_service.get_companies(
            is_active=is_active,
            is_featured=is_featured
        )
        
        logger.info(
            "Companies retrieved",
            count=len(companies),
            user_id=str(current_user.id)
        )
        
        return companies
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get companies",
            error=str(e),
            user_id=str(current_user.id)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "COMPANIES_FETCH_FAILED",
                "message": "Failed to retrieve companies"
            }
        )