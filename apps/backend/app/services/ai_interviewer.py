"""AI Interviewer service for real-time interview interactions."""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.interview import (
    InterviewSession, InterviewQuestion, InterviewResponse,
    InterviewType, QuestionCategory
)
from app.models.user import User
from app.schemas.interview import QuestionGenerationRequest
from app.services.groq_client import GroqClient
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIInterviewer:
    """AI-powered interviewer for real-time interview interactions."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.groq_client = GroqClient()
        
        # AI interviewer personality and behavior settings
        self.interviewer_persona = {
            "name": "Alex",
            "style": "professional yet friendly",
            "approach": "encouraging and constructive",
            "expertise": "experienced technical recruiter and interview coach"
        }
    
    async def generate_introduction(
        self, 
        session: InterviewSession, 
        first_question: InterviewQuestion
    ) -> Dict[str, Any]:
        """Generate AI interviewer introduction for the session."""
        
        try:
            context = {
                "interview_type": session.interview_type,
                "company_name": session.company_name or "our company",
                "position_title": session.position_title or "this position",
                "duration": session.total_duration,
                "question_count": session.question_count
            }
            
            prompt = self._build_introduction_prompt(context)
            
            messages = [
                {
                    "role": "system",
                    "content": f"""You are {self.interviewer_persona['name']}, an {self.interviewer_persona['expertise']}. 
                    Your style is {self.interviewer_persona['style']} and your approach is {self.interviewer_persona['approach']}.
                    You are conducting a {session.interview_type} interview. Keep responses natural and conversational."""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            introduction_text = await self.groq_client.generate_response(
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )
            
            return {
                "text": introduction_text,
                "interviewer_name": self.interviewer_persona["name"],
                "session_overview": {
                    "type": session.interview_type,
                    "duration_minutes": session.total_duration,
                    "question_count": session.question_count,
                    "adaptive_mode": session.adaptive_mode
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating introduction: {e}")
            return {
                "text": f"Hello! I'm {self.interviewer_persona['name']}, and I'll be conducting your {session.interview_type} interview today. We have {session.question_count} questions planned for the next {session.total_duration} minutes. Let's begin!",
                "interviewer_name": self.interviewer_persona["name"],
                "session_overview": {
                    "type": session.interview_type,
                    "duration_minutes": session.total_duration,
                    "question_count": session.question_count,
                    "adaptive_mode": session.adaptive_mode
                }
            }
    
    def _build_introduction_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for generating interview introduction."""
        
        return f"""
Generate a warm, professional introduction for a {context['interview_type']} interview.

Context:
- Company: {context['company_name']}
- Position: {context['position_title']}
- Duration: {context['duration']} minutes
- Questions: {context['question_count']}

Requirements:
1. Welcome the candidate warmly
2. Introduce yourself as the interviewer
3. Briefly explain the interview format and duration
4. Set a positive, encouraging tone
5. Keep it concise (2-3 sentences)
6. End by asking if they're ready to begin

Make it sound natural and conversational, not scripted.
"""
    
    async def generate_immediate_feedback(
        self, 
        response: InterviewResponse, 
        session_id: UUID
    ) -> Dict[str, Any]:
        """Generate immediate AI feedback after each response."""
        
        try:
            # Get question and session context
            question = await self.db.get(InterviewQuestion, response.question_id)
            session = await self.db.get(InterviewSession, session_id)
            
            if not question or not session:
                return {"text": "Thank you for your response. Let's continue."}
            
            context = {
                "question_text": question.question_text,
                "question_category": question.category,
                "response_text": response.response_text or "",
                "response_duration": response.response_duration,
                "overall_score": response.overall_score or 50,
                "communication_score": response.communication_score or 50,
                "content_score": response.content_score or 50,
                "interview_type": session.interview_type
            }
            
            prompt = self._build_immediate_feedback_prompt(context)
            
            messages = [
                {
                    "role": "system",
                    "content": f"""You are {self.interviewer_persona['name']}, providing immediate, encouraging feedback during an interview.
                    Be supportive and constructive. Keep feedback brief and positive while noting areas for improvement.
                    Sound like a real interviewer, not an AI system."""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            feedback_text = await self.groq_client.generate_response(
                messages=messages,
                max_tokens=200,
                temperature=0.6
            )
            
            return {
                "text": feedback_text,
                "tone": "encouraging",
                "highlights": self._extract_response_highlights(response),
                "suggestions": response.improvement_suggestions or []
            }
            
        except Exception as e:
            logger.error(f"Error generating immediate feedback: {e}")
            return {
                "text": "Thank you for that response. I can see you put thought into your answer.",
                "tone": "neutral",
                "highlights": [],
                "suggestions": []
            }
    
    def _build_immediate_feedback_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for immediate feedback generation."""
        
        return f"""
Provide brief, encouraging feedback for this interview response:

Question: {context['question_text']}
Category: {context['question_category']}
Response: {context['response_text'][:500]}...
Duration: {context['response_duration']} seconds
Scores: Overall {context['overall_score']}/100, Communication {context['communication_score']}/100

Requirements:
1. Be encouraging and supportive
2. Acknowledge something positive about the response
3. Keep it brief (1-2 sentences)
4. Sound natural and conversational
5. Don't mention specific scores
6. Focus on what they did well

Examples:
- "Great example! I appreciate how you structured your response using specific details."
- "That's a thoughtful approach. Your explanation was clear and well-organized."
- "Excellent point about [specific aspect]. I can see you have good experience with this."

Generate similar encouraging feedback for this response.
"""
    
    async def generate_question_transition(
        self, 
        previous_response: InterviewResponse, 
        next_question: InterviewQuestion
    ) -> Dict[str, Any]:
        """Generate smooth transition between questions."""
        
        try:
            context = {
                "previous_category": (await self.db.get(InterviewQuestion, previous_response.question_id)).category,
                "next_category": next_question.category,
                "next_question": next_question.question_text,
                "response_quality": "good" if (previous_response.overall_score or 50) >= 70 else "average"
            }
            
            prompt = self._build_transition_prompt(context)
            
            messages = [
                {
                    "role": "system",
                    "content": f"""You are {self.interviewer_persona['name']}, smoothly transitioning between interview questions.
                    Keep transitions natural and brief. Maintain interview flow and candidate comfort."""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            transition_text = await self.groq_client.generate_response(
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )
            
            return {
                "text": transition_text,
                "transition_type": "question_to_question",
                "category_change": context["previous_category"] != context["next_category"]
            }
            
        except Exception as e:
            logger.error(f"Error generating question transition: {e}")
            return {
                "text": "Great! Let's move on to the next question.",
                "transition_type": "simple",
                "category_change": False
            }
    
    def _build_transition_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for question transition generation."""
        
        category_change_note = ""
        if context["previous_category"] != context["next_category"]:
            category_change_note = f"We're moving from {context['previous_category']} to {context['next_category']} questions."
        
        return f"""
Generate a brief, natural transition to the next interview question.

Context:
- Previous question category: {context['previous_category']}
- Next question category: {context['next_category']}
- Response quality: {context['response_quality']}
{category_change_note}

Requirements:
1. Keep it very brief (1 sentence)
2. Sound natural and conversational
3. Maintain positive energy
4. Don't repeat the question (it will be shown separately)

Examples:
- "Perfect! Now let's shift gears a bit."
- "Excellent. I'd like to explore another area with you."
- "Great response. Let's move on to something different."

Generate a similar brief transition.
"""
    
    async def generate_completion_summary(self, session: InterviewSession) -> Dict[str, Any]:
        """Generate interview completion summary and encouragement."""
        
        try:
            context = {
                "interview_type": session.interview_type,
                "questions_answered": session.current_question_index,
                "total_questions": session.question_count,
                "overall_score": session.overall_score or 50,
                "duration": session.duration_minutes or session.total_duration
            }
            
            prompt = self._build_completion_prompt(context)
            
            messages = [
                {
                    "role": "system",
                    "content": f"""You are {self.interviewer_persona['name']}, concluding an interview on a positive note.
                    Be encouraging and professional. Thank the candidate and provide closure."""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            summary_text = await self.groq_client.generate_response(
                messages=messages,
                max_tokens=250,
                temperature=0.6
            )
            
            return {
                "text": summary_text,
                "completion_type": "interview_finished",
                "next_steps": [
                    "Review your detailed performance analysis",
                    "Check your personalized improvement plan",
                    "Practice areas identified for development",
                    "Schedule follow-up practice sessions if needed"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error generating completion summary: {e}")
            return {
                "text": f"Thank you for completing the {session.interview_type} interview! You answered {session.current_question_index} questions and showed great effort throughout. Please review your detailed feedback and performance analysis.",
                "completion_type": "interview_finished",
                "next_steps": [
                    "Review your detailed performance analysis",
                    "Check your personalized improvement plan"
                ]
            }
    
    def _build_completion_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for interview completion summary."""
        
        return f"""
Generate a warm, professional conclusion for a completed interview.

Context:
- Interview type: {context['interview_type']}
- Questions answered: {context['questions_answered']}/{context['total_questions']}
- Duration: {context['duration']} minutes
- Performance level: {'strong' if context['overall_score'] >= 75 else 'good' if context['overall_score'] >= 60 else 'developing'}

Requirements:
1. Thank the candidate for their time and effort
2. Acknowledge their participation positively
3. Mention that detailed feedback will be available
4. Keep it encouraging and professional
5. Provide closure to the interview experience
6. 2-3 sentences maximum

Sound like a real interviewer wrapping up, not an AI system.
"""
    
    async def generate_hint(self, question_id: UUID, session_id: UUID) -> Dict[str, Any]:
        """Generate helpful hint for a specific question."""
        
        try:
            question = await self.db.get(InterviewQuestion, question_id)
            session = await self.db.get(InterviewSession, session_id)
            
            if not question or not session:
                return {"text": "Think about your past experiences and try to provide specific examples."}
            
            context = {
                "question_text": question.question_text,
                "question_category": question.category,
                "interview_type": session.interview_type,
                "evaluation_criteria": question.evaluation_criteria or []
            }
            
            prompt = self._build_hint_prompt(context)
            
            messages = [
                {
                    "role": "system",
                    "content": f"""You are {self.interviewer_persona['name']}, providing a helpful hint during an interview.
                    Be supportive and guide the candidate without giving away the answer."""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            hint_text = await self.groq_client.generate_response(
                messages=messages,
                max_tokens=150,
                temperature=0.6
            )
            
            return {
                "text": hint_text,
                "hint_type": "guidance",
                "question_id": str(question_id)
            }
            
        except Exception as e:
            logger.error(f"Error generating hint: {e}")
            return {
                "text": "Take your time to think about this. Consider breaking down the question into smaller parts and addressing each one.",
                "hint_type": "general",
                "question_id": str(question_id)
            }
    
    def _build_hint_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for hint generation."""
        
        criteria_text = ""
        if context["evaluation_criteria"]:
            criteria_text = f"Key areas to consider: {', '.join(context['evaluation_criteria'])}"
        
        return f"""
Provide a helpful hint for this interview question without giving away the answer.

Question: {context['question_text']}
Category: {context['question_category']}
Interview Type: {context['interview_type']}
{criteria_text}

Requirements:
1. Guide the candidate's thinking without providing the answer
2. Suggest an approach or framework to consider
3. Be encouraging and supportive
4. Keep it brief (1-2 sentences)
5. Sound like a helpful interviewer, not an AI

Examples:
- "Think about using the STAR method - Situation, Task, Action, Result."
- "Consider breaking this down into the key components and addressing each one."
- "What specific example from your experience comes to mind?"

Generate a similar helpful hint for this question.
"""
    
    async def generate_adaptive_questions(
        self, 
        session: InterviewSession, 
        request: QuestionGenerationRequest
    ) -> List[InterviewQuestion]:
        """Generate adaptive questions based on current performance."""
        
        try:
            # Get recent responses for performance context
            recent_responses = await self.db.execute(
                select(InterviewResponse)
                .where(InterviewResponse.session_id == session.id)
                .order_by(InterviewResponse.created_at.desc())
                .limit(3)
            )
            responses = recent_responses.scalars().all()
            
            # Calculate performance metrics
            performance_context = self._analyze_current_performance(responses)
            
            # Generate questions using Groq
            questions_data = await self.groq_client.generate_interview_questions(
                interview_type=request.interview_type,
                category=request.category,
                difficulty_level=request.difficulty_level,
                company_name=request.company_name,
                position_title=request.position_title,
                topic_tags=request.topic_tags,
                count=request.count,
                previous_questions=request.previous_questions,
                user_performance=performance_context
            )
            
            # Convert to InterviewQuestion objects
            questions = []
            for i, q_data in enumerate(questions_data):
                question = InterviewQuestion(
                    question_text=q_data["question_text"],
                    category=request.category,
                    difficulty_level=request.difficulty_level,
                    expected_duration=q_data.get("expected_duration", 120),
                    question_order=len(session.questions) + i + 1,
                    generated_by_ai=True,
                    generation_prompt=q_data.get("generation_prompt", ""),
                    generation_context={"adaptive": True, "performance_context": performance_context},
                    context_information=q_data.get("context_information", ""),
                    evaluation_criteria=q_data.get("evaluation_criteria", []),
                    sample_answers=q_data.get("sample_answers", [])
                )
                questions.append(question)
            
            return questions
            
        except Exception as e:
            logger.error(f"Error generating adaptive questions: {e}")
            return []
    
    def _analyze_current_performance(self, responses: List[InterviewResponse]) -> Dict[str, float]:
        """Analyze current performance from recent responses."""
        
        if not responses:
            return {"overall": 0.5, "communication": 0.5, "content": 0.5}
        
        # Calculate averages
        overall_scores = [r.overall_score for r in responses if r.overall_score is not None]
        comm_scores = [r.communication_score for r in responses if r.communication_score is not None]
        content_scores = [r.content_score for r in responses if r.content_score is not None]
        
        return {
            "overall": (sum(overall_scores) / len(overall_scores) / 100) if overall_scores else 0.5,
            "communication": (sum(comm_scores) / len(comm_scores) / 100) if comm_scores else 0.5,
            "content": (sum(content_scores) / len(content_scores) / 100) if content_scores else 0.5
        }
    
    def _extract_response_highlights(self, response: InterviewResponse) -> List[str]:
        """Extract key highlights from response for immediate feedback."""
        
        highlights = []
        
        if response.overall_score and response.overall_score >= 80:
            highlights.append("Strong overall response")
        
        if response.communication_score and response.communication_score >= 80:
            highlights.append("Clear communication")
        
        if response.content_score and response.content_score >= 80:
            highlights.append("Good content depth")
        
        if response.structure_score and response.structure_score >= 0.8:
            highlights.append("Well-structured answer")
        
        if response.response_duration and response.response_duration >= 60:
            highlights.append("Thoughtful, detailed response")
        
        return highlights[:3]  # Limit to top 3 highlights