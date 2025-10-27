from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text, update, delete
from sqlalchemy.orm import selectinload, joinedload
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
import structlog
import json
import csv
import io
from datetime import datetime

from app.models.question import Question, QuestionType, DifficultyLevel, QuestionStatus
from app.models.content import Category, Tag, Company, QuestionCollection
from app.models.user import User
from app.schemas.content import (
    QuestionCreate, QuestionUpdate, QuestionFilters, QuestionSearchResult,
    BulkQuestionCreate, BulkQuestionUpdate, BulkOperationResult,
    QuestionAnalytics, ContentAnalytics,
    CategoryCreate, CategoryUpdate, TagCreate, TagUpdate,
    CompanyCreate, CompanyUpdate, QuestionCollectionCreate, QuestionCollectionUpdate
)

logger = structlog.get_logger()


class ContentService:
    """Service for managing content including questions, categories, tags, and companies"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Question Management
    async def create_question(
        self, 
        question_data: QuestionCreate, 
        created_by: Optional[UUID] = None
    ) -> Question:
        """Create a new question"""
        try:
            question = Question(
                **question_data.model_dump(exclude={'created_by'}),
                created_by=created_by or question_data.created_by
            )
            
            self.db.add(question)
            await self.db.commit()
            await self.db.refresh(question)
            
            logger.info(
                "Question created successfully",
                question_id=str(question.id),
                type=question.type,
                category=question.category,
                created_by=str(created_by) if created_by else None
            )
            
            return question
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to create question", error=str(e))
            raise
    
    async def get_question(self, question_id: UUID) -> Optional[Question]:
        """Get question by ID"""
        try:
            result = await self.db.execute(
                select(Question).where(Question.id == question_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error("Failed to get question", error=str(e), question_id=str(question_id))
            raise
    
    async def update_question(
        self, 
        question_id: UUID, 
        question_data: QuestionUpdate,
        updated_by: Optional[UUID] = None
    ) -> Optional[Question]:
        """Update question"""
        try:
            result = await self.db.execute(
                select(Question).where(Question.id == question_id)
            )
            question = result.scalar_one_or_none()
            
            if not question:
                return None
            
            # Update fields
            update_data = question_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(question, field, value)
            
            # Increment version if content changed
            content_fields = {'title', 'content', 'options', 'correct_answer', 'explanation'}
            if any(field in update_data for field in content_fields):
                question.version += 1
            
            await self.db.commit()
            await self.db.refresh(question)
            
            logger.info(
                "Question updated successfully",
                question_id=str(question_id),
                version=question.version,
                updated_by=str(updated_by) if updated_by else None
            )
            
            return question
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to update question", error=str(e), question_id=str(question_id))
            raise
    
    async def delete_question(self, question_id: UUID) -> bool:
        """Soft delete question"""
        try:
            result = await self.db.execute(
                select(Question).where(Question.id == question_id)
            )
            question = result.scalar_one_or_none()
            
            if not question:
                return False
            
            question.is_active = False
            await self.db.commit()
            
            logger.info("Question soft deleted", question_id=str(question_id))
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to delete question", error=str(e), question_id=str(question_id))
            raise
    
    async def search_questions(
        self, 
        filters: QuestionFilters,
        page: int = 1,
        size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> QuestionSearchResult:
        """Search questions with advanced filtering"""
        try:
            # Build base query
            query = select(Question)
            count_query = select(func.count(Question.id))
            
            # Apply filters
            conditions = []
            
            if filters.type:
                conditions.append(Question.type == filters.type)
            
            if filters.category:
                conditions.append(Question.category == filters.category)
            
            if filters.subcategory:
                conditions.append(Question.subcategory == filters.subcategory)
            
            if filters.difficulty:
                conditions.append(Question.difficulty.in_(filters.difficulty))
            
            if filters.company_tags:
                conditions.append(Question.company_tags.overlap(filters.company_tags))
            
            if filters.topic_tags:
                conditions.append(Question.topic_tags.overlap(filters.topic_tags))
            
            if filters.skill_tags:
                conditions.append(Question.skill_tags.overlap(filters.skill_tags))
            
            if filters.status:
                conditions.append(Question.status.in_(filters.status))
            
            if filters.is_active is not None:
                conditions.append(Question.is_active == filters.is_active)
            
            if filters.is_premium is not None:
                conditions.append(Question.is_premium == filters.is_premium)
            
            if filters.created_by:
                conditions.append(Question.created_by == filters.created_by)
            
            if filters.min_success_rate is not None:
                conditions.append(Question.success_rate >= filters.min_success_rate)
            
            if filters.max_success_rate is not None:
                conditions.append(Question.success_rate <= filters.max_success_rate)
            
            if filters.min_usage_count is not None:
                conditions.append(Question.usage_count >= filters.min_usage_count)
            
            # Full-text search
            if filters.search:
                search_condition = Question.search_vector.match(filters.search)
                conditions.append(search_condition)
            
            # Apply conditions
            if conditions:
                query = query.where(and_(*conditions))
                count_query = count_query.where(and_(*conditions))
            
            # Get total count
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()
            
            # Apply sorting
            sort_column = getattr(Question, sort_by, Question.created_at)
            if sort_order.lower() == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
            
            # Apply pagination
            offset = (page - 1) * size
            query = query.offset(offset).limit(size)
            
            # Execute query
            result = await self.db.execute(query)
            questions = result.scalars().all()
            
            pages = (total + size - 1) // size
            
            logger.info(
                "Questions searched successfully",
                total=total,
                page=page,
                size=size,
                pages=pages,
                filters=filters.model_dump(exclude_unset=True)
            )
            
            return QuestionSearchResult(
                questions=questions,
                total=total,
                page=page,
                size=size,
                pages=pages
            )
            
        except Exception as e:
            logger.error("Failed to search questions", error=str(e))
            raise
    
    # Bulk Operations
    async def bulk_create_questions(
        self, 
        bulk_data: BulkQuestionCreate,
        created_by: Optional[UUID] = None
    ) -> BulkOperationResult:
        """Bulk create questions"""
        success_count = 0
        error_count = 0
        errors = []
        
        try:
            for i, question_data in enumerate(bulk_data.questions):
                try:
                    question = Question(
                        **question_data.model_dump(exclude={'created_by'}),
                        created_by=created_by or question_data.created_by
                    )
                    self.db.add(question)
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    errors.append({
                        "index": i,
                        "error": str(e),
                        "question_data": question_data.model_dump()
                    })
            
            await self.db.commit()
            
            logger.info(
                "Bulk question creation completed",
                success_count=success_count,
                error_count=error_count,
                total=len(bulk_data.questions)
            )
            
            return BulkOperationResult(
                success_count=success_count,
                error_count=error_count,
                errors=errors
            )
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to bulk create questions", error=str(e))
            raise
    
    async def bulk_update_questions(
        self, 
        bulk_data: BulkQuestionUpdate,
        updated_by: Optional[UUID] = None
    ) -> BulkOperationResult:
        """Bulk update questions"""
        success_count = 0
        error_count = 0
        errors = []
        
        try:
            update_data = bulk_data.updates.model_dump(exclude_unset=True)
            
            for question_id in bulk_data.question_ids:
                try:
                    result = await self.db.execute(
                        select(Question).where(Question.id == question_id)
                    )
                    question = result.scalar_one_or_none()
                    
                    if question:
                        for field, value in update_data.items():
                            setattr(question, field, value)
                        success_count += 1
                    else:
                        error_count += 1
                        errors.append({
                            "question_id": str(question_id),
                            "error": "Question not found"
                        })
                        
                except Exception as e:
                    error_count += 1
                    errors.append({
                        "question_id": str(question_id),
                        "error": str(e)
                    })
            
            await self.db.commit()
            
            logger.info(
                "Bulk question update completed",
                success_count=success_count,
                error_count=error_count,
                total=len(bulk_data.question_ids)
            )
            
            return BulkOperationResult(
                success_count=success_count,
                error_count=error_count,
                errors=errors
            )
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to bulk update questions", error=str(e))
            raise
    
    # Import/Export Operations
    async def export_questions_csv(
        self, 
        filters: Optional[QuestionFilters] = None
    ) -> str:
        """Export questions to CSV format"""
        try:
            # Get questions based on filters
            if filters:
                search_result = await self.search_questions(
                    filters=filters,
                    page=1,
                    size=10000  # Large size to get all matching questions
                )
                questions = search_result.questions
            else:
                result = await self.db.execute(
                    select(Question).where(Question.is_active == True)
                )
                questions = result.scalars().all()
            
            # Create CSV content
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'id', 'type', 'category', 'subcategory', 'difficulty', 'title',
                'content', 'options', 'correct_answer', 'explanation', 'hints',
                'company_tags', 'topic_tags', 'skill_tags', 'status', 'is_premium',
                'usage_count', 'success_rate', 'average_time', 'created_at'
            ])
            
            # Write data
            for question in questions:
                writer.writerow([
                    str(question.id),
                    question.type,
                    question.category,
                    question.subcategory or '',
                    question.difficulty,
                    question.title,
                    question.content,
                    json.dumps(question.options) if question.options else '',
                    question.correct_answer,
                    question.explanation or '',
                    json.dumps(question.hints) if question.hints else '',
                    ','.join(question.company_tags) if question.company_tags else '',
                    ','.join(question.topic_tags) if question.topic_tags else '',
                    ','.join(question.skill_tags) if question.skill_tags else '',
                    question.status,
                    question.is_premium,
                    question.usage_count,
                    question.success_rate,
                    question.average_time,
                    question.created_at.isoformat() if question.created_at else ''
                ])
            
            csv_content = output.getvalue()
            output.close()
            
            logger.info(
                "Questions exported to CSV",
                question_count=len(questions)
            )
            
            return csv_content
            
        except Exception as e:
            logger.error("Failed to export questions to CSV", error=str(e))
            raise
    
    async def import_questions_csv(
        self, 
        csv_content: str,
        created_by: Optional[UUID] = None
    ) -> BulkOperationResult:
        """Import questions from CSV format"""
        success_count = 0
        error_count = 0
        errors = []
        
        try:
            input_stream = io.StringIO(csv_content)
            reader = csv.DictReader(input_stream)
            
            for row_num, row in enumerate(reader, start=2):  # Start from 2 (after header)
                try:
                    # Parse row data
                    question_data = {
                        'type': QuestionType(row['type']),
                        'category': row['category'],
                        'subcategory': row['subcategory'] if row['subcategory'] else None,
                        'difficulty': DifficultyLevel(int(row['difficulty'])),
                        'title': row['title'],
                        'content': row['content'],
                        'options': json.loads(row['options']) if row['options'] else None,
                        'correct_answer': row['correct_answer'],
                        'explanation': row['explanation'] if row['explanation'] else None,
                        'hints': json.loads(row['hints']) if row['hints'] else None,
                        'company_tags': row['company_tags'].split(',') if row['company_tags'] else [],
                        'topic_tags': row['topic_tags'].split(',') if row['topic_tags'] else [],
                        'skill_tags': row['skill_tags'].split(',') if row['skill_tags'] else [],
                        'status': QuestionStatus(row.get('status', 'draft')),
                        'is_premium': row.get('is_premium', '').lower() == 'true',
                        'created_by': created_by
                    }
                    
                    question = Question(**question_data)
                    self.db.add(question)
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    errors.append({
                        "row": row_num,
                        "error": str(e),
                        "data": dict(row)
                    })
            
            await self.db.commit()
            
            logger.info(
                "Questions imported from CSV",
                success_count=success_count,
                error_count=error_count,
                total=success_count + error_count
            )
            
            return BulkOperationResult(
                success_count=success_count,
                error_count=error_count,
                errors=errors
            )
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to import questions from CSV", error=str(e))
            raise
    
    # Content Versioning and Approval
    async def approve_question(
        self, 
        question_id: UUID, 
        approved_by: UUID
    ) -> Optional[Question]:
        """Approve a question"""
        try:
            result = await self.db.execute(
                select(Question).where(Question.id == question_id)
            )
            question = result.scalar_one_or_none()
            
            if not question:
                return None
            
            question.status = QuestionStatus.APPROVED
            question.reviewed_by = approved_by
            question.reviewed_at = datetime.utcnow()
            
            await self.db.commit()
            await self.db.refresh(question)
            
            logger.info(
                "Question approved",
                question_id=str(question_id),
                approved_by=str(approved_by)
            )
            
            return question
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to approve question", error=str(e), question_id=str(question_id))
            raise
    
    async def reject_question(
        self, 
        question_id: UUID, 
        rejected_by: UUID,
        reason: Optional[str] = None
    ) -> Optional[Question]:
        """Reject a question"""
        try:
            result = await self.db.execute(
                select(Question).where(Question.id == question_id)
            )
            question = result.scalar_one_or_none()
            
            if not question:
                return None
            
            question.status = QuestionStatus.REJECTED
            question.reviewed_by = rejected_by
            question.reviewed_at = datetime.utcnow()
            
            if reason:
                if not question.extra_data:
                    question.extra_data = {}
                question.extra_data['rejection_reason'] = reason
            
            await self.db.commit()
            await self.db.refresh(question)
            
            logger.info(
                "Question rejected",
                question_id=str(question_id),
                rejected_by=str(rejected_by),
                reason=reason
            )
            
            return question
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to reject question", error=str(e), question_id=str(question_id))
            raise
    
    # Analytics
    async def get_question_analytics(self, question_id: UUID) -> Optional[QuestionAnalytics]:
        """Get analytics for a specific question"""
        try:
            result = await self.db.execute(
                select(Question).where(Question.id == question_id)
            )
            question = result.scalar_one_or_none()
            
            if not question:
                return None
            
            return QuestionAnalytics(
                question_id=question.id,
                usage_count=question.usage_count,
                success_rate=question.success_rate,
                average_time=question.average_time,
                difficulty_rating=None,  # Could be calculated from user feedback
                user_feedback_score=None  # Could be calculated from user ratings
            )
            
        except Exception as e:
            logger.error("Failed to get question analytics", error=str(e), question_id=str(question_id))
            raise
    
    async def get_content_analytics(self) -> ContentAnalytics:
        """Get overall content analytics"""
        try:
            # Total questions
            total_result = await self.db.execute(
                select(func.count(Question.id)).where(Question.is_active == True)
            )
            total_questions = total_result.scalar()
            
            # Questions by type
            type_result = await self.db.execute(
                select(Question.type, func.count(Question.id))
                .where(Question.is_active == True)
                .group_by(Question.type)
            )
            questions_by_type = {row[0]: row[1] for row in type_result}
            
            # Questions by difficulty
            difficulty_result = await self.db.execute(
                select(Question.difficulty, func.count(Question.id))
                .where(Question.is_active == True)
                .group_by(Question.difficulty)
            )
            questions_by_difficulty = {str(row[0]): row[1] for row in difficulty_result}
            
            # Questions by status
            status_result = await self.db.execute(
                select(Question.status, func.count(Question.id))
                .group_by(Question.status)
            )
            questions_by_status = {row[0]: row[1] for row in status_result}
            
            # Top companies (from tags)
            company_result = await self.db.execute(
                text("""
                    SELECT unnest(company_tags) as company, COUNT(*) as count
                    FROM questions 
                    WHERE is_active = true AND company_tags IS NOT NULL
                    GROUP BY company
                    ORDER BY count DESC
                    LIMIT 10
                """)
            )
            top_companies = [{"name": row[0], "count": row[1]} for row in company_result]
            
            # Top topics (from tags)
            topic_result = await self.db.execute(
                text("""
                    SELECT unnest(topic_tags) as topic, COUNT(*) as count
                    FROM questions 
                    WHERE is_active = true AND topic_tags IS NOT NULL
                    GROUP BY topic
                    ORDER BY count DESC
                    LIMIT 10
                """)
            )
            top_topics = [{"name": row[0], "count": row[1]} for row in topic_result]
            
            # Average success rate
            avg_success_result = await self.db.execute(
                select(func.avg(Question.success_rate))
                .where(and_(Question.is_active == True, Question.success_rate.isnot(None)))
            )
            average_success_rate = avg_success_result.scalar()
            
            # Total submissions (would need to join with submissions table)
            # For now, using sum of usage_count as approximation
            submissions_result = await self.db.execute(
                select(func.sum(Question.usage_count))
                .where(Question.is_active == True)
            )
            total_submissions = submissions_result.scalar() or 0
            
            return ContentAnalytics(
                total_questions=total_questions,
                questions_by_type=questions_by_type,
                questions_by_difficulty=questions_by_difficulty,
                questions_by_status=questions_by_status,
                top_companies=top_companies,
                top_topics=top_topics,
                average_success_rate=average_success_rate,
                total_submissions=total_submissions
            )
            
        except Exception as e:
            logger.error("Failed to get content analytics", error=str(e))
            raise
    
    # Category Management
    async def create_category(self, category_data: CategoryCreate) -> Category:
        """Create a new category"""
        try:
            category = Category(**category_data.model_dump())
            self.db.add(category)
            await self.db.commit()
            await self.db.refresh(category)
            
            logger.info("Category created", category_id=str(category.id), name=category.name)
            return category
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to create category", error=str(e))
            raise
    
    async def get_categories(
        self, 
        type_filter: Optional[str] = None,
        parent_id: Optional[UUID] = None,
        is_active: bool = True
    ) -> List[Category]:
        """Get categories with optional filtering"""
        try:
            query = select(Category).options(selectinload(Category.children))
            
            conditions = []
            if type_filter:
                conditions.append(Category.type == type_filter)
            if parent_id is not None:
                conditions.append(Category.parent_id == parent_id)
            if is_active is not None:
                conditions.append(Category.is_active == is_active)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            query = query.order_by(Category.sort_order, Category.name)
            
            result = await self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error("Failed to get categories", error=str(e))
            raise
    
    # Tag Management
    async def create_tag(self, tag_data: TagCreate) -> Tag:
        """Create a new tag"""
        try:
            tag = Tag(**tag_data.model_dump())
            self.db.add(tag)
            await self.db.commit()
            await self.db.refresh(tag)
            
            logger.info("Tag created", tag_id=str(tag.id), name=tag.name)
            return tag
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to create tag", error=str(e))
            raise
    
    async def get_tags(
        self, 
        type_filter: Optional[str] = None,
        is_active: bool = True
    ) -> List[Tag]:
        """Get tags with optional filtering"""
        try:
            query = select(Tag)
            
            conditions = []
            if type_filter:
                conditions.append(Tag.type == type_filter)
            if is_active is not None:
                conditions.append(Tag.is_active == is_active)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            query = query.order_by(Tag.usage_count.desc(), Tag.name)
            
            result = await self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error("Failed to get tags", error=str(e))
            raise
    
    # Company Management
    async def create_company(self, company_data: CompanyCreate) -> Company:
        """Create a new company"""
        try:
            company = Company(**company_data.model_dump())
            self.db.add(company)
            await self.db.commit()
            await self.db.refresh(company)
            
            logger.info("Company created", company_id=str(company.id), name=company.name)
            return company
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to create company", error=str(e))
            raise
    
    async def get_companies(
        self, 
        is_active: bool = True,
        is_featured: Optional[bool] = None
    ) -> List[Company]:
        """Get companies with optional filtering"""
        try:
            query = select(Company)
            
            conditions = []
            if is_active is not None:
                conditions.append(Company.is_active == is_active)
            if is_featured is not None:
                conditions.append(Company.is_featured == is_featured)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            query = query.order_by(Company.popularity_score.desc(), Company.name)
            
            result = await self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error("Failed to get companies", error=str(e))
            raise