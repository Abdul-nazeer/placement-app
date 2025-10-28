import asyncio
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from uuid import UUID
import random

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.models.interview import (
    InterviewSession, InterviewQuestion, InterviewResponse,
    InterviewType, InterviewStatus, QuestionCategory, DifficultyLevel
)
from app.models.user import User
from app.schemas.interview import (
    InterviewSessionCreate, QuestionGenerationRequest, 
    InterviewQuestionCreate, InterviewResponseCreate
)
from app.services.groq_client import GroqClient
from app.services.speech_processing import SpeechProcessor
from app.core.config import settings

logger = logging.getLogger(__name__)


class InterviewEngine:
    """Core engine for managing interview simulations with AI-powered features."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.groq_client = GroqClient()
        self.speech_processor = SpeechProcessor()
        
        # Enhanced question generation templates for different scenarios
        self.question_templates = {
            InterviewType.BEHAVIORAL: {
                QuestionCategory.BEHAVIORAL: [
                    "Tell me about a time when you faced a significant challenge at work. How did you overcome it?",
                    "Describe a situation where you had to work with a difficult team member. What was your approach?",
                    "Give me an example of when you had to learn something new quickly. How did you go about it?",
                    "Tell me about a time when you made a mistake. How did you handle it and what did you learn?",
                    "Describe a situation where you had to meet a tight deadline. What steps did you take?",
                    "Tell me about a time when you had to persuade someone to see things your way.",
                    "Give me an example of when you showed leadership, even if you weren't in a leadership position.",
                    "Describe a situation where you had to adapt to a significant change at work."
                ],
                QuestionCategory.SITUATIONAL: [
                    "How would you handle a situation where you disagree with your manager's decision?",
                    "What would you do if you discovered a colleague was not pulling their weight on a team project?",
                    "If you were assigned a project with an unrealistic deadline, how would you approach it?",
                    "How would you handle receiving constructive criticism about your work?",
                    "What would you do if you had to work with a technology you've never used before?"
                ]
            },
            InterviewType.TECHNICAL: {
                QuestionCategory.TECHNICAL_CODING: [
                    "Implement a function to reverse a linked list iteratively and recursively.",
                    "Design an algorithm to find the longest palindromic substring in a given string.",
                    "Write code to implement a basic LRU (Least Recently Used) cache.",
                    "Solve the two-sum problem with optimal time and space complexity.",
                    "Implement a function to validate if a binary tree is a valid binary search tree.",
                    "Design an algorithm to merge two sorted arrays in-place.",
                    "Write code to detect if a linked list has a cycle and find the starting point.",
                    "Implement a function to find the kth largest element in an unsorted array."
                ],
                QuestionCategory.TECHNICAL_SYSTEM_DESIGN: [
                    "Design a URL shortening service like bit.ly. Consider scalability and reliability.",
                    "How would you architect a chat application that supports millions of users?",
                    "Design a distributed cache system. Explain your approach to consistency and availability.",
                    "How would you design a recommendation system for an e-commerce platform?",
                    "Explain how you would scale a web application from 1000 to 1 million users.",
                    "Design a real-time analytics system for tracking user behavior on a website.",
                    "How would you architect a file storage system like Dropbox or Google Drive?"
                ]
            },
            InterviewType.HR: {
                QuestionCategory.HR_GENERAL: [
                    "Why are you interested in this position and our company?",
                    "What are your greatest strengths and how do they apply to this role?",
                    "What is your biggest weakness and how are you working to improve it?",
                    "Where do you see yourself in 5 years?",
                    "Why are you looking to leave your current role?",
                    "What motivates you in your work?",
                    "How do you handle stress and pressure?",
                    "What type of work environment do you thrive in?"
                ],
                QuestionCategory.COMPANY_SPECIFIC: [
                    "What do you know about our company's mission and values?",
                    "How would you contribute to our company culture?",
                    "What challenges do you think our industry is facing?",
                    "Why do you want to work for us specifically?",
                    "What do you think sets us apart from our competitors?"
                ]
            },
            InterviewType.MIXED: {
                QuestionCategory.BEHAVIORAL: [
                    "Tell me about a technical project you're proud of and the challenges you faced.",
                    "Describe a time when you had to explain a complex technical concept to a non-technical person.",
                    "Give me an example of when you had to debug a difficult problem under pressure."
                ],
                QuestionCategory.TECHNICAL_CODING: [
                    "Walk me through your approach to solving this coding problem step by step.",
                    "How would you optimize this solution for better performance?",
                    "What edge cases would you consider for this implementation?"
                ]
            }
        }
        
        # Scenario-specific evaluation criteria
        self.evaluation_criteria = {
            InterviewType.BEHAVIORAL: [
                "Uses STAR method (Situation, Task, Action, Result)",
                "Provides specific examples and details",
                "Demonstrates self-awareness and learning",
                "Shows problem-solving skills",
                "Exhibits relevant soft skills"
            ],
            InterviewType.TECHNICAL: [
                "Demonstrates technical knowledge and accuracy",
                "Explains thought process clearly",
                "Considers edge cases and constraints",
                "Discusses time and space complexity",
                "Shows problem-solving approach"
            ],
            InterviewType.HR: [
                "Shows genuine interest and research",
                "Aligns with company values and culture",
                "Demonstrates career planning and goals",
                "Exhibits professionalism and communication skills",
                "Provides honest and thoughtful responses"
            ]
        }
    
    async def create_interview_session(
        self, 
        user_id: UUID, 
        session_data: InterviewSessionCreate
    ) -> InterviewSession:
        """Create a new interview session with AI-generated questions."""
        
        # Create the interview session
        session = InterviewSession(
            user_id=user_id,
            interview_type=session_data.interview_type,
            title=session_data.title,
            description=session_data.description,
            company_name=session_data.company_name,
            position_title=session_data.position_title,
            total_duration=session_data.total_duration,
            question_count=session_data.question_count,
            difficulty_level=session_data.difficulty_level,
            adaptive_mode=session_data.adaptive_mode,
            performance_threshold=session_data.performance_threshold,
            question_categories=session_data.question_categories,
            company_tags=session_data.company_tags or [],
            topic_tags=session_data.topic_tags or [],
            enable_video_recording=session_data.enable_video_recording,
            enable_audio_recording=session_data.enable_audio_recording,
            scheduled_time=session_data.scheduled_time
        )
        
        self.db.add(session)
        await self.db.flush()  # Get the session ID
        
        # Generate initial questions
        questions = await self._generate_interview_questions(session)
        
        # Add questions to session
        for question in questions:
            question.session_id = session.id
            self.db.add(question)
        
        await self.db.commit()
        await self.db.refresh(session)
        
        logger.info(f"Created interview session {session.id} with {len(questions)} questions")
        return session
    
    async def create_scenario_based_interview(
        self,
        user_id: UUID,
        interview_type: InterviewType,
        company_name: Optional[str] = None,
        position_title: Optional[str] = None,
        difficulty_level: DifficultyLevel = DifficultyLevel.MEDIUM,
        duration_minutes: int = 45
    ) -> InterviewSession:
        """Create a scenario-based interview session with predefined structure."""
        
        # Define scenario-specific configurations
        scenario_configs = {
            InterviewType.BEHAVIORAL: {
                "title": f"Behavioral Interview - {position_title or 'General Position'}",
                "description": "Practice behavioral questions using the STAR method",
                "categories": [QuestionCategory.BEHAVIORAL, QuestionCategory.SITUATIONAL],
                "question_count": 8,
                "topic_tags": ["leadership", "teamwork", "problem-solving", "communication"]
            },
            InterviewType.TECHNICAL: {
                "title": f"Technical Interview - {position_title or 'Software Engineer'}",
                "description": "Practice coding problems and system design questions",
                "categories": [QuestionCategory.TECHNICAL_CODING, QuestionCategory.TECHNICAL_SYSTEM_DESIGN],
                "question_count": 6,
                "topic_tags": ["algorithms", "data-structures", "system-design", "coding"]
            },
            InterviewType.HR: {
                "title": f"HR Interview - {company_name or 'General Company'}",
                "description": "Practice HR and culture fit questions",
                "categories": [QuestionCategory.HR_GENERAL, QuestionCategory.COMPANY_SPECIFIC],
                "question_count": 10,
                "topic_tags": ["culture-fit", "motivation", "career-goals", "company-knowledge"]
            },
            InterviewType.MIXED: {
                "title": f"Full Interview Loop - {position_title or 'Software Engineer'}",
                "description": "Complete interview experience with multiple rounds",
                "categories": [
                    QuestionCategory.BEHAVIORAL, 
                    QuestionCategory.TECHNICAL_CODING,
                    QuestionCategory.HR_GENERAL
                ],
                "question_count": 12,
                "topic_tags": ["comprehensive", "full-loop", "mixed-format"]
            }
        }
        
        config = scenario_configs.get(interview_type, scenario_configs[InterviewType.BEHAVIORAL])
        
        # Create session data
        session_data = InterviewSessionCreate(
            interview_type=interview_type,
            title=config["title"],
            description=config["description"],
            company_name=company_name,
            position_title=position_title,
            total_duration=duration_minutes,
            question_count=config["question_count"],
            difficulty_level=difficulty_level,
            adaptive_mode=True,
            performance_threshold=0.7,
            question_categories=config["categories"],
            topic_tags=config["topic_tags"],
            enable_video_recording=True,
            enable_audio_recording=True
        )
        
        return await self.create_interview_session(user_id, session_data)
    
    async def start_interview(self, session_id: UUID, user_id: UUID) -> InterviewSession:
        """Start an interview session."""
        
        session = await self._get_session(session_id, user_id)
        if session.status != InterviewStatus.SCHEDULED:
            raise ValueError(f"Cannot start interview in status: {session.status}")
        
        session.start_interview()
        await self.db.commit()
        
        logger.info(f"Started interview session {session_id}")
        return session
    
    async def get_next_question(
        self, 
        session_id: UUID, 
        user_id: UUID
    ) -> Optional[InterviewQuestion]:
        """Get the next question in the interview sequence."""
        
        session = await self._get_session(session_id, user_id, include_questions=True)
        
        if session.status != InterviewStatus.IN_PROGRESS:
            raise ValueError(f"Interview not in progress: {session.status}")
        
        if session.current_question_index >= len(session.questions):
            # Interview completed
            await self._complete_interview(session)
            return None
        
        # Get current question
        current_question = session.questions[session.current_question_index]
        current_question.asked_at = datetime.now(timezone.utc)
        
        # Check if we need adaptive questioning
        if session.adaptive_mode and session.current_question_index > 0:
            await self._adjust_difficulty_if_needed(session)
        
        await self.db.commit()
        return current_question
    
    async def submit_response(
        self,
        session_id: UUID,
        question_id: UUID,
        user_id: UUID,
        response_data: InterviewResponseCreate,
        audio_file_path: Optional[str] = None,
        video_file_path: Optional[str] = None
    ) -> InterviewResponse:
        """Submit and analyze an interview response."""
        
        session = await self._get_session(session_id, user_id)
        
        # Create response record
        response = InterviewResponse(
            session_id=session_id,
            question_id=question_id,
            response_text=response_data.response_text,
            response_duration=response_data.response_duration,
            thinking_time=response_data.thinking_time,
            audio_file_url=audio_file_path,
            video_file_url=video_file_path
        )
        
        self.db.add(response)
        await self.db.flush()
        
        # Process audio if available for enhanced analysis
        if audio_file_path:
            await self._process_audio_response(response, audio_file_path)
        
        # Process video if available (extract audio for analysis)
        if video_file_path and not audio_file_path:
            await self._process_video_response(response, video_file_path)
        
        # Analyze response with AI
        await self._analyze_response(response, session)
        
        # Update session progress
        session.current_question_index += 1
        session.questions_asked.append(question_id)
        
        await self.db.commit()
        
        logger.info(f"Submitted response for question {question_id} in session {session_id}")
        return response
    
    async def pause_interview(self, session_id: UUID, user_id: UUID) -> InterviewSession:
        """Pause an active interview."""
        
        session = await self._get_session(session_id, user_id)
        if session.status != InterviewStatus.IN_PROGRESS:
            raise ValueError(f"Cannot pause interview in status: {session.status}")
        
        session.pause_interview()
        await self.db.commit()
        
        logger.info(f"Paused interview session {session_id}")
        return session
    
    async def resume_interview(self, session_id: UUID, user_id: UUID) -> InterviewSession:
        """Resume a paused interview."""
        
        session = await self._get_session(session_id, user_id)
        if session.status != InterviewStatus.PAUSED:
            raise ValueError(f"Cannot resume interview in status: {session.status}")
        
        session.resume_interview()
        await self.db.commit()
        
        logger.info(f"Resumed interview session {session_id}")
        return session
    
    async def complete_interview(self, session_id: UUID, user_id: UUID) -> InterviewSession:
        """Complete an interview and generate final analysis."""
        
        session = await self._get_session(session_id, user_id, include_responses=True)
        await self._complete_interview(session)
        
        logger.info(f"Completed interview session {session_id}")
        return session
    
    async def _generate_interview_questions(
        self, 
        session: InterviewSession
    ) -> List[InterviewQuestion]:
        """Generate AI-powered interview questions based on session configuration."""
        
        questions = []
        questions_per_category = self._distribute_questions_by_category(
            session.question_count, 
            session.question_categories
        )
        
        for category, count in questions_per_category.items():
            category_questions = await self._generate_questions_for_category(
                session, category, count
            )
            questions.extend(category_questions)
        
        # Randomize question order if needed
        if session.interview_type == InterviewType.MIXED:
            random.shuffle(questions)
        
        # Set question order
        for i, question in enumerate(questions):
            question.question_order = i + 1
        
        return questions
    
    async def _generate_questions_for_category(
        self,
        session: InterviewSession,
        category: QuestionCategory,
        count: int
    ) -> List[InterviewQuestion]:
        """Generate questions for a specific category using AI."""
        
        # Prepare generation context
        context = {
            "interview_type": session.interview_type,
            "category": category,
            "difficulty_level": session.difficulty_level,
            "company_name": session.company_name,
            "position_title": session.position_title,
            "topic_tags": session.topic_tags,
            "count": count
        }
        
        # Generate questions using Groq API
        try:
            generated_questions = await self._call_groq_for_questions(context)
        except Exception as e:
            logger.warning(f"AI generation failed, using templates: {e}")
            generated_questions = self._generate_template_questions(context)
        
        # Create InterviewQuestion objects
        questions = []
        for i, q_data in enumerate(generated_questions[:count]):
            question = InterviewQuestion(
                question_text=q_data["question_text"],
                category=category,
                difficulty_level=session.difficulty_level,
                expected_duration=q_data.get("expected_duration", 120),
                question_order=0,  # Will be set later
                generated_by_ai=q_data.get("generated_by_ai", True),
                generation_prompt=q_data.get("generation_prompt"),
                generation_context=context,
                context_information=q_data.get("context_information"),
                evaluation_criteria=q_data.get("evaluation_criteria", []),
                sample_answers=q_data.get("sample_answers", [])
            )
            questions.append(question)
        
        return questions
    
    async def _call_groq_for_questions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Call Groq API to generate interview questions."""
        
        try:
            questions = await self.groq_client.generate_interview_questions(
                interview_type=context["interview_type"],
                category=context["category"],
                difficulty_level=context["difficulty_level"],
                company_name=context.get("company_name"),
                position_title=context.get("position_title"),
                topic_tags=context.get("topic_tags", []),
                count=context["count"]
            )
            
            return questions
            
        except Exception as e:
            logger.error(f"Groq API call failed: {e}")
            raise
    
    def _build_question_generation_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for AI question generation."""
        
        prompt = f"""
Generate {context['count']} interview questions with the following specifications:

Interview Type: {context['interview_type']}
Category: {context['category']}
Difficulty Level: {context['difficulty_level']}
Company: {context.get('company_name', 'Generic')}
Position: {context.get('position_title', 'Software Engineer')}
Topics: {', '.join(context.get('topic_tags', []))}

Requirements:
1. Questions should be realistic and commonly asked in interviews
2. Difficulty should match the specified level
3. Include context information and evaluation criteria
4. Provide sample answer points (not full answers)
5. Estimate expected response duration in seconds

Return JSON format:
{{
  "questions": [
    {{
      "question_text": "Your question here",
      "expected_duration": 120,
      "context_information": "Background context if needed",
      "evaluation_criteria": ["Criterion 1", "Criterion 2"],
      "sample_answers": ["Key point 1", "Key point 2"],
      "generated_by_ai": true,
      "generation_prompt": "This prompt"
    }}
  ]
}}
"""
        return prompt.strip()
    
    def _generate_template_questions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate questions using predefined templates as fallback."""
        
        interview_type = context["interview_type"]
        category = context["category"]
        count = context["count"]
        
        templates = self.question_templates.get(interview_type, {}).get(category, [])
        if not templates:
            # Generic fallback
            templates = [
                "Tell me about your experience with {topic}.",
                "How would you approach {scenario}?",
                "Describe a challenging situation involving {context}."
            ]
        
        questions = []
        for i in range(count):
            template = random.choice(templates)
            
            # Simple template substitution
            question_text = template.format(
                company_name=context.get("company_name", "the company"),
                position_title=context.get("position_title", "this role"),
                situation="a challenging project",
                challenge="work under pressure",
                scenario="conflicting priorities",
                topic="relevant technologies"
            )
            
            questions.append({
                "question_text": question_text,
                "expected_duration": 120,
                "context_information": None,
                "evaluation_criteria": ["Clarity", "Relevance", "Detail"],
                "sample_answers": [],
                "generated_by_ai": False,
                "generation_prompt": None
            })
        
        return questions
    
    def _distribute_questions_by_category(
        self, 
        total_questions: int, 
        categories: List[QuestionCategory]
    ) -> Dict[QuestionCategory, int]:
        """Distribute questions evenly across categories."""
        
        if not categories:
            return {}
        
        base_count = total_questions // len(categories)
        remainder = total_questions % len(categories)
        
        distribution = {}
        for i, category in enumerate(categories):
            count = base_count + (1 if i < remainder else 0)
            distribution[category] = count
        
        return distribution
    
    async def _process_audio_response(
        self, 
        response: InterviewResponse, 
        audio_file_path: str
    ):
        """Process audio response for comprehensive speech analysis."""
        
        try:
            # Transcribe audio using Whisper
            transcript, confidence, detailed_results = await self.speech_processor.transcribe_audio(audio_file_path)
            
            if transcript:
                # Update response with transcription
                if not response.response_text:  # Only update if no text was provided
                    response.response_text = transcript
                response.transcript_confidence = confidence
                
                # Extract word timestamps for detailed analysis
                word_timestamps = detailed_results.get("word_timestamps", [])
                
                # Perform comprehensive speech analysis
                speech_analysis = await self.speech_processor.analyze_speech_patterns(
                    transcript, word_timestamps
                )
                
                # Update response with speech metrics
                response.speech_pace = speech_analysis.get("words_per_minute", 0)
                response.filler_word_count = speech_analysis.get("filler_word_count", 0)
                response.pause_count = len([p for p in speech_analysis.get("filler_words_detected", []) 
                                          if "pause" in p.get("word", "").lower()])
                
                # Analyze language quality
                language_analysis = await self.speech_processor.analyze_language_quality(transcript)
                
                # Calculate confidence level based on speech patterns
                response.confidence_level = self._calculate_speech_confidence(
                    speech_analysis, language_analysis
                )
                
                # Analyze sentiment (basic implementation)
                response.sentiment_score = self._analyze_sentiment(transcript)
                
                logger.info(f"Audio analysis completed for response {response.id}")
                
        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
    
    async def _process_video_response(
        self, 
        response: InterviewResponse, 
        video_file_path: str
    ):
        """Process video response by extracting and analyzing audio."""
        
        try:
            # Extract audio from video file
            audio_file_path = await self._extract_audio_from_video(video_file_path)
            
            if audio_file_path:
                # Process the extracted audio
                await self._process_audio_response(response, audio_file_path)
                
                # TODO: Add video analysis features like:
                # - Eye contact detection
                # - Facial expression analysis
                # - Body language assessment
                # - Gesture recognition
                
                logger.info(f"Video processing completed for response {response.id}")
                
        except Exception as e:
            logger.error(f"Video processing failed: {e}")
    
    async def _extract_audio_from_video(self, video_file_path: str) -> Optional[str]:
        """Extract audio track from video file."""
        
        try:
            import subprocess
            import tempfile
            import os
            
            # Create temporary audio file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                audio_output_path = temp_audio.name
            
            # Use ffmpeg to extract audio
            cmd = [
                "ffmpeg", "-i", video_file_path,
                "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
                audio_output_path, "-y"
            ]
            
            # Run extraction in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                subprocess.run, 
                cmd, 
                subprocess.PIPE, 
                subprocess.PIPE
            )
            
            if result.returncode == 0 and os.path.exists(audio_output_path):
                return audio_output_path
            else:
                logger.error(f"Audio extraction failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting audio from video: {e}")
            return None
    
    def _calculate_speech_confidence(
        self, 
        speech_analysis: Dict, 
        language_analysis: Dict
    ) -> float:
        """Calculate confidence level based on speech patterns."""
        
        # Factors that indicate confidence
        wpm = speech_analysis.get("words_per_minute", 0)
        filler_percentage = speech_analysis.get("filler_word_percentage", 0)
        pause_frequency = speech_analysis.get("pause_frequency", 0)
        grammar_score = language_analysis.get("grammar_score", 0.5)
        
        # Optimal speaking rate indicates confidence
        wpm_confidence = 1.0 if 120 <= wpm <= 180 else max(0.3, min(wpm / 150, 180 / wpm))
        
        # Fewer fillers indicate more confidence
        filler_confidence = max(0.0, 1.0 - (filler_percentage / 20))
        
        # Moderate pausing is good, too many or too few indicates nervousness
        pause_confidence = 1.0 if 2 <= pause_frequency <= 6 else max(0.3, 1.0 - abs(pause_frequency - 4) / 10)
        
        # Combine factors
        confidence = (
            wpm_confidence * 0.3 + 
            filler_confidence * 0.3 + 
            pause_confidence * 0.2 + 
            grammar_score * 0.2
        )
        
        return max(0.0, min(1.0, confidence))
    
    def _analyze_sentiment(self, text: str) -> float:
        """Basic sentiment analysis of response text."""
        
        try:
            # Simple keyword-based sentiment analysis
            positive_words = {
                'excited', 'passionate', 'love', 'enjoy', 'great', 'excellent', 
                'amazing', 'wonderful', 'fantastic', 'good', 'positive', 'confident'
            }
            
            negative_words = {
                'difficult', 'challenging', 'hard', 'struggle', 'problem', 'issue',
                'worried', 'concerned', 'nervous', 'anxious', 'bad', 'terrible'
            }
            
            words = text.lower().split()
            positive_count = sum(1 for word in words if word in positive_words)
            negative_count = sum(1 for word in words if word in negative_words)
            
            total_sentiment_words = positive_count + negative_count
            
            if total_sentiment_words == 0:
                return 0.0  # Neutral
            
            # Calculate sentiment score (-1 to 1)
            sentiment = (positive_count - negative_count) / total_sentiment_words
            return max(-1.0, min(1.0, sentiment))
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return 0.0
    
    async def _analyze_response(
        self, 
        response: InterviewResponse, 
        session: InterviewSession
    ):
        """Analyze interview response using AI."""
        
        if not response.response_text:
            return
        
        try:
            # Get question for context
            question = await self.db.get(InterviewQuestion, response.question_id)
            
            # Prepare interview context
            interview_context = {
                "interview_type": session.interview_type,
                "company_name": session.company_name,
                "position_title": session.position_title,
                "difficulty_level": session.difficulty_level
            }
            
            # Analyze with Groq
            analysis_data = await self.groq_client.analyze_interview_response(
                question_text=question.question_text,
                response_text=response.response_text,
                question_category=question.category,
                evaluation_criteria=question.evaluation_criteria,
                interview_context=interview_context
            )
            
            # Update response with analysis
            response.content_relevance = analysis_data.get("content_relevance", 0.5)
            response.technical_accuracy = analysis_data.get("technical_accuracy", 0.5)
            response.structure_score = analysis_data.get("structure_score", 0.5)
            response.overall_score = analysis_data.get("overall_score", 50.0)
            response.communication_score = analysis_data.get("communication_score", 50.0)
            response.content_score = analysis_data.get("content_score", 50.0)
            response.ai_feedback = analysis_data.get("feedback", "")
            response.improvement_suggestions = analysis_data.get("improvement_suggestions", [])
            response.strengths = analysis_data.get("strengths", [])
            response.weaknesses = analysis_data.get("weaknesses", [])
            response.analysis_version = "v1.0"
            response.analyzed_at = datetime.now(timezone.utc)
            
        except Exception as e:
            logger.error(f"Response analysis failed: {e}")
            # Set default scores
            response.overall_score = 50.0
            response.communication_score = 50.0
            response.content_score = 50.0
            response.ai_feedback = "Analysis temporarily unavailable."
    
    def _build_response_analysis_prompt(
        self, 
        question: InterviewQuestion, 
        response: InterviewResponse, 
        session: InterviewSession
    ) -> str:
        """Build prompt for AI response analysis."""
        
        prompt = f"""
Analyze this interview response:

Question: {question.question_text}
Category: {question.category}
Expected Duration: {question.expected_duration} seconds
Evaluation Criteria: {', '.join(question.evaluation_criteria)}

Response: {response.response_text}
Response Duration: {response.response_duration} seconds
Thinking Time: {response.thinking_time} seconds

Interview Context:
- Type: {session.interview_type}
- Company: {session.company_name or 'Generic'}
- Position: {session.position_title or 'Software Engineer'}

Analyze and score (0-1 for relevance/accuracy/structure, 0-100 for scores):
1. Content relevance to the question
2. Technical accuracy (if applicable)
3. Response structure and clarity
4. Overall communication effectiveness

Provide specific, actionable feedback and suggestions.

Return JSON format:
{{
  "content_relevance": 0.8,
  "technical_accuracy": 0.7,
  "structure_score": 0.9,
  "overall_score": 85.0,
  "communication_score": 80.0,
  "content_score": 90.0,
  "feedback": "Detailed feedback here",
  "improvement_suggestions": ["Suggestion 1", "Suggestion 2"],
  "strengths": ["Strength 1", "Strength 2"],
  "weaknesses": ["Weakness 1", "Weakness 2"]
}}
"""
        return prompt.strip()
    
    async def _adjust_difficulty_if_needed(self, session: InterviewSession):
        """Adjust question difficulty based on performance (adaptive questioning)."""
        
        if not session.adaptive_mode:
            return
        
        # Get recent responses for performance analysis
        recent_responses = await self.db.execute(
            select(InterviewResponse)
            .where(InterviewResponse.session_id == session.id)
            .where(InterviewResponse.overall_score.isnot(None))
            .order_by(InterviewResponse.created_at.desc())
            .limit(3)
        )
        responses = recent_responses.scalars().all()
        
        if len(responses) < 2:
            return
        
        # Calculate average performance
        avg_score = sum(r.overall_score for r in responses) / len(responses)
        performance_ratio = avg_score / 100.0
        
        # Get the most recent response for context
        latest_response = responses[0]
        latest_question = await self.db.get(InterviewQuestion, latest_response.question_id)
        
        # Generate adaptive follow-up question if needed
        if abs(performance_ratio - session.performance_threshold) > 0.1:
            await self._generate_adaptive_followup_question(
                session, latest_question, latest_response, performance_ratio
            )
    
    async def _generate_adaptive_followup_question(
        self,
        session: InterviewSession,
        previous_question: InterviewQuestion,
        previous_response: InterviewResponse,
        performance_ratio: float
    ):
        """Generate adaptive follow-up question based on performance."""
        
        try:
            # Prepare context for follow-up generation
            interview_context = {
                "interview_type": session.interview_type,
                "category": previous_question.category,
                "company_name": session.company_name,
                "position_title": session.position_title,
                "difficulty_level": session.difficulty_level
            }
            
            # Generate follow-up question using AI
            followup_data = await self.groq_client.generate_followup_question(
                original_question=previous_question.question_text,
                user_response=previous_response.response_text,
                performance_score=performance_ratio,
                interview_context=interview_context
            )
            
            if followup_data:
                # Create and add follow-up question
                followup_question = InterviewQuestion(
                    session_id=session.id,
                    question_text=followup_data["question_text"],
                    category=previous_question.category,
                    difficulty_level=session.difficulty_level,
                    expected_duration=followup_data.get("expected_duration", 90),
                    question_order=len(session.questions) + 1,
                    is_followup=True,
                    parent_question_id=previous_question.id,
                    generated_by_ai=True,
                    context_information=followup_data.get("context_information", ""),
                    evaluation_criteria=followup_data.get("evaluation_criteria", []),
                    difficulty_adjustment=followup_data.get("difficulty_adjustment", 0.0)
                )
                
                self.db.add(followup_question)
                session.question_count += 1  # Increase total question count
                
                logger.info(f"Generated adaptive follow-up question for session {session.id}")
                
        except Exception as e:
            logger.error(f"Failed to generate adaptive follow-up question: {e}")
    
    async def _complete_interview(self, session: InterviewSession):
        """Complete interview and generate final analysis."""
        
        session.complete_interview()
        
        # Calculate overall scores
        if session.responses:
            scores = [r.overall_score for r in session.responses if r.overall_score]
            if scores:
                session.overall_score = sum(scores) / len(scores)
            
            # Calculate category-specific scores
            comm_scores = [r.communication_score for r in session.responses if r.communication_score]
            if comm_scores:
                session.communication_score = sum(comm_scores) / len(comm_scores)
            
            content_scores = [r.content_score for r in session.responses if r.content_score]
            if content_scores:
                # This could be technical_score or behavioral_score based on interview type
                if session.interview_type == InterviewType.TECHNICAL:
                    session.technical_score = sum(content_scores) / len(content_scores)
                else:
                    session.behavioral_score = sum(content_scores) / len(content_scores)
        
        # Generate comprehensive feedback
        await self._generate_final_feedback(session)
    
    async def _generate_final_feedback(self, session: InterviewSession):
        """Generate comprehensive interview feedback using AI."""
        
        try:
            # Prepare session summary for analysis
            summary_data = {
                "interview_type": session.interview_type,
                "total_questions": len(session.responses),
                "overall_score": session.overall_score,
                "communication_score": session.communication_score,
                "technical_score": session.technical_score,
                "behavioral_score": session.behavioral_score,
                "responses": [
                    {
                        "question_category": r.question.category if r.question else "unknown",
                        "score": r.overall_score,
                        "feedback": r.ai_feedback
                    }
                    for r in session.responses
                ]
            }
            
            feedback_prompt = f"""
Generate comprehensive interview feedback based on this session:

{json.dumps(summary_data, indent=2)}

Provide:
1. Overall performance summary
2. Strengths and areas for improvement
3. Specific recommendations for each category
4. Action plan for improvement

Return JSON format with feedback and suggestions.
"""
            
            feedback_result = await self.groq_client.generate_response(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert interview coach providing comprehensive feedback."
                    },
                    {
                        "role": "user",
                        "content": feedback_prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            feedback_data = json.loads(feedback_result)
            session.ai_feedback = feedback_data
            session.improvement_suggestions = feedback_data.get("improvement_suggestions", [])
            
        except Exception as e:
            logger.error(f"Final feedback generation failed: {e}")
    
    async def _get_session(
        self, 
        session_id: UUID, 
        user_id: UUID, 
        include_questions: bool = False,
        include_responses: bool = False
    ) -> InterviewSession:
        """Get interview session with optional related data."""
        
        query = select(InterviewSession).where(
            and_(
                InterviewSession.id == session_id,
                InterviewSession.user_id == user_id
            )
        )
        
        if include_questions:
            query = query.options(selectinload(InterviewSession.questions))
        
        if include_responses:
            query = query.options(
                selectinload(InterviewSession.responses).selectinload(InterviewResponse.question)
            )
        
        result = await self.db.execute(query)
        session = result.scalar_one_or_none()
        
        if not session:
            raise ValueError(f"Interview session {session_id} not found")
        
        return session