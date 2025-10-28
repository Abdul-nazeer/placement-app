"""Performance analyzer service for comprehensive interview analysis."""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
from datetime import datetime, timezone
import statistics

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.interview import (
    InterviewSession, InterviewQuestion, InterviewResponse,
    InterviewType, QuestionCategory, InterviewStatus
)
from app.models.user import User
from app.services.groq_client import GroqClient
from app.core.config import settings

logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """Comprehensive performance analysis for interview sessions."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.groq_client = GroqClient()
        
        # Performance benchmarks and thresholds
        self.benchmarks = {
            "excellent": {"min_score": 85, "percentile": 90},
            "good": {"min_score": 70, "percentile": 75},
            "average": {"min_score": 55, "percentile": 50},
            "needs_improvement": {"min_score": 40, "percentile": 25},
            "poor": {"min_score": 0, "percentile": 10}
        }
        
        # Category weights for different interview types
        self.category_weights = {
            InterviewType.BEHAVIORAL: {
                "communication": 0.4,
                "content": 0.4,
                "structure": 0.2
            },
            InterviewType.TECHNICAL: {
                "communication": 0.2,
                "content": 0.6,
                "structure": 0.2
            },
            InterviewType.HR: {
                "communication": 0.5,
                "content": 0.3,
                "structure": 0.2
            },
            InterviewType.MIXED: {
                "communication": 0.35,
                "content": 0.45,
                "structure": 0.2
            }
        }
    
    async def generate_comprehensive_analysis(self, session: InterviewSession) -> Dict[str, Any]:
        """Generate comprehensive performance analysis for a completed interview session."""
        
        try:
            # Basic performance metrics
            performance_metrics = await self._calculate_performance_metrics(session)
            
            # Detailed category analysis
            category_analysis = await self._analyze_by_category(session)
            
            # Time and pacing analysis
            timing_analysis = await self._analyze_timing_patterns(session)
            
            # Comparative analysis (vs other users)
            comparative_analysis = await self._generate_comparative_analysis(session)
            
            # Trend analysis (if user has previous sessions)
            trend_analysis = await self._analyze_performance_trends(session.user_id, session.interview_type)
            
            # AI-powered insights
            ai_insights = await self._generate_ai_insights(session, performance_metrics)
            
            # Strengths and weaknesses identification
            strengths_weaknesses = await self._identify_strengths_weaknesses(session, performance_metrics)
            
            # Detailed recommendations
            recommendations = await self._generate_detailed_recommendations(
                session, performance_metrics, category_analysis
            )
            
            return {
                "session_id": str(session.id),
                "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
                "overall_performance": performance_metrics,
                "category_breakdown": category_analysis,
                "timing_analysis": timing_analysis,
                "comparative_analysis": comparative_analysis,
                "trend_analysis": trend_analysis,
                "ai_insights": ai_insights,
                "strengths": strengths_weaknesses["strengths"],
                "areas_for_improvement": strengths_weaknesses["weaknesses"],
                "detailed_recommendations": recommendations,
                "performance_level": self._determine_performance_level(performance_metrics["overall_score"]),
                "next_steps": self._generate_next_steps(performance_metrics, recommendations)
            }
            
        except Exception as e:
            logger.error(f"Error generating comprehensive analysis: {e}")
            raise
    
    async def _calculate_performance_metrics(self, session: InterviewSession) -> Dict[str, Any]:
        """Calculate detailed performance metrics."""
        
        responses = session.responses
        if not responses:
            return {
                "overall_score": 0,
                "communication_score": 0,
                "content_score": 0,
                "consistency_score": 0,
                "response_count": 0,
                "completion_rate": 0
            }
        
        # Basic scores
        overall_scores = [r.overall_score for r in responses if r.overall_score is not None]
        comm_scores = [r.communication_score for r in responses if r.communication_score is not None]
        content_scores = [r.content_score for r in responses if r.content_score is not None]
        
        # Calculate averages
        avg_overall = statistics.mean(overall_scores) if overall_scores else 0
        avg_comm = statistics.mean(comm_scores) if comm_scores else 0
        avg_content = statistics.mean(content_scores) if content_scores else 0
        
        # Calculate consistency (lower standard deviation = higher consistency)
        consistency_score = 100
        if len(overall_scores) > 1:
            std_dev = statistics.stdev(overall_scores)
            consistency_score = max(0, 100 - (std_dev * 2))  # Normalize to 0-100
        
        # Completion rate
        completion_rate = (len(responses) / session.question_count) * 100 if session.question_count > 0 else 0
        
        # Response quality distribution
        quality_distribution = self._calculate_quality_distribution(overall_scores)
        
        return {
            "overall_score": round(avg_overall, 1),
            "communication_score": round(avg_comm, 1),
            "content_score": round(avg_content, 1),
            "consistency_score": round(consistency_score, 1),
            "response_count": len(responses),
            "completion_rate": round(completion_rate, 1),
            "quality_distribution": quality_distribution,
            "score_range": {
                "min": min(overall_scores) if overall_scores else 0,
                "max": max(overall_scores) if overall_scores else 0,
                "median": statistics.median(overall_scores) if overall_scores else 0
            }
        }
    
    def _calculate_quality_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Calculate distribution of response quality."""
        
        if not scores:
            return {"excellent": 0, "good": 0, "average": 0, "poor": 0}
        
        distribution = {"excellent": 0, "good": 0, "average": 0, "poor": 0}
        
        for score in scores:
            if score >= 85:
                distribution["excellent"] += 1
            elif score >= 70:
                distribution["good"] += 1
            elif score >= 55:
                distribution["average"] += 1
            else:
                distribution["poor"] += 1
        
        return distribution
    
    async def _analyze_by_category(self, session: InterviewSession) -> Dict[str, Any]:
        """Analyze performance by question category."""
        
        category_performance = {}
        
        for response in session.responses:
            if not response.question:
                continue
            
            category = response.question.category
            if category not in category_performance:
                category_performance[category] = {
                    "scores": [],
                    "response_times": [],
                    "question_count": 0
                }
            
            category_performance[category]["question_count"] += 1
            
            if response.overall_score is not None:
                category_performance[category]["scores"].append(response.overall_score)
            
            if response.response_duration:
                category_performance[category]["response_times"].append(response.response_duration)
        
        # Calculate category statistics
        category_analysis = {}
        for category, data in category_performance.items():
            scores = data["scores"]
            times = data["response_times"]
            
            category_analysis[category] = {
                "average_score": statistics.mean(scores) if scores else 0,
                "question_count": data["question_count"],
                "average_response_time": statistics.mean(times) if times else 0,
                "performance_level": self._determine_performance_level(
                    statistics.mean(scores) if scores else 0
                ),
                "consistency": self._calculate_category_consistency(scores)
            }
        
        return category_analysis
    
    def _calculate_category_consistency(self, scores: List[float]) -> float:
        """Calculate consistency within a category."""
        
        if len(scores) <= 1:
            return 100.0
        
        std_dev = statistics.stdev(scores)
        return max(0, 100 - (std_dev * 2))
    
    async def _analyze_timing_patterns(self, session: InterviewSession) -> Dict[str, Any]:
        """Analyze timing and pacing patterns."""
        
        response_times = []
        thinking_times = []
        
        for response in session.responses:
            if response.response_duration:
                response_times.append(response.response_duration)
            if response.thinking_time:
                thinking_times.append(response.thinking_time)
        
        if not response_times:
            return {"average_response_time": 0, "pacing_analysis": "insufficient_data"}
        
        avg_response_time = statistics.mean(response_times)
        avg_thinking_time = statistics.mean(thinking_times) if thinking_times else 0
        
        # Analyze pacing patterns
        pacing_analysis = self._analyze_pacing_pattern(response_times)
        
        # Time efficiency analysis
        efficiency_score = self._calculate_time_efficiency(response_times, session.total_duration)
        
        return {
            "average_response_time": round(avg_response_time, 1),
            "average_thinking_time": round(avg_thinking_time, 1),
            "total_response_time": sum(response_times),
            "pacing_analysis": pacing_analysis,
            "efficiency_score": efficiency_score,
            "time_distribution": {
                "shortest_response": min(response_times),
                "longest_response": max(response_times),
                "median_response": statistics.median(response_times)
            }
        }
    
    def _analyze_pacing_pattern(self, response_times: List[float]) -> str:
        """Analyze pacing pattern from response times."""
        
        if len(response_times) < 3:
            return "insufficient_data"
        
        # Check for trends
        first_half = response_times[:len(response_times)//2]
        second_half = response_times[len(response_times)//2:]
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        if second_avg > first_avg * 1.2:
            return "slowing_down"
        elif second_avg < first_avg * 0.8:
            return "speeding_up"
        else:
            return "consistent"
    
    def _calculate_time_efficiency(self, response_times: List[float], total_duration: int) -> float:
        """Calculate time efficiency score."""
        
        total_response_time = sum(response_times)
        total_available_time = total_duration * 60  # Convert to seconds
        
        if total_available_time == 0:
            return 0
        
        # Optimal usage is around 70-80% of available time
        usage_ratio = total_response_time / total_available_time
        
        if 0.7 <= usage_ratio <= 0.8:
            return 100
        elif usage_ratio < 0.7:
            return usage_ratio / 0.7 * 100
        else:
            return max(0, 100 - ((usage_ratio - 0.8) * 200))
    
    async def _generate_comparative_analysis(self, session: InterviewSession) -> Dict[str, Any]:
        """Generate comparative analysis against other users."""
        
        try:
            # Get similar sessions for comparison
            similar_sessions = await self.db.execute(
                select(InterviewSession)
                .where(
                    and_(
                        InterviewSession.interview_type == session.interview_type,
                        InterviewSession.difficulty_level == session.difficulty_level,
                        InterviewSession.status == InterviewStatus.COMPLETED,
                        InterviewSession.overall_score.isnot(None),
                        InterviewSession.id != session.id
                    )
                )
                .limit(100)  # Sample size for comparison
            )
            
            comparison_sessions = similar_sessions.scalars().all()
            
            if not comparison_sessions:
                return {"percentile": 50, "comparison_available": False}
            
            # Calculate percentiles
            comparison_scores = [s.overall_score for s in comparison_sessions if s.overall_score]
            user_score = session.overall_score or 0
            
            percentile = self._calculate_percentile(user_score, comparison_scores)
            
            return {
                "percentile": percentile,
                "comparison_available": True,
                "sample_size": len(comparison_sessions),
                "average_score": statistics.mean(comparison_scores),
                "performance_ranking": self._get_performance_ranking(percentile),
                "score_distribution": {
                    "25th_percentile": statistics.quantiles(comparison_scores, n=4)[0] if len(comparison_scores) >= 4 else 0,
                    "50th_percentile": statistics.median(comparison_scores),
                    "75th_percentile": statistics.quantiles(comparison_scores, n=4)[2] if len(comparison_scores) >= 4 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating comparative analysis: {e}")
            return {"percentile": 50, "comparison_available": False}
    
    def _calculate_percentile(self, score: float, comparison_scores: List[float]) -> int:
        """Calculate percentile ranking."""
        
        if not comparison_scores:
            return 50
        
        below_count = sum(1 for s in comparison_scores if s < score)
        percentile = (below_count / len(comparison_scores)) * 100
        
        return round(percentile)
    
    def _get_performance_ranking(self, percentile: int) -> str:
        """Get performance ranking based on percentile."""
        
        if percentile >= 90:
            return "top_10_percent"
        elif percentile >= 75:
            return "top_25_percent"
        elif percentile >= 50:
            return "above_average"
        elif percentile >= 25:
            return "below_average"
        else:
            return "bottom_25_percent"
    
    async def _analyze_performance_trends(self, user_id: UUID, interview_type: InterviewType) -> Dict[str, Any]:
        """Analyze performance trends over time."""
        
        try:
            # Get user's previous sessions
            previous_sessions = await self.db.execute(
                select(InterviewSession)
                .where(
                    and_(
                        InterviewSession.user_id == user_id,
                        InterviewSession.interview_type == interview_type,
                        InterviewSession.status == InterviewStatus.COMPLETED,
                        InterviewSession.overall_score.isnot(None)
                    )
                )
                .order_by(InterviewSession.created_at.asc())
                .limit(10)  # Last 10 sessions
            )
            
            sessions = previous_sessions.scalars().all()
            
            if len(sessions) < 2:
                return {"trend_available": False, "session_count": len(sessions)}
            
            # Calculate trend
            scores = [s.overall_score for s in sessions]
            trend = self._calculate_trend(scores)
            
            # Calculate improvement rate
            improvement_rate = self._calculate_improvement_rate(scores)
            
            return {
                "trend_available": True,
                "session_count": len(sessions),
                "trend_direction": trend,
                "improvement_rate": improvement_rate,
                "score_history": [
                    {
                        "session_date": s.created_at.isoformat(),
                        "score": s.overall_score,
                        "session_id": str(s.id)
                    }
                    for s in sessions
                ],
                "performance_consistency": self._calculate_trend_consistency(scores)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing performance trends: {e}")
            return {"trend_available": False, "session_count": 0}
    
    def _calculate_trend(self, scores: List[float]) -> str:
        """Calculate overall trend direction."""
        
        if len(scores) < 2:
            return "insufficient_data"
        
        # Simple linear trend calculation
        first_half_avg = statistics.mean(scores[:len(scores)//2])
        second_half_avg = statistics.mean(scores[len(scores)//2:])
        
        improvement = second_half_avg - first_half_avg
        
        if improvement > 5:
            return "improving"
        elif improvement < -5:
            return "declining"
        else:
            return "stable"
    
    def _calculate_improvement_rate(self, scores: List[float]) -> float:
        """Calculate improvement rate per session."""
        
        if len(scores) < 2:
            return 0
        
        total_improvement = scores[-1] - scores[0]
        sessions_span = len(scores) - 1
        
        return total_improvement / sessions_span if sessions_span > 0 else 0
    
    def _calculate_trend_consistency(self, scores: List[float]) -> float:
        """Calculate consistency of performance trend."""
        
        if len(scores) < 3:
            return 100
        
        # Calculate variance in score changes
        changes = [scores[i+1] - scores[i] for i in range(len(scores)-1)]
        
        if not changes:
            return 100
        
        variance = statistics.variance(changes) if len(changes) > 1 else 0
        consistency = max(0, 100 - variance)
        
        return round(consistency, 1)
    
    async def _generate_ai_insights(self, session: InterviewSession, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered insights about performance."""
        
        try:
            context = {
                "interview_type": session.interview_type,
                "overall_score": metrics["overall_score"],
                "communication_score": metrics["communication_score"],
                "content_score": metrics["content_score"],
                "consistency_score": metrics["consistency_score"],
                "completion_rate": metrics["completion_rate"],
                "response_count": metrics["response_count"]
            }
            
            prompt = self._build_insights_prompt(context)
            
            messages = [
                {
                    "role": "system",
                    "content": """You are an expert interview coach and performance analyst. 
                    Provide insightful, actionable analysis based on interview performance data.
                    Focus on patterns, strengths, and specific areas for improvement."""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            insights_response = await self.groq_client.generate_response(
                messages=messages,
                max_tokens=800,
                temperature=0.3
            )
            
            # Parse insights (expecting JSON format)
            try:
                insights_data = json.loads(insights_response)
            except json.JSONDecodeError:
                # Fallback if not JSON
                insights_data = {
                    "key_insights": [insights_response[:200] + "..."],
                    "performance_patterns": [],
                    "notable_strengths": [],
                    "improvement_opportunities": []
                }
            
            return insights_data
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            return {
                "key_insights": ["Performance analysis completed successfully."],
                "performance_patterns": [],
                "notable_strengths": [],
                "improvement_opportunities": []
            }
    
    def _build_insights_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for AI insights generation."""
        
        return f"""
Analyze this interview performance data and provide expert insights:

Interview Type: {context['interview_type']}
Overall Score: {context['overall_score']}/100
Communication Score: {context['communication_score']}/100
Content Score: {context['content_score']}/100
Consistency Score: {context['consistency_score']}/100
Completion Rate: {context['completion_rate']}%
Questions Answered: {context['response_count']}

Provide analysis in JSON format:
{{
  "key_insights": [
    "Most important insight about performance",
    "Second key insight",
    "Third key insight"
  ],
  "performance_patterns": [
    "Pattern 1 observed in responses",
    "Pattern 2 in communication style"
  ],
  "notable_strengths": [
    "Specific strength 1",
    "Specific strength 2"
  ],
  "improvement_opportunities": [
    "Specific area for improvement 1",
    "Specific area for improvement 2"
  ]
}}

Focus on actionable insights that help the candidate understand their performance and improve.
"""
    
    async def _identify_strengths_weaknesses(
        self, 
        session: InterviewSession, 
        metrics: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Identify specific strengths and weaknesses."""
        
        strengths = []
        weaknesses = []
        
        # Analyze overall performance
        overall_score = metrics["overall_score"]
        if overall_score >= 80:
            strengths.append("Strong overall interview performance")
        elif overall_score < 60:
            weaknesses.append("Overall performance needs improvement")
        
        # Analyze communication
        comm_score = metrics["communication_score"]
        if comm_score >= 80:
            strengths.append("Excellent communication skills")
        elif comm_score < 60:
            weaknesses.append("Communication clarity needs work")
        
        # Analyze content quality
        content_score = metrics["content_score"]
        if content_score >= 80:
            strengths.append("Strong content knowledge and depth")
        elif content_score < 60:
            weaknesses.append("Content depth and accuracy need improvement")
        
        # Analyze consistency
        consistency_score = metrics["consistency_score"]
        if consistency_score >= 80:
            strengths.append("Consistent performance across questions")
        elif consistency_score < 60:
            weaknesses.append("Inconsistent response quality")
        
        # Analyze completion rate
        completion_rate = metrics["completion_rate"]
        if completion_rate >= 90:
            strengths.append("Excellent completion rate and time management")
        elif completion_rate < 70:
            weaknesses.append("Time management and completion rate need attention")
        
        # Analyze response-specific patterns
        response_strengths, response_weaknesses = self._analyze_response_patterns(session.responses)
        strengths.extend(response_strengths)
        weaknesses.extend(response_weaknesses)
        
        return {
            "strengths": strengths[:5],  # Top 5 strengths
            "weaknesses": weaknesses[:5]  # Top 5 weaknesses
        }
    
    def _analyze_response_patterns(self, responses: List[InterviewResponse]) -> Tuple[List[str], List[str]]:
        """Analyze patterns in individual responses."""
        
        strengths = []
        weaknesses = []
        
        if not responses:
            return strengths, weaknesses
        
        # Analyze speech patterns
        avg_filler_count = statistics.mean([r.filler_word_count for r in responses if r.filler_word_count is not None])
        if avg_filler_count < 2:
            strengths.append("Minimal use of filler words - articulate speech")
        elif avg_filler_count > 5:
            weaknesses.append("Frequent use of filler words affects fluency")
        
        # Analyze response structure
        structure_scores = [r.structure_score for r in responses if r.structure_score is not None]
        if structure_scores:
            avg_structure = statistics.mean(structure_scores)
            if avg_structure >= 0.8:
                strengths.append("Well-structured and organized responses")
            elif avg_structure < 0.6:
                weaknesses.append("Response structure and organization need improvement")
        
        # Analyze confidence levels
        confidence_levels = [r.confidence_level for r in responses if r.confidence_level is not None]
        if confidence_levels:
            avg_confidence = statistics.mean(confidence_levels)
            if avg_confidence >= 0.8:
                strengths.append("High confidence and self-assurance")
            elif avg_confidence < 0.6:
                weaknesses.append("Confidence and self-assurance could be improved")
        
        return strengths, weaknesses
    
    async def _generate_detailed_recommendations(
        self, 
        session: InterviewSession, 
        metrics: Dict[str, Any], 
        category_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate detailed, actionable recommendations."""
        
        recommendations = []
        
        # Overall performance recommendations
        overall_score = metrics["overall_score"]
        if overall_score < 70:
            recommendations.append({
                "category": "overall_performance",
                "priority": "high",
                "title": "Focus on Core Interview Skills",
                "description": "Your overall performance indicates room for improvement in fundamental interview skills.",
                "action_items": [
                    "Practice common interview questions daily",
                    "Record yourself answering questions and review",
                    "Work with a mentor or coach for personalized feedback",
                    "Take additional mock interviews to build confidence"
                ],
                "estimated_time": "2-3 weeks of daily practice"
            })
        
        # Communication-specific recommendations
        comm_score = metrics["communication_score"]
        if comm_score < 70:
            recommendations.append({
                "category": "communication",
                "priority": "high",
                "title": "Improve Communication Clarity",
                "description": "Focus on speaking more clearly and confidently during interviews.",
                "action_items": [
                    "Practice speaking slowly and clearly",
                    "Reduce use of filler words (um, uh, like)",
                    "Work on maintaining eye contact",
                    "Practice the STAR method for behavioral questions"
                ],
                "estimated_time": "1-2 weeks of focused practice"
            })
        
        # Content-specific recommendations
        content_score = metrics["content_score"]
        if content_score < 70:
            recommendations.append({
                "category": "content_knowledge",
                "priority": "medium",
                "title": "Strengthen Technical Knowledge",
                "description": "Improve depth and accuracy of your responses.",
                "action_items": [
                    "Review fundamental concepts in your field",
                    "Prepare specific examples and case studies",
                    "Practice explaining complex topics simply",
                    "Stay updated with industry trends and best practices"
                ],
                "estimated_time": "2-4 weeks of study"
            })
        
        # Category-specific recommendations
        for category, analysis in category_analysis.items():
            if analysis["average_score"] < 70:
                recommendations.append({
                    "category": f"{category}_questions",
                    "priority": "medium",
                    "title": f"Improve {category.replace('_', ' ').title()} Responses",
                    "description": f"Your performance in {category} questions needs attention.",
                    "action_items": self._get_category_specific_actions(category),
                    "estimated_time": "1-2 weeks of targeted practice"
                })
        
        # Time management recommendations
        if metrics["completion_rate"] < 80:
            recommendations.append({
                "category": "time_management",
                "priority": "medium",
                "title": "Improve Time Management",
                "description": "Work on managing your time better during interviews.",
                "action_items": [
                    "Practice answering questions within time limits",
                    "Prepare concise examples and stories",
                    "Learn to prioritize key points in responses",
                    "Use a timer during practice sessions"
                ],
                "estimated_time": "1 week of timed practice"
            })
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _get_category_specific_actions(self, category: str) -> List[str]:
        """Get specific action items for different question categories."""
        
        category_actions = {
            "behavioral": [
                "Practice STAR method (Situation, Task, Action, Result)",
                "Prepare 5-7 detailed behavioral examples",
                "Focus on quantifiable achievements",
                "Practice storytelling techniques"
            ],
            "technical_coding": [
                "Solve coding problems daily on platforms like LeetCode",
                "Practice explaining your thought process aloud",
                "Review data structures and algorithms",
                "Work on code optimization techniques"
            ],
            "technical_system_design": [
                "Study system design fundamentals",
                "Practice designing scalable systems",
                "Learn about distributed systems concepts",
                "Review real-world system architectures"
            ],
            "hr_general": [
                "Research the company thoroughly",
                "Prepare thoughtful questions about the role",
                "Practice discussing career goals",
                "Work on presenting yourself professionally"
            ]
        }
        
        return category_actions.get(category, [
            "Practice questions in this category",
            "Seek feedback from experienced professionals",
            "Study relevant materials and examples"
        ])
    
    def _determine_performance_level(self, score: float) -> str:
        """Determine performance level based on score."""
        
        if score >= 85:
            return "excellent"
        elif score >= 70:
            return "good"
        elif score >= 55:
            return "average"
        elif score >= 40:
            return "needs_improvement"
        else:
            return "poor"
    
    def _generate_next_steps(self, metrics: Dict[str, Any], recommendations: List[Dict[str, Any]]) -> List[str]:
        """Generate immediate next steps for the user."""
        
        next_steps = []
        
        # Prioritize based on performance
        overall_score = metrics["overall_score"]
        
        if overall_score < 60:
            next_steps.extend([
                "Schedule additional mock interview sessions",
                "Focus on the high-priority recommendations",
                "Consider working with an interview coach"
            ])
        elif overall_score < 80:
            next_steps.extend([
                "Practice the specific areas identified for improvement",
                "Take 2-3 more mock interviews in the next week",
                "Review and implement the medium-priority recommendations"
            ])
        else:
            next_steps.extend([
                "Continue practicing to maintain your strong performance",
                "Focus on fine-tuning based on detailed feedback",
                "Consider helping others to reinforce your own skills"
            ])
        
        # Add recommendation-specific next steps
        high_priority_recs = [r for r in recommendations if r.get("priority") == "high"]
        if high_priority_recs:
            next_steps.append(f"Start with: {high_priority_recs[0]['title']}")
        
        return next_steps[:5]  # Return top 5 next steps
    
    async def generate_improvement_plan(self, session: InterviewSession, user: User) -> Dict[str, Any]:
        """Generate personalized improvement plan."""
        
        try:
            # Get comprehensive analysis first
            analysis = await self.generate_comprehensive_analysis(session)
            
            # Generate AI-powered improvement plan
            improvement_plan = await self._generate_ai_improvement_plan(session, analysis, user)
            
            # Create structured learning path
            learning_path = self._create_learning_path(analysis["detailed_recommendations"])
            
            # Set up progress tracking milestones
            milestones = self._create_progress_milestones(analysis["areas_for_improvement"])
            
            return {
                "user_id": str(user.id),
                "session_id": str(session.id),
                "plan_created": datetime.now(timezone.utc).isoformat(),
                "current_level": analysis["performance_level"],
                "target_level": self._determine_target_level(analysis["overall_performance"]["overall_score"]),
                "improvement_plan": improvement_plan,
                "learning_path": learning_path,
                "progress_milestones": milestones,
                "estimated_timeline": self._calculate_improvement_timeline(analysis["detailed_recommendations"]),
                "success_metrics": self._define_success_metrics(analysis["overall_performance"])
            }
            
        except Exception as e:
            logger.error(f"Error generating improvement plan: {e}")
            raise
    
    async def _generate_ai_improvement_plan(
        self, 
        session: InterviewSession, 
        analysis: Dict[str, Any], 
        user: User
    ) -> Dict[str, Any]:
        """Generate AI-powered personalized improvement plan."""
        
        try:
            context = {
                "current_performance": analysis["overall_performance"],
                "strengths": analysis["strengths"],
                "weaknesses": analysis["areas_for_improvement"],
                "interview_type": session.interview_type,
                "user_experience_level": "intermediate"  # Could be derived from user profile
            }
            
            prompt = f"""
Create a personalized interview improvement plan based on this analysis:

Current Performance: {context['current_performance']['overall_score']}/100
Interview Type: {context['interview_type']}
Strengths: {', '.join(context['strengths'][:3])}
Areas for Improvement: {', '.join(context['weaknesses'][:3])}

Generate a structured improvement plan in JSON format:
{{
  "focus_areas": [
    {{
      "area": "Communication Skills",
      "current_level": "intermediate",
      "target_level": "advanced",
      "specific_goals": ["Goal 1", "Goal 2"],
      "practice_activities": ["Activity 1", "Activity 2"],
      "resources": ["Resource 1", "Resource 2"]
    }}
  ],
  "weekly_schedule": {{
    "week_1": ["Task 1", "Task 2"],
    "week_2": ["Task 3", "Task 4"]
  }},
  "success_indicators": ["Indicator 1", "Indicator 2"]
}}
"""
            
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert interview coach creating personalized improvement plans."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            plan_response = await self.groq_client.generate_response(
                messages=messages,
                max_tokens=1000,
                temperature=0.3
            )
            
            return json.loads(plan_response)
            
        except Exception as e:
            logger.error(f"Error generating AI improvement plan: {e}")
            return {
                "focus_areas": [],
                "weekly_schedule": {},
                "success_indicators": []
            }
    
    def _create_learning_path(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create structured learning path from recommendations."""
        
        learning_path = []
        
        # Sort recommendations by priority
        high_priority = [r for r in recommendations if r.get("priority") == "high"]
        medium_priority = [r for r in recommendations if r.get("priority") == "medium"]
        
        # Create learning modules
        for i, rec in enumerate(high_priority + medium_priority):
            module = {
                "module_number": i + 1,
                "title": rec["title"],
                "description": rec["description"],
                "learning_objectives": rec["action_items"][:3],
                "estimated_duration": rec.get("estimated_time", "1 week"),
                "difficulty": "beginner" if rec.get("priority") == "medium" else "intermediate",
                "prerequisites": [] if i == 0 else [f"Module {i}"],
                "assessment_criteria": [
                    "Demonstrate improved performance in practice sessions",
                    "Show consistent application of learned techniques",
                    "Receive positive feedback from mock interviews"
                ]
            }
            learning_path.append(module)
        
        return learning_path[:4]  # Limit to 4 modules for manageability
    
    def _create_progress_milestones(self, areas_for_improvement: List[str]) -> List[Dict[str, Any]]:
        """Create progress tracking milestones."""
        
        milestones = []
        
        for i, area in enumerate(areas_for_improvement[:3]):
            milestone = {
                "milestone_id": i + 1,
                "title": f"Improve {area}",
                "description": f"Show measurable improvement in {area.lower()}",
                "target_date": f"Week {(i + 1) * 2}",
                "success_criteria": [
                    f"Score improvement of 10+ points in {area.lower()}",
                    "Consistent performance across practice sessions",
                    "Positive feedback from mock interviews"
                ],
                "measurement_method": "Mock interview assessment",
                "status": "not_started"
            }
            milestones.append(milestone)
        
        return milestones
    
    def _determine_target_level(self, current_score: float) -> str:
        """Determine realistic target performance level."""
        
        if current_score < 50:
            return "average"
        elif current_score < 70:
            return "good"
        elif current_score < 85:
            return "excellent"
        else:
            return "expert"
    
    def _calculate_improvement_timeline(self, recommendations: List[Dict[str, Any]]) -> str:
        """Calculate estimated timeline for improvement."""
        
        if not recommendations:
            return "2-4 weeks"
        
        high_priority_count = sum(1 for r in recommendations if r.get("priority") == "high")
        
        if high_priority_count >= 3:
            return "6-8 weeks"
        elif high_priority_count >= 2:
            return "4-6 weeks"
        else:
            return "2-4 weeks"
    
    def _define_success_metrics(self, performance: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Define success metrics for improvement tracking."""
        
        current_score = performance["overall_score"]
        target_improvement = min(20, 85 - current_score)  # Realistic improvement target
        
        return [
            {
                "metric": "Overall Interview Score",
                "current_value": current_score,
                "target_value": current_score + target_improvement,
                "measurement": "Mock interview assessment"
            },
            {
                "metric": "Communication Clarity",
                "current_value": performance["communication_score"],
                "target_value": min(90, performance["communication_score"] + 15),
                "measurement": "Speech analysis and feedback"
            },
            {
                "metric": "Response Consistency",
                "current_value": performance["consistency_score"],
                "target_value": min(95, performance["consistency_score"] + 10),
                "measurement": "Performance variance tracking"
            }
        ]