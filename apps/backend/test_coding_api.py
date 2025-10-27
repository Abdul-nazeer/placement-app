#!/usr/bin/env python3
"""
Test script for coding challenge API endpoints.
"""
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any

import httpx
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base
from app.models.user import User
from app.models.coding import CodingChallenge, TestCase, CodeSubmission
from app.services.auth import AuthService
from app.services.coding import CodingService
from app.schemas.coding import CodingChallengeCreate, TestCaseCreate, CodeSubmissionCreate


# Test configuration
TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_pass@localhost:5432/test_placement_prep"
BASE_URL = "http://localhost:8000/api/v1"


class TestCodingAPI:
    """Test class for coding challenge API endpoints."""
    
    def __init__(self):
        self.engine = None
        self.session_factory = None
        self.client = httpx.AsyncClient(base_url=BASE_URL)
        self.admin_token = None
        self.user_token = None
        self.test_challenge_id = None
    
    async def setup(self):
        """Set up test environment."""
        # Create test database engine
        self.engine = create_async_engine(TEST_DATABASE_URL, echo=True)
        self.session_factory = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # Create tables
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Create test users and get tokens
        await self.create_test_users()
        
        print("✅ Test setup completed")
    
    async def teardown(self):
        """Clean up test environment."""
        await self.client.aclose()
        if self.engine:
            await self.engine.dispose()
        print("✅ Test teardown completed")
    
    async def create_test_users(self):
        """Create test users and authenticate."""
        async with self.session_factory() as db:
            auth_service = AuthService(db)
            
            # Create admin user
            admin_data = {
                "email": "admin@test.com",
                "password": "admin123",
                "name": "Test Admin",
                "role": "admin"
            }
            
            # Create regular user
            user_data = {
                "email": "user@test.com", 
                "password": "user123",
                "name": "Test User",
                "role": "student"
            }
            
            try:
                admin_user = await auth_service.register_user(admin_data)
                regular_user = await auth_service.register_user(user_data)
                
                # Get tokens
                admin_login = await auth_service.authenticate_user({
                    "email": "admin@test.com",
                    "password": "admin123"
                })
                user_login = await auth_service.authenticate_user({
                    "email": "user@test.com", 
                    "password": "user123"
                })
                
                self.admin_token = admin_login["access_token"]
                self.user_token = user_login["access_token"]
                
                print("✅ Test users created and authenticated")
                
            except Exception as e:
                print(f"❌ Failed to create test users: {e}")
                raise
    
    def get_auth_headers(self, token: str) -> Dict[str, str]:
        """Get authorization headers."""
        return {"Authorization": f"Bearer {token}"}
    
    async def test_create_challenge(self):
        """Test creating a coding challenge."""
        print("\n🧪 Testing challenge creation...")
        
        challenge_data = {
            "title": "Two Sum Problem",
            "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
            "difficulty": "easy",
            "category": "Array",
            "topic_tags": ["Array", "Hash Table"],
            "company_tags": ["Google", "Amazon"],
            "time_limit": 5000,
            "memory_limit": 256,
            "template_code": {
                "python": "def two_sum(nums, target):\n    # Your code here\n    pass",
                "java": "public int[] twoSum(int[] nums, int target) {\n    // Your code here\n    return new int[]{};\n}"
            },
            "solution_approach": "Use a hash map to store complements",
            "hints": ["Think about what you need to find", "Use a hash map"],
            "test_cases": [
                {
                    "input_data": "[2,7,11,15]\n9",
                    "expected_output": "[0,1]",
                    "is_sample": True,
                    "is_hidden": False,
                    "weight": 1.0,
                    "explanation": "nums[0] + nums[1] = 2 + 7 = 9"
                },
                {
                    "input_data": "[3,2,4]\n6",
                    "expected_output": "[1,2]",
                    "is_sample": False,
                    "is_hidden": True,
                    "weight": 1.0
                }
            ]
        }
        
        response = await self.client.post(
            "/coding/challenges",
            json=challenge_data,
            headers=self.get_auth_headers(self.admin_token)
        )
        
        if response.status_code == 201:
            result = response.json()
            self.test_challenge_id = result["id"]
            print(f"✅ Challenge created successfully: {result['title']}")
            print(f"   Challenge ID: {self.test_challenge_id}")
            return True
        else:
            print(f"❌ Failed to create challenge: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    async def test_get_challenges(self):
        """Test getting challenges list."""
        print("\n🧪 Testing get challenges...")
        
        response = await self.client.get(
            "/coding/challenges",
            headers=self.get_auth_headers(self.user_token)
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Retrieved {len(result['challenges'])} challenges")
            print(f"   Total: {result['total']}")
            return True
        else:
            print(f"❌ Failed to get challenges: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    async def test_get_challenge_detail(self):
        """Test getting challenge details."""
        if not self.test_challenge_id:
            print("❌ No test challenge ID available")
            return False
        
        print("\n🧪 Testing get challenge detail...")
        
        response = await self.client.get(
            f"/coding/challenges/{self.test_challenge_id}",
            headers=self.get_auth_headers(self.user_token)
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Retrieved challenge: {result['title']}")
            print(f"   Test cases: {len(result['test_cases'])}")
            return True
        else:
            print(f"❌ Failed to get challenge detail: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    async def test_submit_code(self):
        """Test code submission."""
        if not self.test_challenge_id:
            print("❌ No test challenge ID available")
            return False
        
        print("\n🧪 Testing code submission...")
        
        submission_data = {
            "challenge_id": self.test_challenge_id,
            "language": "python",
            "code": "def two_sum(nums, target):\n    num_map = {}\n    for i, num in enumerate(nums):\n        complement = target - num\n        if complement in num_map:\n            return [num_map[complement], i]\n        num_map[num] = i\n    return []"
        }
        
        response = await self.client.post(
            "/coding/submissions",
            json=submission_data,
            headers=self.get_auth_headers(self.user_token)
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Code submitted successfully")
            print(f"   Submission ID: {result['id']}")
            print(f"   Status: {result['status']}")
            
            # Wait a bit for execution to complete
            await asyncio.sleep(2)
            
            # Check submission status
            submission_response = await self.client.get(
                f"/coding/submissions/{result['id']}",
                headers=self.get_auth_headers(self.user_token)
            )
            
            if submission_response.status_code == 200:
                submission_result = submission_response.json()
                print(f"   Final Status: {submission_result['status']}")
                print(f"   Score: {submission_result['score']}")
                print(f"   Passed: {submission_result['passed_test_cases']}/{submission_result['total_test_cases']}")
            
            return True
        else:
            print(f"❌ Failed to submit code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    async def test_get_user_stats(self):
        """Test getting user coding statistics."""
        print("\n🧪 Testing user statistics...")
        
        response = await self.client.get(
            "/coding/users/me/stats",
            headers=self.get_auth_headers(self.user_token)
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Retrieved user stats")
            print(f"   Total submissions: {result['total_submissions']}")
            print(f"   Successful submissions: {result['successful_submissions']}")
            print(f"   Average score: {result['average_score']:.2f}")
            return True
        else:
            print(f"❌ Failed to get user stats: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    async def test_utility_endpoints(self):
        """Test utility endpoints."""
        print("\n🧪 Testing utility endpoints...")
        
        # Test categories
        response = await self.client.get(
            "/coding/categories",
            headers=self.get_auth_headers(self.user_token)
        )
        
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Retrieved {len(categories)} categories")
        else:
            print(f"❌ Failed to get categories: {response.status_code}")
            return False
        
        # Test languages
        response = await self.client.get(
            "/coding/languages",
            headers=self.get_auth_headers(self.user_token)
        )
        
        if response.status_code == 200:
            languages = response.json()
            print(f"✅ Retrieved {len(languages)} languages")
        else:
            print(f"❌ Failed to get languages: {response.status_code}")
            return False
        
        # Test difficulties
        response = await self.client.get(
            "/coding/difficulties",
            headers=self.get_auth_headers(self.user_token)
        )
        
        if response.status_code == 200:
            difficulties = response.json()
            print(f"✅ Retrieved {len(difficulties)} difficulty levels")
            return True
        else:
            print(f"❌ Failed to get difficulties: {response.status_code}")
            return False
    
    async def run_all_tests(self):
        """Run all tests."""
        print("🚀 Starting Coding Challenge API Tests")
        print("=" * 50)
        
        try:
            await self.setup()
            
            tests = [
                self.test_create_challenge,
                self.test_get_challenges,
                self.test_get_challenge_detail,
                self.test_submit_code,
                self.test_get_user_stats,
                self.test_utility_endpoints
            ]
            
            passed = 0
            total = len(tests)
            
            for test in tests:
                try:
                    if await test():
                        passed += 1
                except Exception as e:
                    print(f"❌ Test failed with exception: {e}")
            
            print("\n" + "=" * 50)
            print(f"🏁 Test Results: {passed}/{total} tests passed")
            
            if passed == total:
                print("🎉 All tests passed!")
            else:
                print("⚠️  Some tests failed")
            
        except Exception as e:
            print(f"❌ Test setup failed: {e}")
        finally:
            await self.teardown()


async def main():
    """Main test function."""
    tester = TestCodingAPI()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())