"""Speech processing service for communication assessment."""

import asyncio
import json
import logging
import os
import re
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import aiofiles
import spacy
import whisper
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.communication import CommunicationAnalysis, CommunicationRecording
from app.schemas.communication import CommunicationAnalysisCreate

logger = logging.getLogger(__name__)


class SpeechProcessor:
    """Service for processing speech recordings and generating analysis."""
    
    def __init__(self):
        """Initialize the speech processor with models."""
        self.whisper_model = None
        self.nlp_model = None
        self.filler_words = {
            'um', 'uh', 'er', 'ah', 'like', 'you know', 'so', 'well', 
            'actually', 'basically', 'literally', 'right', 'okay', 'yeah'
        }
        self.load_models()
    
    def load_models(self):
        """Load Whisper and spaCy models."""
        try:
            # Load Whisper model (using base model for balance of speed and accuracy)
            logger.info("Loading Whisper model...")
            self.whisper_model = whisper.load_model("base")
            
            # Load spaCy model for English
            logger.info("Loading spaCy model...")
            try:
                self.nlp_model = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model 'en_core_web_sm' not found. Downloading...")
                os.system("python -m spacy download en_core_web_sm")
                self.nlp_model = spacy.load("en_core_web_sm")
            
            logger.info("Speech processing models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading speech processing models: {e}")
            raise
    
    async def transcribe_audio(self, audio_file_path: str) -> Tuple[str, float, Dict]:
        """
        Transcribe audio file using Whisper.
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            Tuple of (transcript, confidence_score, detailed_results)
        """
        try:
            logger.info(f"Starting transcription for: {audio_file_path}")
            
            # Run Whisper transcription in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self.whisper_model.transcribe, 
                audio_file_path,
                {"word_timestamps": True, "language": "en"}
            )
            
            transcript = result["text"].strip()
            
            # Calculate average confidence from segments
            confidence_scores = []
            if "segments" in result:
                for segment in result["segments"]:
                    if "avg_logprob" in segment:
                        # Convert log probability to confidence (0-1)
                        confidence = min(1.0, max(0.0, (segment["avg_logprob"] + 1.0)))
                        confidence_scores.append(confidence)
            
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.8
            
            # Extract word-level timestamps for detailed analysis
            word_timestamps = []
            if "segments" in result:
                for segment in result["segments"]:
                    if "words" in segment:
                        for word_info in segment["words"]:
                            word_timestamps.append({
                                "word": word_info.get("word", "").strip(),
                                "start": word_info.get("start", 0),
                                "end": word_info.get("end", 0),
                                "probability": word_info.get("probability", 0.8)
                            })
            
            detailed_results = {
                "segments": result.get("segments", []),
                "word_timestamps": word_timestamps,
                "language": result.get("language", "en"),
                "duration": result.get("duration", 0)
            }
            
            logger.info(f"Transcription completed. Length: {len(transcript)} chars, Confidence: {avg_confidence:.3f}")
            
            return transcript, avg_confidence, detailed_results
            
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            raise
    
    async def analyze_speech_patterns(self, transcript: str, word_timestamps: List[Dict]) -> Dict:
        """
        Analyze speech patterns including pace, pauses, and filler words.
        
        Args:
            transcript: The transcribed text
            word_timestamps: List of word-level timestamps
            
        Returns:
            Dictionary containing speech pattern analysis
        """
        try:
            if not word_timestamps:
                return self._basic_speech_analysis(transcript)
            
            # Calculate speaking rate (words per minute)
            total_duration = word_timestamps[-1]["end"] - word_timestamps[0]["start"] if word_timestamps else 0
            word_count = len([w for w in word_timestamps if w["word"].strip()])
            wpm = (word_count / total_duration * 60) if total_duration > 0 else 0
            
            # Analyze pauses
            pauses = []
            for i in range(1, len(word_timestamps)):
                gap = word_timestamps[i]["start"] - word_timestamps[i-1]["end"]
                if gap > 0.5:  # Consider gaps > 0.5 seconds as pauses
                    pauses.append(gap)
            
            pause_frequency = len(pauses) / (total_duration / 60) if total_duration > 0 else 0
            avg_pause_duration = sum(pauses) / len(pauses) if pauses else 0
            
            # Detect filler words
            filler_words_detected = []
            filler_count = 0
            
            for word_info in word_timestamps:
                word = word_info["word"].lower().strip()
                if word in self.filler_words:
                    filler_count += 1
                    filler_words_detected.append({
                        "word": word,
                        "timestamp": word_info["start"],
                        "duration": word_info["end"] - word_info["start"]
                    })
            
            filler_percentage = (filler_count / word_count * 100) if word_count > 0 else 0
            
            return {
                "words_per_minute": round(wpm, 2),
                "pause_frequency": round(pause_frequency, 2),
                "average_pause_duration": round(avg_pause_duration, 2),
                "filler_word_count": filler_count,
                "filler_word_percentage": round(filler_percentage, 2),
                "filler_words_detected": filler_words_detected,
                "total_duration": total_duration,
                "word_count": word_count
            }
            
        except Exception as e:
            logger.error(f"Error analyzing speech patterns: {e}")
            return self._basic_speech_analysis(transcript)
    
    def _basic_speech_analysis(self, transcript: str) -> Dict:
        """Basic speech analysis when timestamps are not available."""
        words = transcript.split()
        word_count = len(words)
        
        # Count filler words
        filler_count = sum(1 for word in words if word.lower().strip('.,!?') in self.filler_words)
        filler_percentage = (filler_count / word_count * 100) if word_count > 0 else 0
        
        return {
            "words_per_minute": 0,  # Cannot calculate without timing
            "pause_frequency": 0,
            "average_pause_duration": 0,
            "filler_word_count": filler_count,
            "filler_word_percentage": round(filler_percentage, 2),
            "filler_words_detected": [],
            "total_duration": 0,
            "word_count": word_count
        }
    
    async def analyze_language_quality(self, transcript: str) -> Dict:
        """
        Analyze language quality using spaCy NLP.
        
        Args:
            transcript: The transcribed text
            
        Returns:
            Dictionary containing language quality metrics
        """
        try:
            if not transcript.strip():
                return {
                    "grammar_score": 0.0,
                    "vocabulary_complexity": 0.0,
                    "sentence_structure_score": 0.0,
                    "clarity_score": 0.0
                }
            
            # Process text with spaCy
            doc = self.nlp_model(transcript)
            
            # Grammar analysis (simplified)
            grammar_score = self._analyze_grammar(doc)
            
            # Vocabulary complexity
            vocabulary_complexity = self._analyze_vocabulary_complexity(doc)
            
            # Sentence structure analysis
            sentence_structure_score = self._analyze_sentence_structure(doc)
            
            # Clarity score (combination of factors)
            clarity_score = (grammar_score + vocabulary_complexity + sentence_structure_score) / 3
            
            return {
                "grammar_score": round(grammar_score, 3),
                "vocabulary_complexity": round(vocabulary_complexity, 3),
                "sentence_structure_score": round(sentence_structure_score, 3),
                "clarity_score": round(clarity_score, 3)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing language quality: {e}")
            return {
                "grammar_score": 0.5,
                "vocabulary_complexity": 0.5,
                "sentence_structure_score": 0.5,
                "clarity_score": 0.5
            }
    
    def _analyze_grammar(self, doc) -> float:
        """Analyze grammar quality based on POS tags and dependencies."""
        if len(doc) == 0:
            return 0.0
        
        # Count grammatical elements
        verbs = sum(1 for token in doc if token.pos_ in ["VERB", "AUX"])
        nouns = sum(1 for token in doc if token.pos_ in ["NOUN", "PROPN"])
        complete_sentences = len(list(doc.sents))
        
        # Basic grammar score based on sentence completeness and structure
        if complete_sentences == 0:
            return 0.3
        
        avg_sentence_length = len(doc) / complete_sentences
        verb_noun_ratio = verbs / (nouns + 1)  # Avoid division by zero
        
        # Score based on balanced structure
        grammar_score = min(1.0, (avg_sentence_length / 15) * 0.4 + 
                           min(verb_noun_ratio, 1.0) * 0.6)
        
        return max(0.1, grammar_score)
    
    def _analyze_vocabulary_complexity(self, doc) -> float:
        """Analyze vocabulary complexity and diversity."""
        if len(doc) == 0:
            return 0.0
        
        # Get unique lemmas (base forms of words)
        lemmas = [token.lemma_.lower() for token in doc 
                 if token.is_alpha and not token.is_stop]
        
        if not lemmas:
            return 0.0
        
        # Calculate type-token ratio (vocabulary diversity)
        unique_lemmas = set(lemmas)
        ttr = len(unique_lemmas) / len(lemmas)
        
        # Analyze word complexity (average word length)
        avg_word_length = sum(len(lemma) for lemma in lemmas) / len(lemmas)
        
        # Combine metrics
        complexity_score = min(1.0, ttr * 0.6 + (avg_word_length / 10) * 0.4)
        
        return max(0.1, complexity_score)
    
    def _analyze_sentence_structure(self, doc) -> float:
        """Analyze sentence structure complexity and variety."""
        sentences = list(doc.sents)
        
        if not sentences:
            return 0.0
        
        # Analyze sentence length variety
        sentence_lengths = [len(sent) for sent in sentences]
        avg_length = sum(sentence_lengths) / len(sentence_lengths)
        
        # Check for variety in sentence structures
        dependency_patterns = set()
        for sent in sentences:
            pattern = tuple(token.dep_ for token in sent[:5])  # First 5 dependencies
            dependency_patterns.add(pattern)
        
        structure_variety = len(dependency_patterns) / len(sentences)
        
        # Score based on appropriate length and variety
        length_score = min(1.0, avg_length / 12)  # Optimal around 12 words
        variety_score = min(1.0, structure_variety * 2)
        
        structure_score = (length_score + variety_score) / 2
        
        return max(0.1, structure_score)
    
    async def analyze_content_relevance(self, transcript: str, prompt_text: str) -> Dict:
        """
        Analyze content relevance to the given prompt.
        
        Args:
            transcript: The transcribed speech
            prompt_text: The original prompt/question
            
        Returns:
            Dictionary containing content analysis metrics
        """
        try:
            if not transcript.strip() or not prompt_text.strip():
                return {
                    "relevance_score": 0.0,
                    "completeness_score": 0.0,
                    "coherence_score": 0.0
                }
            
            # Process both texts
            transcript_doc = self.nlp_model(transcript)
            prompt_doc = self.nlp_model(prompt_text)
            
            # Calculate relevance based on semantic similarity
            relevance_score = self._calculate_semantic_similarity(transcript_doc, prompt_doc)
            
            # Analyze completeness (response length and structure)
            completeness_score = self._analyze_completeness(transcript_doc)
            
            # Analyze coherence (logical flow)
            coherence_score = self._analyze_coherence(transcript_doc)
            
            return {
                "relevance_score": round(relevance_score, 3),
                "completeness_score": round(completeness_score, 3),
                "coherence_score": round(coherence_score, 3)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing content relevance: {e}")
            return {
                "relevance_score": 0.5,
                "completeness_score": 0.5,
                "coherence_score": 0.5
            }
    
    def _calculate_semantic_similarity(self, doc1, doc2) -> float:
        """Calculate semantic similarity between two documents."""
        try:
            # Use spaCy's built-in similarity if available
            if doc1.vector.any() and doc2.vector.any():
                similarity = doc1.similarity(doc2)
                return max(0.0, min(1.0, similarity))
            
            # Fallback: keyword overlap
            words1 = set(token.lemma_.lower() for token in doc1 
                        if token.is_alpha and not token.is_stop)
            words2 = set(token.lemma_.lower() for token in doc2 
                        if token.is_alpha and not token.is_stop)
            
            if not words1 or not words2:
                return 0.0
            
            overlap = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            return overlap / union if union > 0 else 0.0
            
        except Exception:
            return 0.5
    
    def _analyze_completeness(self, doc) -> float:
        """Analyze response completeness."""
        sentences = list(doc.sents)
        
        if not sentences:
            return 0.0
        
        # Score based on response length and structure
        word_count = len([token for token in doc if token.is_alpha])
        sentence_count = len(sentences)
        
        # Optimal response: 50-200 words, 3-8 sentences
        word_score = min(1.0, word_count / 100) if word_count <= 200 else max(0.5, 200 / word_count)
        sentence_score = min(1.0, sentence_count / 5) if sentence_count <= 8 else max(0.5, 8 / sentence_count)
        
        return (word_score + sentence_score) / 2
    
    def _analyze_coherence(self, doc) -> float:
        """Analyze logical coherence and flow."""
        sentences = list(doc.sents)
        
        if len(sentences) < 2:
            return 0.8 if sentences else 0.0
        
        # Check for discourse markers and connectives
        connectives = {"however", "therefore", "moreover", "furthermore", "additionally", 
                      "consequently", "meanwhile", "similarly", "in contrast", "for example"}
        
        connective_count = sum(1 for token in doc 
                              if token.lemma_.lower() in connectives)
        
        # Score based on appropriate use of connectives
        coherence_score = min(1.0, connective_count / len(sentences) * 3)
        
        # Boost score for longer responses (they tend to be more coherent if structured)
        if len(sentences) >= 3:
            coherence_score = min(1.0, coherence_score + 0.2)
        
        return max(0.3, coherence_score)
    
    async def generate_comprehensive_analysis(
        self, 
        transcript: str, 
        word_timestamps: List[Dict],
        prompt_text: str = ""
    ) -> Dict:
        """
        Generate comprehensive communication analysis.
        
        Args:
            transcript: The transcribed speech
            word_timestamps: Word-level timing information
            prompt_text: Original prompt for relevance analysis
            
        Returns:
            Complete analysis dictionary
        """
        try:
            # Perform all analyses
            speech_analysis = await self.analyze_speech_patterns(transcript, word_timestamps)
            language_analysis = await self.analyze_language_quality(transcript)
            content_analysis = await self.analyze_content_relevance(transcript, prompt_text)
            
            # Calculate overall scores
            fluency_score = self._calculate_fluency_score(speech_analysis, language_analysis)
            confidence_score = self._calculate_confidence_score(speech_analysis, language_analysis)
            overall_score = self._calculate_overall_score(
                fluency_score, confidence_score, content_analysis
            )
            
            # Generate feedback
            strengths, weaknesses, suggestions = self._generate_feedback(
                speech_analysis, language_analysis, content_analysis
            )
            
            return {
                **speech_analysis,
                **language_analysis,
                **content_analysis,
                "fluency_score": round(fluency_score, 3),
                "confidence_score": round(confidence_score, 3),
                "overall_score": round(overall_score, 3),
                "strengths": strengths,
                "weaknesses": weaknesses,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Error generating comprehensive analysis: {e}")
            raise
    
    def _calculate_fluency_score(self, speech_analysis: Dict, language_analysis: Dict) -> float:
        """Calculate fluency score from speech and language metrics."""
        wpm = speech_analysis.get("words_per_minute", 0)
        filler_percentage = speech_analysis.get("filler_word_percentage", 0)
        grammar_score = language_analysis.get("grammar_score", 0)
        
        # Optimal WPM is around 150-180
        wpm_score = 1.0 if 120 <= wpm <= 200 else max(0.3, min(wpm / 150, 200 / wpm))
        
        # Lower filler percentage is better
        filler_score = max(0.0, 1.0 - (filler_percentage / 20))  # 20% filler = 0 score
        
        fluency = (wpm_score * 0.4 + filler_score * 0.3 + grammar_score * 0.3)
        return min(1.0, max(0.0, fluency))
    
    def _calculate_confidence_score(self, speech_analysis: Dict, language_analysis: Dict) -> float:
        """Calculate confidence score from speech patterns."""
        pause_frequency = speech_analysis.get("pause_frequency", 0)
        filler_percentage = speech_analysis.get("filler_word_percentage", 0)
        clarity_score = language_analysis.get("clarity_score", 0)
        
        # Fewer pauses and fillers indicate more confidence
        pause_score = max(0.0, 1.0 - (pause_frequency / 10))  # 10 pauses/min = 0 score
        filler_score = max(0.0, 1.0 - (filler_percentage / 15))  # 15% filler = 0 score
        
        confidence = (pause_score * 0.3 + filler_score * 0.3 + clarity_score * 0.4)
        return min(1.0, max(0.0, confidence))
    
    def _calculate_overall_score(self, fluency: float, confidence: float, content: Dict) -> float:
        """Calculate overall communication score."""
        relevance = content.get("relevance_score", 0)
        completeness = content.get("completeness_score", 0)
        coherence = content.get("coherence_score", 0)
        
        content_score = (relevance + completeness + coherence) / 3
        
        overall = (fluency * 0.3 + confidence * 0.3 + content_score * 0.4)
        return min(1.0, max(0.0, overall))
    
    def _generate_feedback(
        self, 
        speech_analysis: Dict, 
        language_analysis: Dict, 
        content_analysis: Dict
    ) -> Tuple[List[str], List[str], List[str]]:
        """Generate personalized feedback based on analysis."""
        strengths = []
        weaknesses = []
        suggestions = []
        
        # Analyze speech patterns
        wpm = speech_analysis.get("words_per_minute", 0)
        filler_percentage = speech_analysis.get("filler_word_percentage", 0)
        
        if wpm >= 120 and wpm <= 200:
            strengths.append("Good speaking pace - clear and easy to follow")
        elif wpm < 120:
            weaknesses.append("Speaking pace is quite slow")
            suggestions.append("Try to speak a bit faster to maintain engagement")
        else:
            weaknesses.append("Speaking pace is very fast")
            suggestions.append("Slow down your speech for better clarity")
        
        if filler_percentage < 5:
            strengths.append("Minimal use of filler words - very articulate")
        elif filler_percentage > 15:
            weaknesses.append("Frequent use of filler words")
            suggestions.append("Practice pausing instead of using filler words like 'um' and 'uh'")
        
        # Analyze language quality
        grammar_score = language_analysis.get("grammar_score", 0)
        vocabulary_complexity = language_analysis.get("vocabulary_complexity", 0)
        
        if grammar_score >= 0.7:
            strengths.append("Strong grammar and sentence structure")
        elif grammar_score < 0.5:
            weaknesses.append("Grammar and sentence structure need improvement")
            suggestions.append("Focus on complete sentences and proper grammar")
        
        if vocabulary_complexity >= 0.6:
            strengths.append("Good vocabulary variety and complexity")
        elif vocabulary_complexity < 0.4:
            weaknesses.append("Limited vocabulary variety")
            suggestions.append("Try to use more varied and descriptive words")
        
        # Analyze content
        relevance_score = content_analysis.get("relevance_score", 0)
        completeness_score = content_analysis.get("completeness_score", 0)
        
        if relevance_score >= 0.7:
            strengths.append("Response is highly relevant to the question")
        elif relevance_score < 0.5:
            weaknesses.append("Response doesn't fully address the question")
            suggestions.append("Make sure to directly answer what's being asked")
        
        if completeness_score >= 0.7:
            strengths.append("Comprehensive and well-developed response")
        elif completeness_score < 0.5:
            weaknesses.append("Response lacks detail and development")
            suggestions.append("Provide more specific examples and elaborate on your points")
        
        return strengths, weaknesses, suggestions


# Global instance
speech_processor = SpeechProcessor()