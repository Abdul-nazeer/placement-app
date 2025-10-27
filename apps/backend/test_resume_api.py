#!/usr/bin/env python3
"""
Test script for Resume Analysis API endpoints.
"""

import asyncio
import json
import tempfile
from pathlib import Path
from uuid import uuid4

import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base
from app.models.user import User, UserProfile
from app.models.resume import Resume
from app.services.resume_processing import ResumeProcessor
from app.services.ats_analyzer import ATSCompatibilityAnalyzer
from app.services.skill_extraction import SkillExtractor


class ResumeAPITester:
    """Test class for Resume API functionality."""
    
    def __init__(self):
        self.base_url = "http://localhost:8000/api/v1"
        self.test_user_email = "resume_test@example.com"
        self.test_user_password = "testpass123"
        self.auth_token = None
        
        # Initialize services
        self.resume_processor = ResumeProcessor()
        self.ats_analyzer = ATSCompatibilityAnalyzer()
        self.skill_extractor = SkillExtractor()
    
    async def setup_test_user(self):
        """Create a test user for API testing."""
        
        # Create database engine
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        try:
            # Check if test user exists
            existing_user = db.query(User).filter(User.email == self.test_user_email).first()
            if existing_user:
                print(f"Test user {self.test_user_email} already exists")
                return existing_user.id
            
            # Create test user
            from app.core.security import get_password_hash
            
            test_user = User(
                email=self.test_user_email,
                name="Resume Test User",
                password_hash=get_password_hash(self.test_user_password),
                role="student"
            )
            
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            
            # Create user profile
            profile = UserProfile(
                user_id=test_user.id,
                college="Test University",
                graduation_year=2024,
                target_companies=["Google", "Microsoft"],
                preferred_roles=["Software Engineer"]
            )
            
            db.add(profile)
            db.commit()
            
            print(f"Created test user: {test_user.id}")
            return test_user.id
            
        finally:
            db.close()
    
    async def authenticate(self):
        """Authenticate and get access token."""
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/login",
                data={
                    "username": self.test_user_email,
                    "password": self.test_user_password
                }
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data["access_token"]
                print("✓ Authentication successful")
                return True
            else:
                print(f"✗ Authentication failed: {response.status_code} - {response.text}")
                return False
    
    def get_auth_headers(self):
        """Get authorization headers."""
        return {"Authorization": f"Bearer {self.auth_token}"}
    
    def create_sample_resume_file(self) -> Path:
        """Create a sample resume file for testing."""
        
        sample_content = """
John Doe
Software Engineer
john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe

PROFESSIONAL SUMMARY
Experienced software engineer with 5+ years developing scalable web applications.
Proficient in Python, JavaScript, and cloud technologies.

WORK EXPERIENCE

Senior Software Engineer - Tech Corp (2021 - Present)
• Developed and maintained 10+ microservices using Python and FastAPI
• Improved system performance by 40% through optimization and caching
• Led a team of 4 developers on critical product features
• Implemented CI/CD pipelines reducing deployment time by 60%

Software Engineer - StartupXYZ (2019 - 2021)
• Built responsive web applications using React and Node.js
• Collaborated with cross-functional teams to deliver features on time
• Wrote comprehensive unit tests achieving 85% code coverage

EDUCATION
Bachelor of Science in Computer Science
University of Technology (2015 - 2019)
GPA: 3.8/4.0

TECHNICAL SKILLS
Programming Languages: Python, JavaScript, Java, C++
Frameworks: FastAPI, React, Django, Express.js
Databases: PostgreSQL, MongoDB, Redis
Cloud: AWS, Docker, Kubernetes
Tools: Git, Jenkins, Jira

PROJECTS
E-commerce Platform
• Built full-stack application serving 1000+ users
• Implemented payment processing and inventory management
• Technologies: React, Node.js, PostgreSQL, AWS
        """
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        temp_file.write(sample_content.strip())
        temp_file.close()
        
        return Path(temp_file.name)
    
    async def test_resume_upload(self):
        """Test resume upload endpoint."""
        
        print("\n=== Testing Resume Upload ===")
        
        # Create sample resume file
        resume_file = self.create_sample_resume_file()
        
        try:
            async with httpx.AsyncClient() as client:
                with open(resume_file, 'rb') as f:
                    files = {"file": ("sample_resume.txt", f, "text/plain")}
                    data = {
                        "target_role": "Software Engineer",
                        "target_industry": "technology"
                    }
                    
                    response = await client.post(
                        f"{self.base_url}/resume/upload",
                        files=files,
                        data=data,
                        headers=self.get_auth_headers()
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✓ Resume uploaded successfully: {result['id']}")
                    print(f"  Filename: {result['filename']}")
                    print(f"  Status: {result['processing_status']}")
                    return result['id']
                else:
                    print(f"✗ Resume upload failed: {response.status_code} - {response.text}")
                    return None
        
        finally:
            # Clean up temporary file
            resume_file.unlink()
    
    async def test_get_resumes(self):
        """Test get user resumes endpoint."""
        
        print("\n=== Testing Get Resumes ===")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/resume/",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                resumes = response.json()
                print(f"✓ Retrieved {len(resumes)} resumes")
                for resume in resumes:
                    print(f"  - {resume['filename']} (Status: {resume['processing_status']})")
                return resumes
            else:
                print(f"✗ Get resumes failed: {response.status_code} - {response.text}")
                return []
    
    async def test_resume_analysis(self, resume_id: str):
        """Test resume analysis endpoint."""
        
        print(f"\n=== Testing Resume Analysis for {resume_id} ===")
        
        # Wait a bit for processing (in real scenario, this would be background)
        await asyncio.sleep(2)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/resume/{resume_id}/analysis",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                analysis = response.json()
                print(f"✓ Resume analysis retrieved")
                print(f"  ATS Score: {analysis['ats_score']}")
                print(f"  Suggestions: {len(analysis['suggestions'])} items")
                return analysis
            elif response.status_code == 400:
                print(f"⚠ Resume analysis not ready yet: {response.json()['detail']}")
                return None
            else:
                print(f"✗ Resume analysis failed: {response.status_code} - {response.text}")
                return None
    
    async def test_resume_templates(self):
        """Test resume templates endpoint."""
        
        print("\n=== Testing Resume Templates ===")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/resume/templates/")
            
            if response.status_code == 200:
                templates = response.json()
                print(f"✓ Retrieved {len(templates)} resume templates")
                for template in templates[:3]:  # Show first 3
                    print(f"  - {template['name']} ({template['category']})")
                return templates
            else:
                print(f"✗ Get templates failed: {response.status_code} - {response.text}")
                return []
    
    async def test_service_functionality(self):
        """Test core service functionality."""
        
        print("\n=== Testing Service Functionality ===")
        
        # Test resume processing
        sample_text = """
        John Doe
        Software Engineer
        john.doe@email.com
        
        EXPERIENCE
        Senior Developer at TechCorp (2020-2023)
        - Developed web applications using Python and React
        - Improved performance by 50%
        
        SKILLS
        Python, JavaScript, React, SQL
        """
        
        try:
            # Test text parsing
            structured_data = self.resume_processor.parse_resume_structure(sample_text)
            print(f"✓ Resume parsing successful")
            print(f"  Contact: {structured_data.contact_info.name}")
            print(f"  Experience: {len(structured_data.work_experience)} jobs")
            print(f"  Skills: {len(structured_data.skills)} skills")
            
            # Test ATS analysis
            ats_analysis = self.ats_analyzer.analyze_ats_compatibility(
                structured_data, sample_text, "technology", "Software Engineer"
            )
            print(f"✓ ATS analysis successful")
            print(f"  Overall Score: {ats_analysis.overall_score:.1f}")
            print(f"  Keyword Score: {ats_analysis.keyword_score:.1f}")
            
            # Test skill extraction
            extracted_skills = self.skill_extractor.extract_skills(sample_text)
            print(f"✓ Skill extraction successful")
            print(f"  Technical Skills: {len(extracted_skills['technical'])}")
            print(f"  Soft Skills: {len(extracted_skills['soft'])}")
            
            return True
            
        except Exception as e:
            print(f"✗ Service functionality test failed: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all resume API tests."""
        
        print("Starting Resume API Tests...")
        print("=" * 50)
        
        # Setup
        await self.setup_test_user()
        
        if not await self.authenticate():
            print("Cannot proceed without authentication")
            return
        
        # Test service functionality
        await self.test_service_functionality()
        
        # Test API endpoints
        resume_id = await self.test_resume_upload()
        await self.test_get_resumes()
        await self.test_resume_templates()
        
        if resume_id:
            await self.test_resume_analysis(resume_id)
        
        print("\n" + "=" * 50)
        print("Resume API Tests Completed!")


async def main():
    """Main test function."""
    tester = ResumeAPITester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())