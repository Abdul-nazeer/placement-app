"""Skill extraction and keyword matching service."""

import re
import json
from typing import Dict, List, Set, Tuple, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class SkillExtractor:
    """Service for extracting and matching skills from resume text."""
    
    def __init__(self):
        """Initialize skill extractor with predefined skill databases."""
        self.technical_skills = self._load_technical_skills()
        self.soft_skills = self._load_soft_skills()
        self.industry_keywords = self._load_industry_keywords()
        self.job_title_keywords = self._load_job_title_keywords()
    
    def _load_technical_skills(self) -> Dict[str, List[str]]:
        """Load technical skills database."""
        return {
            "programming_languages": [
                "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
                "php", "ruby", "swift", "kotlin", "scala", "r", "matlab", "perl",
                "shell", "bash", "powershell", "sql", "html", "css", "sass", "less"
            ],
            "frameworks": [
                "react", "angular", "vue", "svelte", "node.js", "express", "fastapi",
                "django", "flask", "spring", "spring boot", "laravel", "rails",
                "asp.net", ".net", "xamarin", "flutter", "react native", "ionic"
            ],
            "databases": [
                "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "cassandra",
                "oracle", "sql server", "sqlite", "dynamodb", "firebase", "neo4j"
            ],
            "cloud_platforms": [
                "aws", "azure", "google cloud", "gcp", "heroku", "digitalocean",
                "linode", "vultr", "cloudflare", "vercel", "netlify"
            ],
            "devops_tools": [
                "docker", "kubernetes", "jenkins", "gitlab ci", "github actions",
                "terraform", "ansible", "chef", "puppet", "vagrant", "helm"
            ],
            "data_science": [
                "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
                "matplotlib", "seaborn", "plotly", "jupyter", "spark", "hadoop"
            ],
            "testing": [
                "jest", "mocha", "chai", "pytest", "unittest", "selenium", "cypress",
                "playwright", "postman", "insomnia", "junit", "testng"
            ],
            "version_control": [
                "git", "github", "gitlab", "bitbucket", "svn", "mercurial"
            ],
            "operating_systems": [
                "linux", "ubuntu", "centos", "redhat", "windows", "macos", "unix"
            ],
            "web_technologies": [
                "rest api", "graphql", "websockets", "microservices", "serverless",
                "oauth", "jwt", "cors", "ajax", "json", "xml", "yaml"
            ]
        }
    
    def _load_soft_skills(self) -> List[str]:
        """Load soft skills database."""
        return [
            "leadership", "communication", "teamwork", "problem solving", "analytical thinking",
            "creative thinking", "adaptability", "time management", "project management",
            "critical thinking", "decision making", "conflict resolution", "negotiation",
            "presentation skills", "public speaking", "writing skills", "research skills",
            "attention to detail", "organizational skills", "multitasking", "prioritization",
            "customer service", "sales skills", "marketing skills", "strategic planning",
            "innovation", "collaboration", "mentoring", "coaching", "training",
            "emotional intelligence", "cultural awareness", "flexibility", "resilience"
        ]
    
    def _load_industry_keywords(self) -> Dict[str, List[str]]:
        """Load industry-specific keywords."""
        return {
            "technology": [
                "software development", "web development", "mobile development", "ai", "ml",
                "machine learning", "artificial intelligence", "data science", "cybersecurity",
                "blockchain", "iot", "cloud computing", "devops", "agile", "scrum"
            ],
            "finance": [
                "financial analysis", "risk management", "investment banking", "portfolio management",
                "trading", "derivatives", "compliance", "audit", "accounting", "fintech"
            ],
            "healthcare": [
                "patient care", "clinical research", "medical devices", "pharmaceuticals",
                "healthcare administration", "telemedicine", "electronic health records"
            ],
            "marketing": [
                "digital marketing", "content marketing", "social media marketing", "seo", "sem",
                "email marketing", "brand management", "market research", "analytics"
            ],
            "consulting": [
                "business analysis", "process improvement", "change management", "strategy",
                "operations", "transformation", "stakeholder management"
            ]
        }
    
    def _load_job_title_keywords(self) -> Dict[str, List[str]]:
        """Load job title specific keywords."""
        return {
            "software_engineer": [
                "algorithms", "data structures", "system design", "code review",
                "debugging", "optimization", "scalability", "performance tuning"
            ],
            "data_scientist": [
                "statistical analysis", "predictive modeling", "data visualization",
                "feature engineering", "model validation", "a/b testing"
            ],
            "product_manager": [
                "product roadmap", "user stories", "market research", "competitive analysis",
                "stakeholder management", "product strategy", "user experience"
            ],
            "devops_engineer": [
                "ci/cd", "infrastructure as code", "monitoring", "logging", "automation",
                "containerization", "orchestration", "cloud architecture"
            ],
            "frontend_developer": [
                "responsive design", "cross-browser compatibility", "user interface",
                "user experience", "accessibility", "performance optimization"
            ],
            "backend_developer": [
                "api development", "database design", "server architecture", "security",
                "authentication", "authorization", "caching", "load balancing"
            ]
        }
    
    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract skills from resume text."""
        text_lower = text.lower()
        
        extracted_skills = {
            "technical": [],
            "soft": [],
            "industry_specific": []
        }
        
        # Extract technical skills
        for category, skills in self.technical_skills.items():
            for skill in skills:
                if self._is_skill_present(skill, text_lower):
                    extracted_skills["technical"].append({
                        "name": skill,
                        "category": category,
                        "confidence": self._calculate_skill_confidence(skill, text_lower)
                    })
        
        # Extract soft skills
        for skill in self.soft_skills:
            if self._is_skill_present(skill, text_lower):
                extracted_skills["soft"].append({
                    "name": skill,
                    "confidence": self._calculate_skill_confidence(skill, text_lower)
                })
        
        # Extract industry-specific skills
        for industry, keywords in self.industry_keywords.items():
            for keyword in keywords:
                if self._is_skill_present(keyword, text_lower):
                    extracted_skills["industry_specific"].append({
                        "name": keyword,
                        "industry": industry,
                        "confidence": self._calculate_skill_confidence(keyword, text_lower)
                    })
        
        return extracted_skills
    
    def _is_skill_present(self, skill: str, text: str) -> bool:
        """Check if a skill is present in the text."""
        # Handle multi-word skills
        if " " in skill:
            # For multi-word skills, check for exact phrase or variations
            patterns = [
                skill,
                skill.replace(" ", "-"),
                skill.replace(" ", "_"),
                skill.replace(".", "")
            ]
            return any(pattern in text for pattern in patterns)
        else:
            # For single words, use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill) + r'\b'
            return bool(re.search(pattern, text, re.IGNORECASE))
    
    def _calculate_skill_confidence(self, skill: str, text: str) -> float:
        """Calculate confidence score for skill extraction."""
        # Count occurrences
        count = text.count(skill.lower())
        
        # Base confidence on frequency and context
        confidence = min(count * 0.3 + 0.7, 1.0)
        
        # Boost confidence if skill appears in context
        context_patterns = [
            f"experienced in {skill}",
            f"proficient in {skill}",
            f"expert in {skill}",
            f"skilled in {skill}",
            f"knowledge of {skill}",
            f"using {skill}",
            f"with {skill}",
            f"{skill} development",
            f"{skill} programming"
        ]
        
        for pattern in context_patterns:
            if pattern in text:
                confidence = min(confidence + 0.2, 1.0)
                break
        
        return round(confidence, 2)
    
    def match_job_requirements(self, extracted_skills: Dict[str, List[str]], 
                              job_description: str) -> Dict[str, any]:
        """Match extracted skills against job requirements."""
        job_text = job_description.lower()
        
        # Extract required skills from job description
        required_skills = self.extract_skills(job_text)
        
        # Calculate match scores
        technical_match = self._calculate_match_score(
            extracted_skills.get("technical", []),
            required_skills.get("technical", [])
        )
        
        soft_skills_match = self._calculate_match_score(
            extracted_skills.get("soft", []),
            required_skills.get("soft", [])
        )
        
        industry_match = self._calculate_match_score(
            extracted_skills.get("industry_specific", []),
            required_skills.get("industry_specific", [])
        )
        
        # Overall match score
        overall_match = (technical_match * 0.5 + soft_skills_match * 0.3 + industry_match * 0.2)
        
        # Identify missing skills
        missing_technical = self._find_missing_skills(
            extracted_skills.get("technical", []),
            required_skills.get("technical", [])
        )
        
        missing_soft = self._find_missing_skills(
            extracted_skills.get("soft", []),
            required_skills.get("soft", [])
        )
        
        return {
            "overall_match_score": round(overall_match, 2),
            "technical_match_score": round(technical_match, 2),
            "soft_skills_match_score": round(soft_skills_match, 2),
            "industry_match_score": round(industry_match, 2),
            "missing_technical_skills": missing_technical,
            "missing_soft_skills": missing_soft,
            "matched_skills": self._find_matched_skills(extracted_skills, required_skills),
            "skill_gap_analysis": self._generate_skill_gap_analysis(extracted_skills, required_skills)
        }
    
    def _calculate_match_score(self, candidate_skills: List[Dict], required_skills: List[Dict]) -> float:
        """Calculate match score between candidate and required skills."""
        if not required_skills:
            return 100.0
        
        if not candidate_skills:
            return 0.0
        
        candidate_skill_names = {skill["name"].lower() for skill in candidate_skills}
        required_skill_names = {skill["name"].lower() for skill in required_skills}
        
        matched_skills = candidate_skill_names.intersection(required_skill_names)
        match_score = (len(matched_skills) / len(required_skill_names)) * 100
        
        return match_score
    
    def _find_missing_skills(self, candidate_skills: List[Dict], required_skills: List[Dict]) -> List[str]:
        """Find skills that are required but missing from candidate."""
        candidate_skill_names = {skill["name"].lower() for skill in candidate_skills}
        required_skill_names = {skill["name"].lower() for skill in required_skills}
        
        missing = required_skill_names - candidate_skill_names
        return list(missing)
    
    def _find_matched_skills(self, candidate_skills: Dict, required_skills: Dict) -> Dict[str, List[str]]:
        """Find skills that match between candidate and requirements."""
        matched = {"technical": [], "soft": [], "industry_specific": []}
        
        for category in matched.keys():
            candidate_names = {skill["name"].lower() for skill in candidate_skills.get(category, [])}
            required_names = {skill["name"].lower() for skill in required_skills.get(category, [])}
            matched[category] = list(candidate_names.intersection(required_names))
        
        return matched
    
    def _generate_skill_gap_analysis(self, candidate_skills: Dict, required_skills: Dict) -> Dict[str, any]:
        """Generate detailed skill gap analysis."""
        analysis = {
            "strengths": [],
            "gaps": [],
            "recommendations": []
        }
        
        # Identify strengths
        for category, skills in candidate_skills.items():
            high_confidence_skills = [skill for skill in skills if skill.get("confidence", 0) > 0.8]
            if high_confidence_skills:
                analysis["strengths"].append(f"Strong {category} skills: {', '.join([s['name'] for s in high_confidence_skills[:3]])}")
        
        # Identify gaps
        for category, skills in required_skills.items():
            candidate_names = {skill["name"].lower() for skill in candidate_skills.get(category, [])}
            missing = [skill["name"] for skill in skills if skill["name"].lower() not in candidate_names]
            if missing:
                analysis["gaps"].append(f"Missing {category} skills: {', '.join(missing[:3])}")
        
        # Generate recommendations
        if analysis["gaps"]:
            analysis["recommendations"].append("Focus on acquiring the missing technical skills through online courses or projects")
            analysis["recommendations"].append("Highlight transferable skills that demonstrate your ability to learn new technologies")
            analysis["recommendations"].append("Consider adding relevant projects or certifications to showcase your capabilities")
        
        return analysis
    
    def suggest_skill_improvements(self, extracted_skills: Dict[str, List[str]], 
                                 target_role: Optional[str] = None) -> List[Dict[str, str]]:
        """Suggest skill improvements based on target role."""
        suggestions = []
        
        if target_role:
            target_role_lower = target_role.lower()
            
            # Get role-specific keywords
            role_keywords = []
            for role, keywords in self.job_title_keywords.items():
                if role.replace("_", " ") in target_role_lower:
                    role_keywords = keywords
                    break
            
            # Check for missing role-specific skills
            candidate_technical = {skill["name"].lower() for skill in extracted_skills.get("technical", [])}
            
            for keyword in role_keywords:
                if keyword.lower() not in candidate_technical:
                    suggestions.append({
                        "type": "missing_skill",
                        "skill": keyword,
                        "suggestion": f"Consider adding '{keyword}' to your skillset for {target_role} roles",
                        "priority": "high"
                    })
        
        # General suggestions
        technical_count = len(extracted_skills.get("technical", []))
        soft_count = len(extracted_skills.get("soft", []))
        
        if technical_count < 5:
            suggestions.append({
                "type": "skill_quantity",
                "suggestion": "Add more technical skills to strengthen your profile",
                "priority": "medium"
            })
        
        if soft_count < 3:
            suggestions.append({
                "type": "soft_skills",
                "suggestion": "Include more soft skills like leadership, communication, and teamwork",
                "priority": "medium"
            })
        
        return suggestions[:10]  # Return top 10 suggestions
    
    def generate_keyword_optimization_report(self, text: str, target_keywords: List[str]) -> Dict[str, any]:
        """Generate keyword optimization report."""
        text_lower = text.lower()
        
        # Analyze current keyword usage
        keyword_analysis = {}
        for keyword in target_keywords:
            count = text_lower.count(keyword.lower())
            density = (count / len(text.split())) * 100 if text else 0
            
            keyword_analysis[keyword] = {
                "count": count,
                "density": round(density, 2),
                "present": count > 0,
                "optimal_density": self._get_optimal_keyword_density(keyword)
            }
        
        # Calculate optimization score
        present_keywords = sum(1 for kw in keyword_analysis.values() if kw["present"])
        optimization_score = (present_keywords / len(target_keywords)) * 100 if target_keywords else 100
        
        # Generate recommendations
        recommendations = []
        for keyword, analysis in keyword_analysis.items():
            if not analysis["present"]:
                recommendations.append(f"Add '{keyword}' to improve ATS compatibility")
            elif analysis["density"] < analysis["optimal_density"]:
                recommendations.append(f"Increase usage of '{keyword}' (current: {analysis['density']}%, optimal: {analysis['optimal_density']}%)")
        
        return {
            "optimization_score": round(optimization_score, 2),
            "keyword_analysis": keyword_analysis,
            "recommendations": recommendations,
            "total_keywords": len(target_keywords),
            "present_keywords": present_keywords,
            "missing_keywords": len(target_keywords) - present_keywords
        }
    
    def _get_optimal_keyword_density(self, keyword: str) -> float:
        """Get optimal keyword density for ATS optimization."""
        # General rule: 1-3% density for important keywords
        if len(keyword.split()) > 1:  # Multi-word keywords
            return 1.0
        else:  # Single word keywords
            return 2.0