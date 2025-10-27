#!/usr/bin/env python3
"""
Simple test for resume processing services.
"""

import asyncio
from app.services.resume_processing import ResumeProcessor
from app.services.ats_analyzer import ATSCompatibilityAnalyzer
from app.services.skill_extraction import SkillExtractor
from app.schemas.resume import StructuredResumeData, ContactInfo, WorkExperience, Education, Skill


async def test_resume_services():
    """Test resume processing services."""
    
    print("Testing Resume Processing Services...")
    print("=" * 50)
    
    # Initialize services
    resume_processor = ResumeProcessor()
    ats_analyzer = ATSCompatibilityAnalyzer()
    skill_extractor = SkillExtractor()
    
    # Sample resume text
    sample_text = """
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
    """
    
    try:
        # Test 1: Resume parsing
        print("1. Testing Resume Parsing...")
        structured_data = resume_processor.parse_resume_structure(sample_text)
        print(f"✓ Resume parsing successful")
        print(f"  Contact Name: {structured_data.contact_info.name}")
        print(f"  Contact Email: {structured_data.contact_info.email}")
        print(f"  Work Experience: {len(structured_data.work_experience)} jobs")
        print(f"  Education: {len(structured_data.education)} entries")
        print(f"  Skills: {len(structured_data.skills)} skills")
        
        # Test 2: ATS Analysis
        print("\n2. Testing ATS Analysis...")
        ats_analysis = ats_analyzer.analyze_ats_compatibility(
            structured_data, sample_text, "technology", "Software Engineer"
        )
        print(f"✓ ATS analysis successful")
        print(f"  Overall Score: {ats_analysis.overall_score:.1f}/100")
        print(f"  Keyword Score: {ats_analysis.keyword_score:.1f}/100")
        print(f"  Format Score: {ats_analysis.format_score:.1f}/100")
        print(f"  Structure Score: {ats_analysis.structure_score:.1f}/100")
        print(f"  Missing Keywords: {len(ats_analysis.missing_keywords)}")
        
        # Test 3: Skill Extraction
        print("\n3. Testing Skill Extraction...")
        extracted_skills = skill_extractor.extract_skills(sample_text)
        print(f"✓ Skill extraction successful")
        print(f"  Technical Skills: {len(extracted_skills['technical'])}")
        print(f"  Soft Skills: {len(extracted_skills['soft'])}")
        print(f"  Industry Skills: {len(extracted_skills['industry_specific'])}")
        
        # Show some extracted technical skills
        if extracted_skills['technical']:
            print("  Sample Technical Skills:")
            for skill in extracted_skills['technical'][:5]:
                print(f"    - {skill['name']} (confidence: {skill['confidence']})")
        
        # Test 4: Content Analysis
        print("\n4. Testing Content Analysis...")
        content_analysis = resume_processor.analyze_content_quality(structured_data)
        print(f"✓ Content analysis successful")
        print(f"  Readability Score: {content_analysis.readability_score:.1f}/100")
        print(f"  Grammar Score: {content_analysis.grammar_score:.1f}/100")
        print(f"  Impact Score: {content_analysis.impact_score:.1f}/100")
        
        # Test 5: Complete Analysis
        print("\n5. Testing Complete Analysis...")
        complete_analysis = await resume_processor.generate_complete_analysis(
            structured_data, "Software Engineer"
        )
        print(f"✓ Complete analysis successful")
        print(f"  Overall Score: {complete_analysis.overall_score:.1f}/100")
        print(f"  Strengths: {len(complete_analysis.strengths)}")
        print(f"  Weaknesses: {len(complete_analysis.weaknesses)}")
        print(f"  Priority Improvements: {len(complete_analysis.priority_improvements)}")
        
        if complete_analysis.strengths:
            print("  Sample Strengths:")
            for strength in complete_analysis.strengths[:2]:
                print(f"    - {strength}")
        
        if complete_analysis.priority_improvements:
            print("  Sample Improvements:")
            for improvement in complete_analysis.priority_improvements[:2]:
                print(f"    - {improvement}")
        
        print("\n" + "=" * 50)
        print("✓ All resume processing services working correctly!")
        return True
        
    except Exception as e:
        print(f"\n✗ Error testing resume services: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    asyncio.run(test_resume_services())