"""
Aptitude Test Engine Service

This service implements the core aptitude testing functionality including:
- Test session management with time tracking
- Adaptive question selection algorithm
- Automatic scoring and result calculation
- Test configuration and customization options
"""

from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
import random
import math
from enum import Enum

from app.models.question import Question, QuestionType, DifficultyLevel
from app.models.session import TestSession, SessionStatus, TestType
from app.models.submission import Submission, SubmissionType, SubmissionStatus
from app.models.user import User
from app.schemas.content import TestSessionCreate, TestSessionUpdate, SubmissionCreate
from app.core.database import get_db


class AdaptiveAlgorithm(str, Enum):
    """Adaptive question selection algorithms"""
    RANDOM = "random"
    DIFFICULTY_BASED = "difficulty_based"
    PERFORMANCE_BASED = "performance_based"
    IRT_BASED = "irt_based"  # Item Response Theory
    BALANCED = "balanced"


class TestConfiguration:
    """Test configuration class for aptitude tests"""
    
    def __init__(
        self,
        test_type: TestType = TestType.APTITUDE,
        total_questions: int = 20,
        time_limit: Optional[int] = None,  # seconds
        time_per_question: Optional[int] = None,  # seconds
        categories: Optional[List[str]] = None,
        difficulty_levels: Optional[List[int]] = None,
        company_tags: Optional[List[str]] = None,
        topic_tags: Optional[List[str]] = None,
        adaptive_algorithm: AdaptiveAlgorithm = AdaptiveAlgorithm.BALANCED,
        randomize_questions: bool = True,
        randomize_options: bool = True,
        allow_review: bool = True,
        show_results: bool = True,
        passing_score: float = 60.0,
        negative_marking: bool = False,
        negative_marking_ratio: float = 0.25,
        difficulty_distribution: Optional[Dict[int, float]] = None,
        **kwargs
    ):
        self.test_type = test_type
        self.total_questions = total_questions
        self.time_limit = time_limit
        self.time_per_question = time_per_question
        self.categories = categories or []
        self.difficulty_levels = difficulty_levels or [1, 2, 3, 4, 5]
        self.company_tags = company_tags or []
        self.topic_tags = topic_tags or []
        self.adaptive_algorithm = adaptive_algorithm
        self.randomize_questions = randomize_questions
        self.randomize_options = randomize_options
        self.allow_review = allow_review
        self.show_results = show_results
        self.passing_score = passing_score
        self.negative_marking = negative_marking
        self.negative_marking_ratio = negative_marking_ratio
        
        # Default difficulty distribution (balanced)
        self.difficulty_distribution = difficulty_distribution or {
            1: 0.1,  # 10% beginner
            2: 0.2,  # 20% easy
            3: 0.4,  # 40% medium
            4: 0.2,  # 20% hard
            5: 0.1   # 10% expert
        }
        
        # Additional configuration
        self.extra_config = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "test_type": self.test_type,
            "total_questions": self.total_questions,
            "time_limit": self.time_limit,
            "time_per_question": self.time_per_question,
            "categories": self.categories,
            "difficulty_levels": self.difficulty_levels,
            "company_tags": self.company_tags,
            "topic_tags": self.topic_tags,
            "adaptive_algorithm": self.adaptive_algorithm,
            "randomize_questions": self.randomize_questions,
            "randomize_options": self.randomize_options,
            "allow_review": self.allow_review,
            "show_results": self.show_results,
            "passing_score": self.passing_score,
            "negative_marking": self.negative_marking,
            "negative_marking_ratio": self.negative_marking_ratio,
            "difficulty_distribution": self.difficulty_distribution,
            **self.extra_config
        }


class AptitudeTestEngine:
    """Core aptitude test engine with adaptive algorithms and session management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_test_session(
        self,
        user_id: UUID,
        config: TestConfiguration,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> TestSession:
        """Create a new aptitude test session with selected questions"""
        
        # Select questions based on configuration
        selected_questions = await self._select_questions(config)
        
        if len(selected_questions) < config.total_questions:
            # If not enough questions available, adjust total questions
            config.total_questions = len(selected_questions)
        
        # Create test session
        session = TestSession(
            user_id=user_id,
            test_type=config.test_type,
            title=title or f"Aptitude Test - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            description=description,
            configuration=config.to_dict(),
            question_ids=[q.id for q in selected_questions],
            total_questions=len(selected_questions),
            time_limit=config.time_limit,
            time_per_question=config.time_per_question,
            allow_review=config.allow_review,
            show_results=config.show_results,
            randomize_questions=config.randomize_questions,
            randomize_options=config.randomize_options,
            categories=config.categories,
            difficulty_levels=config.difficulty_levels,
            company_tags=config.company_tags,
            topic_tags=config.topic_tags,
            status=SessionStatus.CREATED
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    async def start_session(self, session_id: UUID, user_id: UUID) -> TestSession:
        """Start a test session"""
        session = self.db.query(TestSession).filter(
            and_(
                TestSession.id == session_id,
                TestSession.user_id == user_id,
                TestSession.status == SessionStatus.CREATED
            )
        ).first()
        
        if not session:
            raise ValueError("Session not found or cannot be started")
        
        session.start_session()
        session.start_time = datetime.now(timezone.utc)
        
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    async def get_current_question(self, session_id: UUID, user_id: UUID) -> Optional[Question]:
        """Get the current question for a session"""
        session = self.db.query(TestSession).filter(
            and_(
                TestSession.id == session_id,
                TestSession.user_id == user_id
            )
        ).first()
        
        if not session or session.current_question_index >= len(session.question_ids):
            return None
        
        question_id = session.question_ids[session.current_question_index]
        question = self.db.query(Question).filter(Question.id == question_id).first()
        
        # Randomize options if configured
        if question and session.randomize_options and question.options:
            question.options = self._randomize_options(question.options, question.correct_answer)
        
        return question
    
    async def submit_answer(
        self,
        session_id: UUID,
        user_id: UUID,
        question_id: UUID,
        user_answer: str,
        time_taken: int
    ) -> Tuple[Submission, bool]:  # Returns (submission, is_session_complete)
        """Submit an answer and calculate score"""
        
        # Get session and validate
        session = self.db.query(TestSession).filter(
            and_(
                TestSession.id == session_id,
                TestSession.user_id == user_id,
                TestSession.status == SessionStatus.ACTIVE
            )
        ).first()
        
        if not session:
            raise ValueError("Session not found or not active")
        
        # Get question
        question = self.db.query(Question).filter(Question.id == question_id).first()
        if not question:
            raise ValueError("Question not found")
        
        # Check if answer already submitted for this question
        existing_submission = self.db.query(Submission).filter(
            and_(
                Submission.session_id == session_id,
                Submission.question_id == question_id
            )
        ).first()
        
        if existing_submission:
            raise ValueError("Answer already submitted for this question")
        
        # Calculate score
        is_correct = self._evaluate_answer(question, user_answer)
        score = self._calculate_question_score(question, is_correct, time_taken, session.configuration)
        
        # Create submission
        submission = Submission(
            user_id=user_id,
            session_id=session_id,
            question_id=question_id,
            submission_type=SubmissionType.APTITUDE,
            user_answer=user_answer,
            is_correct=is_correct,
            score=score,
            max_score=self._get_max_question_score(question, session.configuration),
            time_taken=time_taken,
            time_limit=session.time_per_question,
            status=SubmissionStatus.EVALUATED,
            submitted_at=datetime.now(timezone.utc),
            evaluated_at=datetime.now(timezone.utc)
        )
        
        self.db.add(submission)
        
        # Update session progress
        if is_correct:
            session.correct_answers += 1
        else:
            session.incorrect_answers += 1
        
        session.update_score(score)
        session.current_question_index += 1
        
        # Update question analytics
        question.increment_usage()
        question.update_analytics(is_correct, time_taken)
        
        # Check if session is complete
        is_complete = session.current_question_index >= session.total_questions
        if is_complete:
            await self._complete_session(session)
        
        self.db.commit()
        self.db.refresh(submission)
        
        return submission, is_complete
    
    async def pause_session(self, session_id: UUID, user_id: UUID) -> TestSession:
        """Pause a test session"""
        session = self.db.query(TestSession).filter(
            and_(
                TestSession.id == session_id,
                TestSession.user_id == user_id,
                TestSession.status == SessionStatus.ACTIVE
            )
        ).first()
        
        if not session:
            raise ValueError("Session not found or cannot be paused")
        
        session.pause_session()
        session.pause_time = datetime.now(timezone.utc)
        
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    async def resume_session(self, session_id: UUID, user_id: UUID) -> TestSession:
        """Resume a paused test session"""
        session = self.db.query(TestSession).filter(
            and_(
                TestSession.id == session_id,
                TestSession.user_id == user_id,
                TestSession.status == SessionStatus.PAUSED
            )
        ).first()
        
        if not session:
            raise ValueError("Session not found or cannot be resumed")
        
        session.resume_session()
        
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    async def get_session_progress(self, session_id: UUID, user_id: UUID) -> Dict[str, Any]:
        """Get detailed session progress information"""
        session = self.db.query(TestSession).filter(
            and_(
                TestSession.id == session_id,
                TestSession.user_id == user_id
            )
        ).first()
        
        if not session:
            raise ValueError("Session not found")
        
        # Calculate time remaining
        time_remaining = None
        if session.time_limit and session.start_time:
            elapsed = (datetime.now(timezone.utc) - session.start_time).total_seconds()
            elapsed -= session.total_pause_duration
            time_remaining = max(0, session.time_limit - int(elapsed))
        
        # Get submissions for detailed analysis
        submissions = self.db.query(Submission).filter(
            Submission.session_id == session_id
        ).all()
        
        return {
            "session_id": session.id,
            "status": session.status,
            "current_question": session.current_question_index + 1,
            "total_questions": session.total_questions,
            "progress_percentage": session.progress_percentage,
            "correct_answers": session.correct_answers,
            "incorrect_answers": session.incorrect_answers,
            "skipped_answers": session.skipped_answers,
            "current_score": float(session.score) if session.score else 0.0,
            "accuracy_percentage": session.accuracy_percentage,
            "time_remaining": time_remaining,
            "time_limit": session.time_limit,
            "start_time": session.start_time,
            "submissions_count": len(submissions),
            "can_pause": session.status == SessionStatus.ACTIVE,
            "can_resume": session.status == SessionStatus.PAUSED,
            "allow_review": session.allow_review
        }
    
    async def get_session_results(self, session_id: UUID, user_id: UUID) -> Dict[str, Any]:
        """Get comprehensive session results and analysis"""
        session = self.db.query(TestSession).filter(
            and_(
                TestSession.id == session_id,
                TestSession.user_id == user_id,
                TestSession.status == SessionStatus.COMPLETED
            )
        ).first()
        
        if not session:
            raise ValueError("Session not found or not completed")
        
        # Get all submissions with questions
        submissions = self.db.query(Submission).join(Question).filter(
            Submission.session_id == session_id
        ).all()
        
        # Calculate detailed analytics
        category_performance = self._calculate_category_performance(submissions)
        difficulty_performance = self._calculate_difficulty_performance(submissions)
        time_analysis = self._calculate_time_analysis(submissions, session)
        
        return {
            "session_id": session.id,
            "title": session.title,
            "test_type": session.test_type,
            "total_questions": session.total_questions,
            "correct_answers": session.correct_answers,
            "incorrect_answers": session.incorrect_answers,
            "skipped_answers": session.skipped_answers,
            "final_score": float(session.score) if session.score else 0.0,
            "max_score": float(session.max_score) if session.max_score else 0.0,
            "percentage": session.percentage,
            "accuracy_percentage": session.accuracy_percentage,
            "total_time_taken": session.total_time_taken,
            "average_time_per_question": session.total_time_taken / session.total_questions if session.total_time_taken else None,
            "start_time": session.start_time,
            "end_time": session.end_time,
            "passed": session.percentage >= session.configuration.get("passing_score", 60.0) if session.percentage else False,
            "category_performance": category_performance,
            "difficulty_performance": difficulty_performance,
            "time_analysis": time_analysis,
            "detailed_submissions": [
                {
                    "question_id": sub.question_id,
                    "user_answer": sub.user_answer,
                    "correct_answer": sub.question.correct_answer,
                    "is_correct": sub.is_correct,
                    "score": float(sub.score) if sub.score else 0.0,
                    "time_taken": sub.time_taken,
                    "category": sub.question.category,
                    "difficulty": sub.question.difficulty
                }
                for sub in submissions
            ] if session.show_results else []
        }
    
    # Private helper methods
    
    async def _select_questions(self, config: TestConfiguration) -> List[Question]:
        """Select questions based on configuration and adaptive algorithm"""
        
        # Build base query
        query = self.db.query(Question).filter(
            and_(
                Question.type == QuestionType.APTITUDE,
                Question.is_active == True,
                Question.status == "approved"
            )
        )
        
        # Apply filters
        if config.categories:
            query = query.filter(Question.category.in_(config.categories))
        
        if config.difficulty_levels:
            query = query.filter(Question.difficulty.in_(config.difficulty_levels))
        
        if config.company_tags:
            query = query.filter(Question.company_tags.overlap(config.company_tags))
        
        if config.topic_tags:
            query = query.filter(Question.topic_tags.overlap(config.topic_tags))
        
        # Get available questions
        available_questions = query.all()
        
        if not available_questions:
            raise ValueError("No questions available with the specified criteria")
        
        # Apply adaptive selection algorithm
        if config.adaptive_algorithm == AdaptiveAlgorithm.RANDOM:
            selected = self._random_selection(available_questions, config)
        elif config.adaptive_algorithm == AdaptiveAlgorithm.DIFFICULTY_BASED:
            selected = self._difficulty_based_selection(available_questions, config)
        elif config.adaptive_algorithm == AdaptiveAlgorithm.BALANCED:
            selected = self._balanced_selection(available_questions, config)
        else:
            # Default to balanced selection
            selected = self._balanced_selection(available_questions, config)
        
        # Randomize order if configured
        if config.randomize_questions:
            random.shuffle(selected)
        
        return selected[:config.total_questions]
    
    def _random_selection(self, questions: List[Question], config: TestConfiguration) -> List[Question]:
        """Random question selection"""
        return random.sample(questions, min(len(questions), config.total_questions))
    
    def _difficulty_based_selection(self, questions: List[Question], config: TestConfiguration) -> List[Question]:
        """Select questions based on difficulty distribution"""
        selected = []
        questions_by_difficulty = {}
        
        # Group questions by difficulty
        for question in questions:
            if question.difficulty not in questions_by_difficulty:
                questions_by_difficulty[question.difficulty] = []
            questions_by_difficulty[question.difficulty].append(question)
        
        # Select based on distribution
        for difficulty, ratio in config.difficulty_distribution.items():
            if difficulty in questions_by_difficulty:
                count = int(config.total_questions * ratio)
                available = questions_by_difficulty[difficulty]
                selected.extend(random.sample(available, min(len(available), count)))
        
        # Fill remaining slots if needed
        remaining = config.total_questions - len(selected)
        if remaining > 0:
            remaining_questions = [q for q in questions if q not in selected]
            selected.extend(random.sample(remaining_questions, min(len(remaining_questions), remaining)))
        
        return selected
    
    def _balanced_selection(self, questions: List[Question], config: TestConfiguration) -> List[Question]:
        """Balanced selection considering difficulty, category, and performance"""
        selected = []
        
        # Group questions by category and difficulty
        grouped = {}
        for question in questions:
            key = (question.category, question.difficulty)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(question)
        
        # Calculate questions per group
        total_groups = len(grouped)
        questions_per_group = max(1, config.total_questions // total_groups)
        
        # Select from each group
        for group_questions in grouped.values():
            # Sort by success rate (ascending) to prefer challenging questions
            group_questions.sort(key=lambda q: q.success_rate or 50.0)
            count = min(len(group_questions), questions_per_group)
            selected.extend(group_questions[:count])
        
        # Fill remaining slots
        remaining = config.total_questions - len(selected)
        if remaining > 0:
            remaining_questions = [q for q in questions if q not in selected]
            selected.extend(random.sample(remaining_questions, min(len(remaining_questions), remaining)))
        
        return selected
    
    def _evaluate_answer(self, question: Question, user_answer: str) -> bool:
        """Evaluate if the user's answer is correct"""
        # Normalize answers for comparison
        correct_answer = question.correct_answer.strip().lower()
        user_answer = user_answer.strip().lower()
        
        return correct_answer == user_answer
    
    def _calculate_question_score(
        self,
        question: Question,
        is_correct: bool,
        time_taken: int,
        config: Dict[str, Any]
    ) -> float:
        """Calculate score for a question based on correctness and configuration"""
        
        base_score = 1.0  # Base score per question
        
        if is_correct:
            score = base_score
            
            # Time bonus (if answered quickly)
            if config.get("time_per_question") and time_taken < config["time_per_question"] * 0.5:
                score += 0.1  # 10% bonus for quick answers
                
        else:
            # Negative marking if enabled
            if config.get("negative_marking", False):
                score = -base_score * config.get("negative_marking_ratio", 0.25)
            else:
                score = 0.0
        
        return score
    
    def _get_max_question_score(self, question: Question, config: Dict[str, Any]) -> float:
        """Get maximum possible score for a question"""
        base_score = 1.0
        
        # Add time bonus potential
        if config.get("time_per_question"):
            base_score += 0.1
        
        return base_score
    
    def _randomize_options(self, options: List[str], correct_answer: str) -> List[str]:
        """Randomize question options while maintaining correct answer mapping"""
        if not options or len(options) < 2:
            return options
        
        # Create a copy and shuffle
        randomized = options.copy()
        random.shuffle(randomized)
        
        return randomized
    
    async def _complete_session(self, session: TestSession):
        """Complete a test session and calculate final results"""
        session.complete_session()
        session.end_time = datetime.now(timezone.utc)
        
        # Calculate total time taken
        if session.start_time:
            total_time = (session.end_time - session.start_time).total_seconds()
            session.total_time_taken = int(total_time - session.total_pause_duration)
        
        # Calculate max possible score
        config = session.configuration
        max_score_per_question = self._get_max_question_score(None, config)  # Generic calculation
        session.max_score = session.total_questions * max_score_per_question
        
        # Calculate percentage
        if session.max_score and session.max_score > 0:
            session.percentage = (float(session.score) / float(session.max_score)) * 100
        else:
            session.percentage = (session.correct_answers / session.total_questions) * 100
    
    def _calculate_category_performance(self, submissions: List[Submission]) -> Dict[str, Any]:
        """Calculate performance by category"""
        category_stats = {}
        
        for submission in submissions:
            category = submission.question.category
            if category not in category_stats:
                category_stats[category] = {
                    "total": 0,
                    "correct": 0,
                    "total_time": 0,
                    "total_score": 0.0
                }
            
            stats = category_stats[category]
            stats["total"] += 1
            if submission.is_correct:
                stats["correct"] += 1
            stats["total_time"] += submission.time_taken
            stats["total_score"] += float(submission.score) if submission.score else 0.0
        
        # Calculate percentages and averages
        for category, stats in category_stats.items():
            stats["accuracy"] = (stats["correct"] / stats["total"]) * 100
            stats["average_time"] = stats["total_time"] / stats["total"]
            stats["average_score"] = stats["total_score"] / stats["total"]
        
        return category_stats
    
    def _calculate_difficulty_performance(self, submissions: List[Submission]) -> Dict[str, Any]:
        """Calculate performance by difficulty level"""
        difficulty_stats = {}
        
        for submission in submissions:
            difficulty = submission.question.difficulty
            if difficulty not in difficulty_stats:
                difficulty_stats[difficulty] = {
                    "total": 0,
                    "correct": 0,
                    "total_time": 0,
                    "total_score": 0.0
                }
            
            stats = difficulty_stats[difficulty]
            stats["total"] += 1
            if submission.is_correct:
                stats["correct"] += 1
            stats["total_time"] += submission.time_taken
            stats["total_score"] += float(submission.score) if submission.score else 0.0
        
        # Calculate percentages and averages
        for difficulty, stats in difficulty_stats.items():
            stats["accuracy"] = (stats["correct"] / stats["total"]) * 100
            stats["average_time"] = stats["total_time"] / stats["total"]
            stats["average_score"] = stats["total_score"] / stats["total"]
        
        return difficulty_stats
    
    def _calculate_time_analysis(self, submissions: List[Submission], session: TestSession) -> Dict[str, Any]:
        """Calculate time-based analysis"""
        if not submissions:
            return {}
        
        times = [sub.time_taken for sub in submissions]
        
        return {
            "total_time": sum(times),
            "average_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times),
            "time_efficiency": session.total_time_taken / session.time_limit if session.time_limit else None
        }