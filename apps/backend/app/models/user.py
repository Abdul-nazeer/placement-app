from sqlalchemy import Column, String, Boolean, DateTime, Integer, JSON, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from enum import Enum

from app.core.database import Base


class UserRole(str, Enum):
    """User role enumeration"""
    STUDENT = "student"
    TRAINER = "trainer"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default=UserRole.STUDENT.value)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    test_sessions = relationship("TestSession", back_populates="user", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="user", cascade="all, delete-orphan")
    chat_conversations = relationship("ChatConversation", back_populates="user", cascade="all, delete-orphan")
    communication_sessions = relationship("CommunicationSession", back_populates="user", cascade="all, delete-orphan")
    communication_progress = relationship("CommunicationProgress", back_populates="user", cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    interview_sessions = relationship("InterviewSession", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    college = Column(String(255), nullable=True)
    graduation_year = Column(Integer, nullable=True)
    target_companies = Column(JSON, default=list)
    preferred_roles = Column(JSON, default=list)
    skill_levels = Column(JSON, default=dict)  # {"python": 8, "javascript": 6, "sql": 7}
    bio = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    github_url = Column(String(500), nullable=True)
    resume_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="profile")
    
    def __repr__(self):
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, college={self.college})>"


class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token_jti = Column(String(255), unique=True, nullable=False, index=True)  # JWT ID claim
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<TokenBlacklist(jti={self.token_jti}, user_id={self.user_id})>"