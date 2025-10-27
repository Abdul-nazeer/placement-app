"""Resume processing service for parsing and analyzing resumes."""

import os
import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import tempfile
import asyncio
from datetime import datetime

import PyPDF2
import docx
import spacy
from spacy.matcher import Matcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

from app.schemas.resume import (
    StructuredResumeData, ContactInfo, WorkExperience, Education, 
    Skill, ResumeSection, ATSAnalysis, ContentAnalysis, ResumeAnalysisResult
)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

logger = logging.getLogger(__name__)


class ResumeProcessor:
    """Core resume processing engine."""
    
    def __init__(self):
        """Initialize the resume processor."""
        self.nlp = None
        self.matcher = None
        self._load_nlp_model()
        self._setup_patterns()
        self.stop_words = set(stopwords.words('english'))
        
        # ATS-friendly keywords by category
        self.ats_keywords = {
            'technical': [
                'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'mongodb',
                'aws', 'docker', 'kubernetes', 'git', 'agile', 'scrum', 'ci/cd',
                'machine learning', 'data analysis', 'api', 'microservices'
            ],
            'soft_skills': [
                'leadership', 'communication', 'teamwork', 'problem-solving',
                'analytical', 'creative', 'adaptable', 'detail-oriented',
                'time management', 'project management', 'collaboration'
            ],
            'action_verbs': [
                'developed', 'implemented', 'designed', 'created', 'managed',
                'led', 'improved', 'optimized', 'achieved', 'delivered',
                'collaborated', 'analyzed', 'built', 'maintained', 'deployed'
            ]
        }
    
    def _load_nlp_model(self):
        """Load spaCy NLP model."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model 'en_core_web_sm' not found. Installing...")
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
    
    def _setup_patterns(self):
        """Setup spaCy patterns for entity extraction."""
        self.matcher = Matcher(self.nlp.vocab)
        
        # Email pattern
        email_pattern = [{"LIKE_EMAIL": True}]
        self.matcher.add("EMAIL", [email_pattern])
        
        # Phone pattern
        phone_patterns = [
            [{"TEXT": {"REGEX": r"\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}"}}],
            [{"TEXT": {"REGEX": r"\([0-9]{3}\)\s?[0-9]{3}-[0-9]{4}"}}],
            [{"TEXT": {"REGEX": r"[0-9]{3}-[0-9]{3}-[0-9]{4}"}}]
        ]
        for i, pattern in enumerate(phone_patterns):
            self.matcher.add(f"PHONE_{i}", [pattern])
        
        # LinkedIn pattern
        linkedin_pattern = [{"TEXT": {"REGEX": r"linkedin\.com/in/[\w-]+"}}]
        self.matcher.add("LINKEDIN", [linkedin_pattern])
        
        # GitHub pattern
        github_pattern = [{"TEXT": {"REGEX": r"github\.com/[\w-]+"}}]
        self.matcher.add("GITHUB", [github_pattern])
    
    async def extract_text_from_file(self, file_path: str, file_type: str) -> str:
        """Extract text from PDF or DOC/DOCX files."""
        try:
            if file_type.lower() == 'pdf':
                return await self._extract_from_pdf(file_path)
            elif file_type.lower() in ['doc', 'docx']:
                return await self._extract_from_docx(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            raise
    
    async def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {str(e)}")
            raise
        return text.strip()
    
    async def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error reading DOCX {file_path}: {str(e)}")
            raise
    
    def parse_resume_structure(self, text: str) -> StructuredResumeData:
        """Parse resume text into structured data."""
        doc = self.nlp(text)
        
        # Extract contact information
        contact_info = self._extract_contact_info(text, doc)
        
        # Identify sections
        sections = self._identify_sections(text)
        
        # Extract structured data from sections
        work_experience = self._extract_work_experience(sections)
        education = self._extract_education(sections)
        skills = self._extract_skills(sections)
        summary = self._extract_summary(sections)
        
        return StructuredResumeData(
            contact_info=contact_info,
            summary=summary,
            work_experience=work_experience,
            education=education,
            skills=skills,
            sections=[ResumeSection(type=k, title=k, content=v) for k, v in sections.items()]
        )
    
    def _extract_contact_info(self, text: str, doc) -> ContactInfo:
        """Extract contact information from resume text."""
        contact_info = ContactInfo()
        
        # Use spaCy matcher to find patterns
        matches = self.matcher(doc)
        
        for match_id, start, end in matches:
            label = self.nlp.vocab.strings[match_id]
            span = doc[start:end]
            
            if label == "EMAIL":
                contact_info.email = span.text
            elif label.startswith("PHONE"):
                contact_info.phone = span.text
            elif label == "LINKEDIN":
                contact_info.linkedin = span.text
            elif label == "GITHUB":
                contact_info.github = span.text
        
        # Extract name (usually first line or first entity)
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and not any(char in line for char in ['@', 'http', '(', ')']):
                # Simple heuristic: if it's not email/url/phone, might be name
                if len(line.split()) <= 4 and len(line) > 2:
                    contact_info.name = line
                    break
        
        return contact_info
    
    def _identify_sections(self, text: str) -> Dict[str, str]:
        """Identify and extract resume sections."""
        sections = {}
        
        # Common section headers
        section_patterns = {
            'summary': r'(summary|profile|objective|about)',
            'experience': r'(experience|work|employment|career)',
            'education': r'(education|academic|qualification)',
            'skills': r'(skills|technical|competencies|expertise)',
            'projects': r'(projects|portfolio)',
            'certifications': r'(certifications|certificates|licenses)',
            'achievements': r'(achievements|awards|honors)',
            'references': r'(references)'
        }
        
        lines = text.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a section header
            is_header = False
            for section_name, pattern in section_patterns.items():
                if re.search(pattern, line.lower()) and len(line) < 50:
                    # Save previous section
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content)
                    
                    current_section = section_name
                    current_content = []
                    is_header = True
                    break
            
            if not is_header and current_section:
                current_content.append(line)
        
        # Save last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _extract_work_experience(self, sections: Dict[str, str]) -> List[WorkExperience]:
        """Extract work experience from sections."""
        experience_text = sections.get('experience', '')
        if not experience_text:
            return []
        
        experiences = []
        
        # Split by common patterns (company names, dates, etc.)
        # This is a simplified implementation
        paragraphs = experience_text.split('\n\n')
        
        for paragraph in paragraphs:
            if len(paragraph.strip()) < 20:  # Skip short paragraphs
                continue
            
            lines = [line.strip() for line in paragraph.split('\n') if line.strip()]
            if not lines:
                continue
            
            # First line often contains company and position
            first_line = lines[0]
            
            # Extract dates (simple pattern)
            date_pattern = r'(\d{4})\s*[-–]\s*(\d{4}|present|current)'
            date_match = re.search(date_pattern, paragraph, re.IGNORECASE)
            
            start_date = date_match.group(1) if date_match else None
            end_date = date_match.group(2) if date_match else None
            
            # Simple heuristic for company and position
            company = first_line
            position = ""
            
            if ' - ' in first_line:
                parts = first_line.split(' - ')
                position = parts[0]
                company = parts[1]
            elif ' at ' in first_line:
                parts = first_line.split(' at ')
                position = parts[0]
                company = parts[1]
            
            description = lines[1:] if len(lines) > 1 else []
            
            experiences.append(WorkExperience(
                company=company,
                position=position,
                start_date=start_date,
                end_date=end_date,
                description=description
            ))
        
        return experiences
    
    def _extract_education(self, sections: Dict[str, str]) -> List[Education]:
        """Extract education from sections."""
        education_text = sections.get('education', '')
        if not education_text:
            return []
        
        education_list = []
        
        # Split by lines and look for degree patterns
        lines = [line.strip() for line in education_text.split('\n') if line.strip()]
        
        for line in lines:
            # Look for degree patterns
            degree_patterns = [
                r'(bachelor|master|phd|doctorate|b\.?s\.?|m\.?s\.?|b\.?a\.?|m\.?a\.?)',
                r'(degree|diploma|certificate)'
            ]
            
            has_degree = any(re.search(pattern, line, re.IGNORECASE) for pattern in degree_patterns)
            
            if has_degree:
                # Extract year
                year_match = re.search(r'(\d{4})', line)
                year = year_match.group(1) if year_match else None
                
                education_list.append(Education(
                    institution=line,
                    degree=line,
                    end_date=year
                ))
        
        return education_list
    
    def _extract_skills(self, sections: Dict[str, str]) -> List[Skill]:
        """Extract skills from sections."""
        skills_text = sections.get('skills', '')
        if not skills_text:
            return []
        
        skills = []
        
        # Split by common delimiters
        skill_items = re.split(r'[,;•\n]', skills_text)
        
        for item in skill_items:
            item = item.strip()
            if item and len(item) > 1:
                # Categorize skill (simple heuristic)
                category = "technical"
                if any(soft in item.lower() for soft in ['communication', 'leadership', 'teamwork']):
                    category = "soft"
                elif any(lang in item.lower() for lang in ['english', 'spanish', 'french']):
                    category = "language"
                
                skills.append(Skill(name=item, category=category))
        
        return skills
    
    def _extract_summary(self, sections: Dict[str, str]) -> Optional[str]:
        """Extract summary/objective from sections."""
        return sections.get('summary') or sections.get('objective')
    
    def analyze_ats_compatibility(self, structured_data: StructuredResumeData, 
                                 target_role: Optional[str] = None) -> ATSAnalysis:
        """Analyze ATS compatibility of the resume."""
        
        # Combine all text for analysis
        all_text = ""
        if structured_data.summary:
            all_text += structured_data.summary + " "
        
        for exp in structured_data.work_experience:
            all_text += f"{exp.position} {exp.company} " + " ".join(exp.description) + " "
        
        for skill in structured_data.skills:
            all_text += skill.name + " "
        
        all_text = all_text.lower()
        
        # Keyword analysis
        keyword_score, missing_keywords, keyword_density = self._analyze_keywords(all_text, target_role)
        
        # Format analysis
        format_score, format_issues = self._analyze_format(structured_data)
        
        # Structure analysis
        structure_score, structure_issues = self._analyze_structure(structured_data)
        
        # Overall score (weighted average)
        overall_score = (keyword_score * 0.4 + format_score * 0.3 + structure_score * 0.3)
        
        return ATSAnalysis(
            overall_score=overall_score,
            keyword_score=keyword_score,
            format_score=format_score,
            structure_score=structure_score,
            missing_keywords=missing_keywords,
            keyword_density=keyword_density,
            format_issues=format_issues,
            structure_issues=structure_issues,
            keyword_suggestions=self._generate_keyword_suggestions(missing_keywords, target_role),
            format_recommendations=self._generate_format_recommendations(format_issues),
            structure_recommendations=self._generate_structure_recommendations(structure_issues)
        )
    
    def _analyze_keywords(self, text: str, target_role: Optional[str] = None) -> Tuple[float, List[str], Dict[str, float]]:
        """Analyze keyword optimization."""
        all_keywords = []
        for category in self.ats_keywords.values():
            all_keywords.extend(category)
        
        found_keywords = []
        keyword_density = {}
        
        for keyword in all_keywords:
            count = text.count(keyword.lower())
            if count > 0:
                found_keywords.append(keyword)
                keyword_density[keyword] = count / len(text.split()) * 100
        
        missing_keywords = [kw for kw in all_keywords if kw not in found_keywords]
        
        # Score based on keyword coverage
        score = (len(found_keywords) / len(all_keywords)) * 100
        
        return score, missing_keywords[:10], keyword_density  # Return top 10 missing
    
    def _analyze_format(self, structured_data: StructuredResumeData) -> Tuple[float, List[str]]:
        """Analyze format compatibility."""
        issues = []
        score = 100.0
        
        # Check for contact information
        if not structured_data.contact_info.email:
            issues.append("Missing email address")
            score -= 20
        
        if not structured_data.contact_info.phone:
            issues.append("Missing phone number")
            score -= 10
        
        # Check for essential sections
        if not structured_data.work_experience:
            issues.append("Missing work experience section")
            score -= 30
        
        if not structured_data.education:
            issues.append("Missing education section")
            score -= 20
        
        if not structured_data.skills:
            issues.append("Missing skills section")
            score -= 20
        
        return max(score, 0), issues
    
    def _analyze_structure(self, structured_data: StructuredResumeData) -> Tuple[float, List[str]]:
        """Analyze resume structure."""
        issues = []
        score = 100.0
        
        # Check work experience details
        for exp in structured_data.work_experience:
            if not exp.start_date:
                issues.append("Missing start dates in work experience")
                score -= 10
                break
        
        # Check education details
        for edu in structured_data.education:
            if not edu.degree:
                issues.append("Missing degree information in education")
                score -= 10
                break
        
        # Check summary length
        if structured_data.summary and len(structured_data.summary.split()) > 100:
            issues.append("Summary is too long (should be under 100 words)")
            score -= 5
        
        return max(score, 0), issues
    
    def _generate_keyword_suggestions(self, missing_keywords: List[str], 
                                    target_role: Optional[str] = None) -> List[str]:
        """Generate keyword suggestions."""
        suggestions = []
        
        # Prioritize based on target role
        if target_role:
            role_lower = target_role.lower()
            if 'developer' in role_lower or 'engineer' in role_lower:
                suggestions.extend([kw for kw in missing_keywords if kw in self.ats_keywords['technical']][:5])
            elif 'manager' in role_lower:
                suggestions.extend([kw for kw in missing_keywords if kw in self.ats_keywords['soft_skills']][:5])
        
        # Add general suggestions
        suggestions.extend(missing_keywords[:3])
        
        return list(set(suggestions))[:8]  # Return unique suggestions, max 8
    
    def _generate_format_recommendations(self, format_issues: List[str]) -> List[str]:
        """Generate format recommendations."""
        recommendations = []
        
        for issue in format_issues:
            if "email" in issue.lower():
                recommendations.append("Add a professional email address in the contact section")
            elif "phone" in issue.lower():
                recommendations.append("Include a phone number for easy contact")
            elif "experience" in issue.lower():
                recommendations.append("Add work experience section with job titles, companies, and dates")
            elif "education" in issue.lower():
                recommendations.append("Include education section with degree, institution, and graduation year")
            elif "skills" in issue.lower():
                recommendations.append("Add a skills section highlighting relevant technical and soft skills")
        
        return recommendations
    
    def _generate_structure_recommendations(self, structure_issues: List[str]) -> List[str]:
        """Generate structure recommendations."""
        recommendations = []
        
        for issue in structure_issues:
            if "start dates" in issue.lower():
                recommendations.append("Include start and end dates for all work experiences")
            elif "degree" in issue.lower():
                recommendations.append("Specify degree type and field of study in education section")
            elif "summary" in issue.lower():
                recommendations.append("Keep professional summary concise (2-3 sentences, under 100 words)")
        
        return recommendations
    
    def analyze_content_quality(self, structured_data: StructuredResumeData) -> ContentAnalysis:
        """Analyze content quality and provide improvement suggestions."""
        
        # Combine all text for analysis
        all_text = ""
        if structured_data.summary:
            all_text += structured_data.summary + " "
        
        for exp in structured_data.work_experience:
            all_text += " ".join(exp.description) + " "
        
        # Readability analysis (simplified)
        readability_score = self._calculate_readability(all_text)
        
        # Grammar analysis (basic)
        grammar_score, grammar_issues = self._analyze_grammar(all_text)
        
        # Impact analysis
        impact_score, weak_phrases, missing_metrics = self._analyze_impact(all_text)
        
        # Generate suggestions
        content_suggestions = self._generate_content_suggestions(structured_data)
        rewrite_suggestions = self._generate_rewrite_suggestions(structured_data)
        
        return ContentAnalysis(
            readability_score=readability_score,
            grammar_score=grammar_score,
            impact_score=impact_score,
            grammar_issues=grammar_issues,
            weak_phrases=weak_phrases,
            missing_metrics=missing_metrics,
            content_suggestions=content_suggestions,
            rewrite_suggestions=rewrite_suggestions
        )
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate readability score (simplified)."""
        if not text:
            return 0.0
        
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        
        if not sentences or not words:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        
        # Simple readability score (inverse of average sentence length)
        # Ideal sentence length is 15-20 words
        if 15 <= avg_sentence_length <= 20:
            return 100.0
        elif avg_sentence_length < 15:
            return 80.0 + (avg_sentence_length / 15) * 20
        else:
            return max(100.0 - (avg_sentence_length - 20) * 2, 0)
    
    def _analyze_grammar(self, text: str) -> Tuple[float, List[Dict[str, str]]]:
        """Basic grammar analysis."""
        issues = []
        
        # Check for common issues
        if re.search(r'\bi\b', text):  # Lowercase 'i'
            issues.append({"type": "capitalization", "message": "Use 'I' instead of 'i'"})
        
        if re.search(r'[.!?]\s*[a-z]', text):  # Sentence not starting with capital
            issues.append({"type": "capitalization", "message": "Start sentences with capital letters"})
        
        # Score based on issues found
        score = max(100 - len(issues) * 10, 0)
        
        return score, issues
    
    def _analyze_impact(self, text: str) -> Tuple[float, List[str], List[str]]:
        """Analyze impact and quantification."""
        weak_phrases = []
        missing_metrics = []
        
        # Check for weak phrases
        weak_patterns = [
            r'\bresponsible for\b',
            r'\bhelped with\b',
            r'\bassisted in\b',
            r'\bworked on\b',
            r'\binvolved in\b'
        ]
        
        for pattern in weak_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                weak_phrases.append(pattern.replace(r'\b', '').replace('\\', ''))
        
        # Check for metrics/numbers
        has_numbers = bool(re.search(r'\d+%|\d+\+|\$\d+|\d+x', text))
        
        if not has_numbers:
            missing_metrics.append("Add quantifiable achievements (percentages, dollar amounts, etc.)")
        
        # Score based on action verbs and metrics
        action_verb_count = sum(1 for verb in self.ats_keywords['action_verbs'] 
                               if verb in text.lower())
        
        score = min((action_verb_count * 10) + (30 if has_numbers else 0), 100)
        
        return score, weak_phrases, missing_metrics
    
    def _generate_content_suggestions(self, structured_data: StructuredResumeData) -> List[Dict[str, str]]:
        """Generate content improvement suggestions."""
        suggestions = []
        
        # Check summary
        if not structured_data.summary:
            suggestions.append({
                "section": "summary",
                "suggestion": "Add a professional summary highlighting your key skills and career objectives"
            })
        
        # Check work experience descriptions
        for i, exp in enumerate(structured_data.work_experience):
            if not exp.description or len(exp.description) < 2:
                suggestions.append({
                    "section": f"experience_{i}",
                    "suggestion": f"Add more detailed bullet points for {exp.position} role describing your achievements"
                })
        
        return suggestions
    
    def _generate_rewrite_suggestions(self, structured_data: StructuredResumeData) -> List[Dict[str, str]]:
        """Generate rewrite suggestions for better impact."""
        suggestions = []
        
        # Example rewrite suggestions
        suggestions.append({
            "original": "Responsible for managing team",
            "improved": "Led cross-functional team of 8 developers, improving project delivery by 25%"
        })
        
        suggestions.append({
            "original": "Worked on software development",
            "improved": "Developed and deployed 5 web applications using React and Node.js, serving 10,000+ users"
        })
        
        return suggestions
    
    async def generate_complete_analysis(self, structured_data: StructuredResumeData,
                                       target_role: Optional[str] = None) -> ResumeAnalysisResult:
        """Generate complete resume analysis."""
        
        # Run all analyses
        ats_analysis = self.analyze_ats_compatibility(structured_data, target_role)
        content_analysis = self.analyze_content_quality(structured_data)
        
        # Calculate overall score
        overall_score = (ats_analysis.overall_score * 0.6 + 
                        (content_analysis.readability_score + content_analysis.grammar_score + 
                         content_analysis.impact_score) / 3 * 0.4)
        
        # Generate strengths and weaknesses
        strengths = []
        weaknesses = []
        priority_improvements = []
        
        if ats_analysis.keyword_score > 70:
            strengths.append("Good keyword optimization for ATS systems")
        else:
            weaknesses.append("Needs better keyword optimization")
            priority_improvements.append("Add relevant industry keywords")
        
        if ats_analysis.format_score > 80:
            strengths.append("Well-structured format")
        else:
            weaknesses.append("Format needs improvement")
            priority_improvements.append("Improve resume structure and formatting")
        
        if content_analysis.impact_score > 70:
            strengths.append("Strong impact-focused content")
        else:
            weaknesses.append("Content lacks quantifiable achievements")
            priority_improvements.append("Add metrics and quantifiable results")
        
        return ResumeAnalysisResult(
            ats_analysis=ats_analysis,
            content_analysis=content_analysis,
            overall_score=overall_score,
            strengths=strengths,
            weaknesses=weaknesses,
            priority_improvements=priority_improvements
        )