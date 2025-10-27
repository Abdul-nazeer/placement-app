from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from enum import Enum

from app.core.database import Base


class CategoryType(str, Enum):
    APTITUDE = "aptitude"
    CODING = "coding"
    COMMUNICATION = "communication"
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"


class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True, index=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    type = Column(String(50), nullable=False, index=True)  # CategoryType enum
    
    # Hierarchy support
    parent_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True, index=True)
    level = Column(Integer, nullable=False, default=0)  # 0 = root, 1 = subcategory, etc.
    sort_order = Column(Integer, nullable=False, default=0)
    
    # Metadata
    icon = Column(String(100), nullable=True)
    color = Column(String(7), nullable=True)  # Hex color code
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Analytics
    question_count = Column(Integer, nullable=False, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    parent = relationship("Category", remote_side=[id], back_populates="children")
    children = relationship("Category", back_populates="parent", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name}, type={self.type}, level={self.level})>"


class Tag(Base):
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True, index=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    type = Column(String(50), nullable=False, index=True)  # company, topic, skill, etc.
    
    # Metadata
    color = Column(String(7), nullable=True)  # Hex color code
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Analytics
    usage_count = Column(Integer, nullable=False, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def increment_usage(self):
        """Increment usage count"""
        self.usage_count += 1
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name}, type={self.type}, usage_count={self.usage_count})>"


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False, unique=True, index=True)
    slug = Column(String(200), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    
    # Company details
    industry = Column(String(100), nullable=True)
    size = Column(String(50), nullable=True)  # startup, small, medium, large, enterprise
    headquarters = Column(String(200), nullable=True)
    website = Column(String(500), nullable=True)
    logo_url = Column(String(500), nullable=True)
    
    # Metadata
    is_active = Column(Boolean, nullable=False, default=True)
    is_featured = Column(Boolean, nullable=False, default=False)
    
    # Analytics
    question_count = Column(Integer, nullable=False, default=0)
    popularity_score = Column(Integer, nullable=False, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Company(id={self.id}, name={self.name}, industry={self.industry})>"


class QuestionCollection(Base):
    __tablename__ = "question_collections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False, index=True)
    slug = Column(String(200), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    
    # Collection metadata
    type = Column(String(50), nullable=False, index=True)  # company_pack, topic_pack, custom, etc.
    difficulty_level = Column(Integer, nullable=True)  # Overall difficulty
    estimated_time = Column(Integer, nullable=True)  # Estimated completion time in minutes
    
    # Organization
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True, index=True)
    
    # Access control
    is_public = Column(Boolean, nullable=False, default=True)
    is_premium = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Analytics
    question_count = Column(Integer, nullable=False, default=0)
    usage_count = Column(Integer, nullable=False, default=0)
    average_score = Column(Integer, nullable=True)
    
    # Administrative
    created_by = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    company = relationship("Company")
    category = relationship("Category")
    
    def __repr__(self):
        return f"<QuestionCollection(id={self.id}, name={self.name}, type={self.type}, question_count={self.question_count})>"


# Create indexes for performance
Index('idx_categories_type_active', Category.type, Category.is_active)
Index('idx_categories_parent_level', Category.parent_id, Category.level)
Index('idx_tags_type_active', Tag.type, Tag.is_active)
Index('idx_companies_active_featured', Company.is_active, Company.is_featured)
Index('idx_question_collections_type_public', QuestionCollection.type, QuestionCollection.is_public)