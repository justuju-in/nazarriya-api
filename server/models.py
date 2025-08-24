from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional, List
import uuid
from .database import Base

# Database Models (SQLAlchemy)
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    age = Column(Integer, nullable=True)
    preferred_language = Column(String(50), nullable=True)
    state = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=True)  # Auto-generated from first message
    session_data = Column(JSONB, nullable=True)  # Store session context, preferences
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False, index=True)
    sender_type = Column(String(20), nullable=False)  # 'user' or 'bot'
    content = Column(Text, nullable=False)
    message_data = Column(JSONB, nullable=True)  # Store sources, context, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")

# Pydantic Models for API
class UserCreate(BaseModel):
    email: str
    password: str
    first_name: Optional[str] = None
    age: Optional[int] = None
    preferred_language: Optional[str] = None
    state: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserProfile(BaseModel):
    id: str
    email: str
    first_name: Optional[str] = None
    age: Optional[int] = None
    preferred_language: Optional[str] = None
    state: Optional[str] = None
    created_at: str

class ChatMessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    response: str
    sources: Optional[List[str]] = None
    response_data: Optional[dict] = None

class ChatMessageResponse(BaseModel):
    id: str
    session_id: str
    sender_type: str
    content: str
    message_data: Optional[dict] = None
    created_at: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserProfile

# New models for session management
class SessionCreate(BaseModel):
    title: Optional[str] = None

class SessionUpdate(BaseModel):
    title: str

class SessionResponse(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int

class SessionHistoryResponse(BaseModel):
    session_id: str
    history: List[dict]

class MessageResponse(BaseModel):
    sender: str
    text: str
    created_at: str
