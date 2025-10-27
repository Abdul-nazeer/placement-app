"""ATS (Applicant Tracking System) compatibility analyzer."""

import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import logging

from app.schemas.resume import StructuredResumeData, ATSAnalysis

logger = logging.getLogger(__name__)


@dataclass
class ATSRule:
    """Represents an ATS compatibility rule."""
    name: str
    description: str
    weight: float
    check_function: str
    penalty: float = 0.0
    bonus: float = 0.0


class ATSCompatibilityAnalyzer:
    """Analyzer for ATS compatibility scoring and optimization."""
    
    def __init__(self):
        """Initialize ATS analyzer with rules and patterns."""
        self.ats_rules = self._load_ats_rules()
        self.problematic_formats = self._load_problematic_formats()
        self.ats_friendly_sections = self._load_ats_sections()
        self.keyword_categories = self._load_keyword_categories()
    
    def _load_ats_rules(self) -> List[ATSRule]:
        """Load ATS compatibility rules."""
        return [
            ATSRule(
                name="contact_information",
                description="Resume must have complete contact information",
                weight=0.15,
                check_function="check_contact_info",
                penalty=20.0
            ),
            ATSRule(
                name="standard_sections",
                description="Resume must have standard sections (Experience, Education, Skills)",
                weight=0.20,
                check_function="check_standard_sections",
                penalty=25.0
            ),
            ATSRule(
                name="keyword_optimization",
                description="Resume should contain relevant industry keywords",
                weight=0.25,
                check_function="check_keyword_optimization",
                penalty=30.0
            ),
            ATSRule(
                name="format_compatibility",
                description="Resume format should be ATS-readable",
                weight=0.15,
                check_function="check_format_compatibility",
                penalty=20.0
            ),
            ATSRule(
                name="section_headers",
                description="Section headers should be clear and standard",
                weight=0.10,
                check_function="check_section_headers",
                penalty=10.0
            ),
            ATSRule(
                name="date_formatting",
                description="Dates should be consistently formatted",
                weight=0.08,
                check_function="check_date_formatting",
                penalty=8.0
            ),
            ATSRule(
                name="bullet_points",
                description="Experience should use bullet points effectively",
                weight=0.07,
                check_function="check_bullet_points",
                penalty=7.0
            )
        ]
    
    def _load_problematic_formats(self) -> Dict[str, List[str]]:
        """Load formats that cause ATS parsing issues."""
        return {
            "headers_footers": [
                "Text in headers or footers may not be parsed",
                "Contact info in headers might be missed"
            ],
            "tables": [
                "Complex tables can confuse ATS parsers",
                "Information in table cells may be misaligned"
            ],
            "graphics": [
                "Images and graphics are not readable by ATS",
                "Text within images will be ignored"
            ],
            "columns": [
                "Multi-column layouts can scramble text order",
                "ATS may read across columns incorrectly"
            ],
            "special_characters": [
                "Unusual fonts or characters may not display correctly",
                "Special symbols might be converted to question marks"
            ],
            "text_boxes": [
                "Text boxes may not be parsed in correct order",
                "Content in text boxes might be skipped"
            ]
        }
    
    def _load_ats_sections(self) -> List[str]:
        """Load standard ATS-friendly section names."""
        return [
            "contact information", "professional summary", "summary", "objective",
            "work experience", "experience", "employment history", "professional experience",
            "education", "academic background", "qualifications",
            "skills", "technical skills", "core competencies", "areas of expertise",
            "certifications", "licenses", "professional certifications",
            "projects", "key projects", "notable projects",
            "achievements", "accomplishments", "awards",
            "publications", "research", "patents"
        ]
    
    def _load_keyword_categories(self) -> Dict[str, Dict[str, List[str]]]:
        """Load keyword categories for different industries and roles."""
        return {
            "technology": {
                "programming": [
                    "python", "java", "javascript", "c++", "c#", "go", "rust", "php", "ruby"
                ],
                "frameworks": [
                    "react", "angular", "vue", "django", "flask", "spring", "express", "laravel"
                ],
                "databases": [
                    "mysql", "postgresql", "mongodb", "redis", "oracle", "sql server"
                ],
                "cloud": [
                    "aws", "azure", "google cloud", "docker", "kubernetes", "terraform"
                ],
                "methodologies": [
                    "agile", "scrum", "devops", "ci/cd", "tdd", "microservices"
                ]
            },
            "business": {
                "analysis": [
                    "business analysis", "data analysis", "market research", "competitive analysis"
                ],
                "management": [
                    "project management", "team leadership", "strategic planning", "process improvement"
                ],
                "finance": [
                    "financial modeling", "budgeting", "forecasting", "risk management"
                ]
            },
            "marketing": {
                "digital": [
                    "seo", "sem", "social media marketing", "content marketing", "email marketing"
                ],
                "analytics": [
                    "google analytics", "conversion optimization", "a/b testing", "roi analysis"
                ],
                "tools": [
                    "hubspot", "salesforce", "mailchimp", "hootsuite", "buffer"
                ]
            }
        }
    
    def analyze_ats_compatibility(self, structured_data: StructuredResumeData, 
                                 raw_text: str, target_industry: Optional[str] = None,
                                 target_role: Optional[str] = None) -> ATSAnalysis:
        """Perform comprehensive ATS compatibility analysis."""
        
        analysis_results = {}
        total_score = 100.0
        
        # Run all ATS rule checks
        for rule in self.ats_rules:
            try:
                check_method = getattr(self, rule.check_function)
                rule_result = check_method(structured_data, raw_text, target_industry, target_role)
                analysis_results[rule.name] = rule_result
                
                if not rule_result.get("passed", True):
                    total_score -= rule.penalty * rule.weight
                elif rule_result.get("bonus", False):
                    total_score += rule.bonus * rule.weight
                    
            except AttributeError:
                logger.warning(f"ATS rule check method {rule.check_function} not found")
                continue
        
        # Calculate component scores
        keyword_score = analysis_results.get("keyword_optimization", {}).get("score", 0)
        format_score = analysis_results.get("format_compatibility", {}).get("score", 0)
        structure_score = analysis_results.get("standard_sections", {}).get("score", 0)
        
        # Compile issues and recommendations
        format_issues = self._compile_format_issues(analysis_results)
        structure_issues = self._compile_structure_issues(analysis_results)
        missing_keywords = analysis_results.get("keyword_optimization", {}).get("missing_keywords", [])
        keyword_density = analysis_results.get("keyword_optimization", {}).get("keyword_density", {})
        
        # Generate recommendations
        keyword_suggestions = self._generate_keyword_suggestions(missing_keywords, target_industry, target_role)
        format_recommendations = self._generate_format_recommendations(format_issues)
        structure_recommendations = self._generate_structure_recommendations(structure_issues)
        
        return ATSAnalysis(
            overall_score=max(total_score, 0),
            keyword_score=keyword_score,
            format_score=format_score,
            structure_score=structure_score,
            missing_keywords=missing_keywords,
            keyword_density=keyword_density,
            format_issues=format_issues,
            structure_issues=structure_issues,
            keyword_suggestions=keyword_suggestions,
            format_recommendations=format_recommendations,
            structure_recommendations=structure_recommendations
        )
    
    def check_contact_info(self, structured_data: StructuredResumeData, raw_text: str, 
                          target_industry: Optional[str] = None, target_role: Optional[str] = None) -> Dict[str, Any]:
        """Check completeness of contact information."""
        contact = structured_data.contact_info
        issues = []
        score = 100.0
        
        if not contact.email:
            issues.append("Missing email address")
            score -= 30
        elif not self._is_valid_email(contact.email):
            issues.append("Email format appears invalid")
            score -= 15
        
        if not contact.phone:
            issues.append("Missing phone number")
            score -= 25
        elif not self._is_valid_phone(contact.phone):
            issues.append("Phone number format may not be ATS-friendly")
            score -= 10
        
        if not contact.name:
            issues.append("Name not clearly identified")
            score -= 20
        
        # Professional links are bonus points
        bonus = False
        if contact.linkedin:
            bonus = True
            score += 5
        if contact.github and target_industry == "technology":
            bonus = True
            score += 5
        
        return {
            "passed": len(issues) == 0,
            "score": max(score, 0),
            "issues": issues,
            "bonus": bonus,
            "details": {
                "has_email": bool(contact.email),
                "has_phone": bool(contact.phone),
                "has_name": bool(contact.name),
                "has_linkedin": bool(contact.linkedin),
                "has_github": bool(contact.github)
            }
        }
    
    def check_standard_sections(self, structured_data: StructuredResumeData, raw_text: str,
                               target_industry: Optional[str] = None, target_role: Optional[str] = None) -> Dict[str, Any]:
        """Check for presence of standard resume sections."""
        issues = []
        score = 100.0
        
        # Essential sections
        if not structured_data.work_experience:
            issues.append("Missing work experience section")
            score -= 40
        
        if not structured_data.education:
            issues.append("Missing education section")
            score -= 30
        
        if not structured_data.skills:
            issues.append("Missing skills section")
            score -= 20
        
        # Recommended sections
        if not structured_data.summary:
            issues.append("Missing professional summary")
            score -= 10
        
        return {
            "passed": len(issues) == 0,
            "score": max(score, 0),
            "issues": issues,
            "details": {
                "has_experience": bool(structured_data.work_experience),
                "has_education": bool(structured_data.education),
                "has_skills": bool(structured_data.skills),
                "has_summary": bool(structured_data.summary)
            }
        }
    
    def check_keyword_optimization(self, structured_data: StructuredResumeData, raw_text: str,
                                  target_industry: Optional[str] = None, target_role: Optional[str] = None) -> Dict[str, Any]:
        """Check keyword optimization for ATS."""
        text_lower = raw_text.lower()
        
        # Get relevant keywords based on industry and role
        relevant_keywords = self._get_relevant_keywords(target_industry, target_role)
        
        # Analyze keyword presence and density
        keyword_analysis = {}
        found_keywords = []
        missing_keywords = []
        
        for keyword in relevant_keywords:
            count = text_lower.count(keyword.lower())
            density = (count / len(raw_text.split())) * 100 if raw_text else 0
            
            keyword_analysis[keyword] = {
                "count": count,
                "density": round(density, 2)
            }
            
            if count > 0:
                found_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        # Calculate keyword score
        keyword_coverage = len(found_keywords) / len(relevant_keywords) if relevant_keywords else 1.0
        keyword_score = keyword_coverage * 100
        
        # Check for keyword stuffing
        stuffing_penalty = 0
        for keyword, analysis in keyword_analysis.items():
            if analysis["density"] > 5.0:  # More than 5% density is likely stuffing
                stuffing_penalty += 10
        
        final_score = max(keyword_score - stuffing_penalty, 0)
        
        return {
            "passed": keyword_score >= 60,
            "score": final_score,
            "keyword_density": {k: v["density"] for k, v in keyword_analysis.items()},
            "missing_keywords": missing_keywords[:10],  # Top 10 missing
            "found_keywords": found_keywords,
            "keyword_coverage": round(keyword_coverage * 100, 2),
            "stuffing_detected": stuffing_penalty > 0
        }
    
    def check_format_compatibility(self, structured_data: StructuredResumeData, raw_text: str,
                                  target_industry: Optional[str] = None, target_role: Optional[str] = None) -> Dict[str, Any]:
        """Check format compatibility with ATS systems."""
        issues = []
        score = 100.0
        
        # Check for problematic formatting patterns in text
        if re.search(r'[^\x00-\x7F]', raw_text):  # Non-ASCII characters
            issues.append("Contains non-standard characters that may not parse correctly")
            score -= 15
        
        # Check for excessive special formatting
        if len(re.findall(r'[•◦▪▫‣⁃]', raw_text)) > 50:  # Too many special bullets
            issues.append("Excessive use of special bullet characters")
            score -= 10
        
        # Check for proper line breaks and structure
        lines = raw_text.split('\n')
        empty_lines = sum(1 for line in lines if not line.strip())
        if empty_lines / len(lines) > 0.5:  # More than 50% empty lines
            issues.append("Excessive white space may affect parsing")
            score -= 10
        
        # Check for consistent formatting
        if not self._has_consistent_date_format(raw_text):
            issues.append("Inconsistent date formatting")
            score -= 10
        
        return {
            "passed": len(issues) == 0,
            "score": max(score, 0),
            "issues": issues,
            "details": {
                "has_special_chars": bool(re.search(r'[^\x00-\x7F]', raw_text)),
                "excessive_bullets": len(re.findall(r'[•◦▪▫‣⁃]', raw_text)) > 50,
                "consistent_dates": self._has_consistent_date_format(raw_text)
            }
        }
    
    def check_section_headers(self, structured_data: StructuredResumeData, raw_text: str,
                             target_industry: Optional[str] = None, target_role: Optional[str] = None) -> Dict[str, Any]:
        """Check if section headers are ATS-friendly."""
        issues = []
        score = 100.0
        
        # Extract potential section headers from text
        lines = raw_text.split('\n')
        potential_headers = []
        
        for line in lines:
            line = line.strip()
            if line and len(line) < 50 and not any(char in line for char in ['@', '(', ')', '.']):
                # Might be a header if it's short and doesn't contain contact info patterns
                potential_headers.append(line.lower())
        
        # Check if headers match standard ATS-friendly names
        standard_headers_found = 0
        for header in potential_headers:
            if any(std_header in header for std_header in self.ats_friendly_sections):
                standard_headers_found += 1
        
        if standard_headers_found < 3:  # Should have at least 3 standard sections
            issues.append("Section headers may not be ATS-friendly")
            score -= 20
        
        return {
            "passed": len(issues) == 0,
            "score": max(score, 0),
            "issues": issues,
            "standard_headers_found": standard_headers_found
        }
    
    def check_date_formatting(self, structured_data: StructuredResumeData, raw_text: str,
                             target_industry: Optional[str] = None, target_role: Optional[str] = None) -> Dict[str, Any]:
        """Check consistency of date formatting."""
        issues = []
        score = 100.0
        
        # Find all date patterns in text
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY
            r'\b\d{4}-\d{1,2}-\d{1,2}\b',  # YYYY-MM-DD
            r'\b\w+ \d{4}\b',              # Month YYYY
            r'\b\d{4}\b'                   # Just year
        ]
        
        found_patterns = set()
        for pattern in date_patterns:
            if re.search(pattern, raw_text):
                found_patterns.add(pattern)
        
        if len(found_patterns) > 2:  # More than 2 different date formats
            issues.append("Inconsistent date formatting across resume")
            score -= 15
        
        # Check for missing dates in experience
        for exp in structured_data.work_experience:
            if not exp.start_date:
                issues.append("Missing start dates in work experience")
                score -= 10
                break
        
        return {
            "passed": len(issues) == 0,
            "score": max(score, 0),
            "issues": issues,
            "date_formats_found": len(found_patterns)
        }
    
    def check_bullet_points(self, structured_data: StructuredResumeData, raw_text: str,
                           target_industry: Optional[str] = None, target_role: Optional[str] = None) -> Dict[str, Any]:
        """Check effective use of bullet points."""
        issues = []
        score = 100.0
        
        # Count bullet points in experience descriptions
        total_bullets = 0
        for exp in structured_data.work_experience:
            total_bullets += len(exp.description)
        
        if total_bullets < len(structured_data.work_experience) * 2:  # Less than 2 bullets per job
            issues.append("Insufficient detail in work experience descriptions")
            score -= 20
        
        # Check for action verbs at start of bullets
        action_verbs = [
            "achieved", "developed", "implemented", "managed", "led", "created",
            "improved", "increased", "reduced", "delivered", "designed", "built"
        ]
        
        action_verb_count = 0
        total_descriptions = 0
        
        for exp in structured_data.work_experience:
            for desc in exp.description:
                total_descriptions += 1
                first_word = desc.split()[0].lower() if desc.split() else ""
                if first_word in action_verbs:
                    action_verb_count += 1
        
        if total_descriptions > 0 and (action_verb_count / total_descriptions) < 0.5:
            issues.append("Many bullet points don't start with strong action verbs")
            score -= 15
        
        return {
            "passed": len(issues) == 0,
            "score": max(score, 0),
            "issues": issues,
            "total_bullets": total_bullets,
            "action_verb_ratio": round(action_verb_count / total_descriptions, 2) if total_descriptions > 0 else 0
        }
    
    def _get_relevant_keywords(self, target_industry: Optional[str] = None, 
                              target_role: Optional[str] = None) -> List[str]:
        """Get relevant keywords based on industry and role."""
        keywords = []
        
        if target_industry and target_industry.lower() in self.keyword_categories:
            industry_keywords = self.keyword_categories[target_industry.lower()]
            for category_keywords in industry_keywords.values():
                keywords.extend(category_keywords)
        
        # Add general professional keywords
        general_keywords = [
            "leadership", "management", "communication", "teamwork", "problem solving",
            "analytical", "strategic", "innovative", "results-driven", "collaborative"
        ]
        keywords.extend(general_keywords)
        
        return list(set(keywords))  # Remove duplicates
    
    def _is_valid_email(self, email: str) -> bool:
        """Check if email format is valid."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _is_valid_phone(self, phone: str) -> bool:
        """Check if phone format is ATS-friendly."""
        # Remove common formatting characters
        cleaned = re.sub(r'[^\d]', '', phone)
        return len(cleaned) >= 10
    
    def _has_consistent_date_format(self, text: str) -> bool:
        """Check if dates are consistently formatted."""
        date_formats = []
        
        # Check for different date patterns
        patterns = {
            'slash': r'\d{1,2}/\d{1,2}/\d{4}',
            'dash': r'\d{4}-\d{1,2}-\d{1,2}',
            'month_year': r'\w+ \d{4}',
            'year_only': r'\b\d{4}\b'
        }
        
        for format_name, pattern in patterns.items():
            if re.search(pattern, text):
                date_formats.append(format_name)
        
        return len(date_formats) <= 2  # Allow up to 2 different formats
    
    def _compile_format_issues(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Compile format-related issues from analysis results."""
        issues = []
        
        format_result = analysis_results.get("format_compatibility", {})
        issues.extend(format_result.get("issues", []))
        
        contact_result = analysis_results.get("contact_information", {})
        issues.extend(contact_result.get("issues", []))
        
        return issues
    
    def _compile_structure_issues(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Compile structure-related issues from analysis results."""
        issues = []
        
        sections_result = analysis_results.get("standard_sections", {})
        issues.extend(sections_result.get("issues", []))
        
        headers_result = analysis_results.get("section_headers", {})
        issues.extend(headers_result.get("issues", []))
        
        dates_result = analysis_results.get("date_formatting", {})
        issues.extend(dates_result.get("issues", []))
        
        bullets_result = analysis_results.get("bullet_points", {})
        issues.extend(bullets_result.get("issues", []))
        
        return issues
    
    def _generate_keyword_suggestions(self, missing_keywords: List[str], 
                                    target_industry: Optional[str] = None,
                                    target_role: Optional[str] = None) -> List[str]:
        """Generate keyword suggestions for optimization."""
        suggestions = []
        
        # Prioritize based on industry and role
        if target_industry and target_role:
            role_specific = self._get_role_specific_keywords(target_role)
            suggestions.extend([kw for kw in missing_keywords if kw in role_specific][:3])
        
        # Add high-impact general keywords
        high_impact = ["leadership", "management", "analytical", "strategic", "innovative"]
        suggestions.extend([kw for kw in missing_keywords if kw in high_impact][:2])
        
        # Add remaining missing keywords
        remaining = [kw for kw in missing_keywords if kw not in suggestions]
        suggestions.extend(remaining[:5])
        
        return suggestions[:10]
    
    def _generate_format_recommendations(self, format_issues: List[str]) -> List[str]:
        """Generate format improvement recommendations."""
        recommendations = []
        
        for issue in format_issues:
            if "email" in issue.lower():
                recommendations.append("Add a professional email address (firstname.lastname@domain.com)")
            elif "phone" in issue.lower():
                recommendations.append("Include phone number in standard format (123-456-7890)")
            elif "characters" in issue.lower():
                recommendations.append("Use standard characters and avoid special symbols")
            elif "formatting" in issue.lower():
                recommendations.append("Use consistent formatting throughout the resume")
        
        return recommendations
    
    def _generate_structure_recommendations(self, structure_issues: List[str]) -> List[str]:
        """Generate structure improvement recommendations."""
        recommendations = []
        
        for issue in structure_issues:
            if "experience" in issue.lower():
                recommendations.append("Add work experience section with job titles, companies, and dates")
            elif "education" in issue.lower():
                recommendations.append("Include education section with degree and institution")
            elif "skills" in issue.lower():
                recommendations.append("Add skills section highlighting relevant technical and soft skills")
            elif "summary" in issue.lower():
                recommendations.append("Include professional summary at the top of your resume")
            elif "dates" in issue.lower():
                recommendations.append("Use consistent date formatting (MM/YYYY recommended)")
            elif "bullet" in issue.lower():
                recommendations.append("Use bullet points starting with action verbs to describe achievements")
        
        return recommendations
    
    def _get_role_specific_keywords(self, target_role: str) -> List[str]:
        """Get keywords specific to target role."""
        role_keywords = {
            "software engineer": ["programming", "coding", "development", "algorithms", "debugging"],
            "data scientist": ["analytics", "machine learning", "statistics", "modeling", "visualization"],
            "product manager": ["roadmap", "strategy", "stakeholder", "requirements", "user experience"],
            "marketing manager": ["campaigns", "branding", "digital marketing", "analytics", "roi"]
        }
        
        role_lower = target_role.lower()
        for role, keywords in role_keywords.items():
            if role in role_lower:
                return keywords
        
        return []