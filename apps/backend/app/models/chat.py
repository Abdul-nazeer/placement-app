from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class ChatConversation(Base):
    __tablename__ = "chat_conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("test_sessions.id", ondelete="SET NULL"), nullable=True, index=True)
    context_type = Column(String(50), nullable=False, index=True)  # coding, aptitude, general, mock_interview
    title = Column(String(255), nullable=True)  # Auto-generated or user-provided title
    messages = Column(JSON, default=list)  # Array of message objects
    is_active = Column(String(20), default="active")  # active, archived, deleted
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="chat_conversations")
    
    def __repr__(self):
        return f"<ChatConversation(id={self.id}, user_id={self.user_id}, context={self.context_type})>"


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("chat_conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    extra_data = Column(JSON, default=dict)  # Additional context, tokens used, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    conversation = relationship("ChatConversation")
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, conversation_id={self.conversation_id}, role={self.role})>"