"""
Coding challenge service for managing challenges, submissions, and code execution.
"""
import asyncio
import json
import hashlib
import difflib
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.orm import selectinload
import structlog
import uuid

from app.models.coding import (
    CodingChallenge, TestCase, CodeSubmission, CodeExecution,
    DifficultyLevel, LanguageType, ExecutionStatus
)
from app.models.user import User
from app.schemas.coding import (
    CodingChallengeCreate, CodingChallengeUpdate, CodingChallengeFilters,
    CodeSubmissionCreate, CodeExecutionResult, TestCaseResult,
    CodingChallengeAnalytics, UserCodingStats, CodeQualityMetrics,
    PlagiarismResult
)

logger = structlog.get_logger()


class CodingService:
    """Service for managing coding challenges and submissions."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_challenge(
        self, 
        challenge_data: CodingChallengeCreate, 
        created_by: uuid.UUID
    ) -> CodingChallenge:
        """Create a new coding challenge with test cases."""
        try:
            # Create the challenge
            challenge = CodingChallenge(
                title=challenge_data.title,
                description=challenge_data.description,
                difficulty=challenge_data.difficulty,
                category=challenge_data.category,
                topic_tags=challenge_data.topic_tags,
                company_tags=challenge_data.company_tags,
                time_limit=challenge_data.time_limit,
                memory_limit=challenge_data.memory_limit,
                template_code=challenge_data.template_code,
                solution_approach=challenge_data.solution_approach,
                hints=challenge_data.hints,
                is_active=challenge_data.is_active,
                created_by=created_by
            )
            
            self.db.add(challenge)
            await self.db.flush()  # Get the challenge ID
            
            # Create test cases
            for test_case_data in challenge_data.test_cases:
                test_case = TestCase(
                    challenge_id=challenge.id,
                    input_data=test_case_data.input_data,
                    expected_output=test_case_data.expected_output,
                    is_sample=test_case_data.is_sample,
                    is_hidden=test_case_data.is_hidden,
                    weight=test_case_data.weight,
                    explanation=test_case_data.explanation
                )
                self.db.add(test_case)
            
            await self.db.commit()
            await self.db.refresh(challenge)
            
            logger.info("Created coding challenge", challenge_id=challenge.id, title=challenge.title)
            return challenge
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to create coding challenge", error=str(e))
            raise
    
    async def get_challenge(self, challenge_id: uuid.UUID) -> Optional[CodingChallenge]:
        """Get a coding challenge by ID with test cases."""
        query = (
            select(CodingChallenge)
            .options(selectinload(CodingChallenge.test_cases))
            .where(CodingChallenge.id == challenge_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_challenges(
        self, 
        filters: CodingChallengeFilters,
        user_id: Optional[uuid.UUID] = None
    ) -> Tuple[List[CodingChallenge], int]:
        """Get coding challenges with filtering and pagination."""
        query = select(CodingChallenge)
        count_query = select(func.count(CodingChallenge.id))
        
        # Apply filters
        conditions = []
        
        if filters.difficulty:
            conditions.append(CodingChallenge.difficulty.in_(filters.difficulty))
        
        if filters.category:
            conditions.append(CodingChallenge.category.in_(filters.category))
        
        if filters.topic_tags:
            conditions.append(CodingChallenge.topic_tags.overlap(filters.topic_tags))
        
        if filters.company_tags:
            conditions.append(CodingChallenge.company_tags.overlap(filters.company_tags))
        
        if filters.is_active is not None:
            conditions.append(CodingChallenge.is_active == filters.is_active)
        
        if filters.search:
            search_term = f"%{filters.search}%"
            conditions.append(
                or_(
                    CodingChallenge.title.ilike(search_term),
                    CodingChallenge.description.ilike(search_term)
                )
            )
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        query = (
            query
            .order_by(desc(CodingChallenge.created_at))
            .offset(filters.offset)
            .limit(filters.limit)
        )
        
        result = await self.db.execute(query)
        challenges = result.scalars().all()
        
        return list(challenges), total
    
    async def update_challenge(
        self, 
        challenge_id: uuid.UUID, 
        update_data: CodingChallengeUpdate
    ) -> Optional[CodingChallenge]:
        """Update a coding challenge."""
        challenge = await self.get_challenge(challenge_id)
        if not challenge:
            return None
        
        try:
            # Update fields
            for field, value in update_data.dict(exclude_unset=True).items():
                setattr(challenge, field, value)
            
            challenge.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(challenge)
            
            logger.info("Updated coding challenge", challenge_id=challenge_id)
            return challenge
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to update coding challenge", challenge_id=challenge_id, error=str(e))
            raise
    
    async def delete_challenge(self, challenge_id: uuid.UUID) -> bool:
        """Soft delete a coding challenge."""
        challenge = await self.get_challenge(challenge_id)
        if not challenge:
            return False
        
        try:
            challenge.is_active = False
            await self.db.commit()
            
            logger.info("Deleted coding challenge", challenge_id=challenge_id)
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to delete coding challenge", challenge_id=challenge_id, error=str(e))
            raise
    
    async def submit_code(
        self, 
        submission_data: CodeSubmissionCreate, 
        user_id: uuid.UUID
    ) -> CodeSubmission:
        """Submit code for a challenge."""
        try:
            submission = CodeSubmission(
                user_id=user_id,
                challenge_id=submission_data.challenge_id,
                session_id=submission_data.session_id,
                language=submission_data.language,
                code=submission_data.code,
                status=ExecutionStatus.PENDING
            )
            
            self.db.add(submission)
            await self.db.commit()
            await self.db.refresh(submission)
            
            logger.info("Code submitted", submission_id=submission.id, user_id=user_id)
            
            # Queue for execution (this would typically be done via Celery)
            # For now, we'll execute synchronously
            await self._execute_code_async(submission.id)
            
            return submission
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to submit code", error=str(e))
            raise
    
    async def _execute_code_async(self, submission_id: uuid.UUID):
        """Execute code asynchronously (placeholder for actual execution)."""
        # This is a placeholder for the actual code execution logic
        # In a real implementation, this would:
        # 1. Get the submission and challenge
        # 2. Create a secure Docker container
        # 3. Execute the code against test cases
        # 4. Update the submission with results
        
        try:
            # Get submission and challenge
            query = (
                select(CodeSubmission)
                .options(selectinload(CodeSubmission.challenge).selectinload(CodingChallenge.test_cases))
                .where(CodeSubmission.id == submission_id)
            )
            result = await self.db.execute(query)
            submission = result.scalar_one_or_none()
            
            if not submission:
                logger.error("Submission not found", submission_id=submission_id)
                return
            
            # Update status to running
            submission.status = ExecutionStatus.RUNNING
            await self.db.commit()
            
            # Simulate code execution (replace with actual execution logic)
            await asyncio.sleep(1)  # Simulate execution time
            
            # Mock results for demonstration
            test_cases = submission.challenge.test_cases
            total_test_cases = len(test_cases)
            passed_test_cases = max(1, int(total_test_cases * 0.8))  # Mock 80% pass rate
            
            test_results = []
            for i, test_case in enumerate(test_cases):
                passed = i < passed_test_cases
                test_results.append({
                    "test_case_id": str(test_case.id),
                    "passed": passed,
                    "execution_time": 0.1,
                    "memory_usage": 10.5,
                    "actual_output": test_case.expected_output if passed else "Wrong output",
                    "error_message": None if passed else "Output mismatch"
                })
            
            # Update submission with results
            submission.status = ExecutionStatus.COMPLETED
            submission.total_test_cases = total_test_cases
            submission.passed_test_cases = passed_test_cases
            submission.score = (passed_test_cases / total_test_cases) * 100
            submission.execution_time = 0.5
            submission.memory_usage = 15.2
            submission.test_results = test_results
            submission.executed_at = datetime.utcnow()
            
            await self.db.commit()
            
            logger.info(
                "Code execution completed", 
                submission_id=submission_id,
                score=submission.score,
                passed=passed_test_cases,
                total=total_test_cases
            )
            
        except Exception as e:
            # Update submission status to failed
            try:
                submission.status = ExecutionStatus.FAILED
                submission.runtime_error = str(e)
                await self.db.commit()
            except:
                pass
            
            logger.error("Code execution failed", submission_id=submission_id, error=str(e))
    
    async def get_submission(self, submission_id: uuid.UUID) -> Optional[CodeSubmission]:
        """Get a code submission by ID."""
        query = select(CodeSubmission).where(CodeSubmission.id == submission_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_submissions(
        self, 
        user_id: uuid.UUID, 
        challenge_id: Optional[uuid.UUID] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[CodeSubmission], int]:
        """Get user's code submissions."""
        query = select(CodeSubmission).where(CodeSubmission.user_id == user_id)
        count_query = select(func.count(CodeSubmission.id)).where(CodeSubmission.user_id == user_id)
        
        if challenge_id:
            query = query.where(CodeSubmission.challenge_id == challenge_id)
            count_query = count_query.where(CodeSubmission.challenge_id == challenge_id)
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        query = (
            query
            .order_by(desc(CodeSubmission.submitted_at))
            .offset(offset)
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        submissions = result.scalars().all()
        
        return list(submissions), total
    
    async def get_challenge_analytics(self, challenge_id: uuid.UUID) -> Optional[CodingChallengeAnalytics]:
        """Get analytics for a specific challenge."""
        challenge = await self.get_challenge(challenge_id)
        if not challenge:
            return None
        
        # Get submission statistics
        stats_query = (
            select(
                func.count(CodeSubmission.id).label('total_submissions'),
                func.count(CodeSubmission.id).filter(CodeSubmission.score >= 100).label('successful_submissions'),
                func.avg(CodeSubmission.score).label('average_score'),
                func.avg(CodeSubmission.execution_time).label('average_execution_time')
            )
            .where(CodeSubmission.challenge_id == challenge_id)
        )
        
        stats_result = await self.db.execute(stats_query)
        stats = stats_result.first()
        
        # Get language popularity
        lang_query = (
            select(CodeSubmission.language, func.count(CodeSubmission.id))
            .where(CodeSubmission.challenge_id == challenge_id)
            .group_by(CodeSubmission.language)
        )
        
        lang_result = await self.db.execute(lang_query)
        popular_languages = {lang: count for lang, count in lang_result.all()}
        
        return CodingChallengeAnalytics(
            challenge_id=challenge_id,
            title=challenge.title,
            total_submissions=stats.total_submissions or 0,
            successful_submissions=stats.successful_submissions or 0,
            average_score=float(stats.average_score or 0),
            average_execution_time=float(stats.average_execution_time or 0) if stats.average_execution_time else None,
            difficulty_rating=self._calculate_difficulty_rating(stats.average_score or 0),
            popular_languages=popular_languages
        )
    
    async def get_user_coding_stats(self, user_id: uuid.UUID) -> UserCodingStats:
        """Get coding statistics for a user."""
        # Get basic statistics
        stats_query = (
            select(
                func.count(CodeSubmission.id).label('total_submissions'),
                func.count(CodeSubmission.id).filter(CodeSubmission.score >= 100).label('successful_submissions'),
                func.avg(CodeSubmission.score).label('average_score'),
                func.count(func.distinct(CodeSubmission.challenge_id)).label('challenges_attempted')
            )
            .where(CodeSubmission.user_id == user_id)
        )
        
        stats_result = await self.db.execute(stats_query)
        stats = stats_result.first()
        
        # Get favorite language
        lang_query = (
            select(CodeSubmission.language, func.count(CodeSubmission.id))
            .where(CodeSubmission.user_id == user_id)
            .group_by(CodeSubmission.language)
            .order_by(desc(func.count(CodeSubmission.id)))
            .limit(1)
        )
        
        lang_result = await self.db.execute(lang_query)
        favorite_lang = lang_result.first()
        
        # Get difficulty breakdown
        difficulty_query = (
            select(CodingChallenge.difficulty, func.count(CodeSubmission.id))
            .join(CodeSubmission, CodingChallenge.id == CodeSubmission.challenge_id)
            .where(CodeSubmission.user_id == user_id)
            .group_by(CodingChallenge.difficulty)
        )
        
        difficulty_result = await self.db.execute(difficulty_query)
        difficulty_breakdown = {diff.value: count for diff, count in difficulty_result.all()}
        
        # Get recent submissions
        recent_query = (
            select(CodeSubmission)
            .where(CodeSubmission.user_id == user_id)
            .order_by(desc(CodeSubmission.submitted_at))
            .limit(5)
        )
        
        recent_result = await self.db.execute(recent_query)
        recent_submissions = list(recent_result.scalars().all())
        
        return UserCodingStats(
            user_id=user_id,
            total_submissions=stats.total_submissions or 0,
            successful_submissions=stats.successful_submissions or 0,
            average_score=float(stats.average_score or 0),
            challenges_solved=stats.successful_submissions or 0,
            favorite_language=favorite_lang[0].value if favorite_lang else None,
            difficulty_breakdown=difficulty_breakdown,
            recent_submissions=recent_submissions
        )
    
    def _calculate_difficulty_rating(self, average_score: float) -> float:
        """Calculate difficulty rating based on average score."""
        if average_score >= 80:
            return 1.0  # Easy
        elif average_score >= 60:
            return 2.0  # Medium
        elif average_score >= 40:
            return 3.0  # Hard
        else:
            return 4.0  # Very Hard
    
    async def analyze_code_quality(self, submission_id: uuid.UUID) -> Optional[CodeQualityMetrics]:
        """Analyze code quality metrics (placeholder implementation)."""
        submission = await self.get_submission(submission_id)
        if not submission:
            return None
        
        # This is a placeholder implementation
        # In a real system, this would use static analysis tools
        code_length = len(submission.code)
        
        # Mock metrics based on code characteristics
        complexity_score = max(0.5, min(1.0, 1.0 - (code_length / 1000)))
        readability_score = 0.8  # Mock score
        efficiency_score = submission.score / 100 if submission.score else 0.5
        best_practices_score = 0.7  # Mock score
        
        suggestions = []
        code_smells = []
        
        if code_length > 500:
            suggestions.append("Consider breaking down the solution into smaller functions")
            code_smells.append("Long method")
        
        if "TODO" in submission.code or "FIXME" in submission.code:
            code_smells.append("TODO/FIXME comments found")
        
        return CodeQualityMetrics(
            submission_id=submission_id,
            complexity_score=complexity_score,
            readability_score=readability_score,
            efficiency_score=efficiency_score,
            best_practices_score=best_practices_score,
            suggestions=suggestions,
            code_smells=code_smells
        )
    
    async def detect_plagiarism(self, submission_id: uuid.UUID) -> Optional[PlagiarismResult]:
        """Detect potential plagiarism (placeholder implementation)."""
        submission = await self.get_submission(submission_id)
        if not submission:
            return None
        
        # Get other submissions for the same challenge
        other_submissions_query = (
            select(CodeSubmission)
            .where(
                and_(
                    CodeSubmission.challenge_id == submission.challenge_id,
                    CodeSubmission.id != submission_id,
                    CodeSubmission.language == submission.language
                )
            )
            .limit(100)  # Limit for performance
        )
        
        result = await self.db.execute(other_submissions_query)
        other_submissions = result.scalars().all()
        
        # Calculate similarity scores
        similar_submissions = []
        max_similarity = 0.0
        
        for other in other_submissions:
            similarity = self._calculate_code_similarity(submission.code, other.code)
            if similarity > 0.7:  # Threshold for suspicious similarity
                similar_submissions.append({
                    "submission_id": str(other.id),
                    "user_id": str(other.user_id),
                    "similarity_score": similarity,
                    "submitted_at": other.submitted_at.isoformat()
                })
                max_similarity = max(max_similarity, similarity)
        
        is_suspicious = max_similarity > 0.8
        confidence_level = max_similarity
        
        return PlagiarismResult(
            submission_id=submission_id,
            similarity_score=max_similarity,
            similar_submissions=similar_submissions,
            is_suspicious=is_suspicious,
            confidence_level=confidence_level
        )
    
    def _calculate_code_similarity(self, code1: str, code2: str) -> float:
        """Calculate similarity between two code snippets."""
        # Simple similarity calculation using difflib
        # In a real implementation, this would use more sophisticated techniques
        # like AST comparison, token-based similarity, etc.
        
        # Normalize code (remove whitespace, comments, etc.)
        normalized_code1 = self._normalize_code(code1)
        normalized_code2 = self._normalize_code(code2)
        
        # Calculate sequence similarity
        matcher = difflib.SequenceMatcher(None, normalized_code1, normalized_code2)
        return matcher.ratio()
    
    def _normalize_code(self, code: str) -> str:
        """Normalize code for similarity comparison."""
        # Remove comments, extra whitespace, etc.
        lines = []
        for line in code.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('//'):
                lines.append(line)
        return '\n'.join(lines)