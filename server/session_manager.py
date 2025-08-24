import uuid
from sqlalchemy.orm import Session
from sqlalchemy import and_
from .models import ChatSession, ChatMessage, User
from .database import get_db
from typing import List, Optional
from sqlalchemy.sql import func

def create_session(user_id: str, db: Session, title: Optional[str] = None) -> str:
    """Create a new chat session for a user."""
    # Auto-generate title if not provided
    if not title:
        title = "New Chat Session"
    
    session = ChatSession(
        user_id=user_id,
        title=title
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return str(session.id)

def add_message(session_id: str, sender: str, text: str, db: Session, user_id: str, message_data: Optional[dict] = None):
    """Add a message to a chat session with user verification."""
    # Verify the session belongs to the user
    session = db.query(ChatSession).filter(
        and_(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        )
    ).first()
    
    if not session:
        raise ValueError("Session not found or access denied")
    
    message = ChatMessage(
        session_id=session_id,
        sender_type=sender,
        content=text,
        message_data=message_data
    )
    db.add(message)
    
    # Update session title if this is the first user message
    if sender == "user" and not session.title or session.title == "New Chat Session":
        # Use first 50 characters of message as title
        session.title = text[:50] + "..." if len(text) > 50 else text
        session.updated_at = func.now()
    
    db.commit()
    db.refresh(message)
    return message

def get_history(session_id: str, db: Session, user_id: str) -> List[dict]:
    """Get chat history for a session with user verification."""
    # Verify the session belongs to the user
    session = db.query(ChatSession).filter(
        and_(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        )
    ).first()
    
    if not session:
        raise ValueError("Session not found or access denied")
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).all()
    
    return [{"sender": msg.sender_type, "text": msg.content, "created_at": msg.created_at} for msg in messages]

def get_user_sessions(user_id: str, db: Session, limit: int = 50, offset: int = 0) -> List[dict]:
    """Get all chat sessions for a user with pagination."""
    try:
        # Convert string user_id to UUID if needed
        import uuid
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise ValueError(f"Invalid UUID format: {user_id}")
        
        # Use a subquery to count messages for each session
        sessions_with_count = db.query(
            ChatSession,
            func.count(ChatMessage.id).label('message_count')
        ).outerjoin(
            ChatMessage, ChatSession.id == ChatMessage.session_id
        ).filter(
            ChatSession.user_id == user_uuid
        ).group_by(
            ChatSession.id
        ).order_by(
            ChatSession.updated_at.desc()
        ).offset(offset).limit(limit).all()
        
        result = [
            {
                "id": str(session.id),
                "title": session.title,
                "created_at": session.created_at.isoformat() if session.created_at else None,
                "updated_at": session.updated_at.isoformat() if session.updated_at else session.created_at.isoformat() if session.created_at else None,
                "message_count": message_count
            }
            for session, message_count in sessions_with_count
        ]
        
        return result
        
    except Exception as e:
        raise

def get_session_by_id(session_id: str, user_id: str, db: Session) -> Optional[ChatSession]:
    """Get a specific session by ID with user verification."""
    session = db.query(ChatSession).filter(
        and_(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        )
    ).first()
    
    return session

def delete_session(session_id: str, user_id: str, db: Session) -> bool:
    """Delete a chat session with user verification."""
    session = db.query(ChatSession).filter(
        and_(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        )
    ).first()
    
    if not session:
        return False
    
    db.delete(session)
    db.commit()
    return True

def update_session_title(session_id: str, user_id: str, title: str, db: Session) -> bool:
    """Update session title with user verification."""
    session = db.query(ChatSession).filter(
        and_(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        )
    ).first()
    
    if not session:
        return False
    
    session.title = title
    session.updated_at = func.now()
    db.commit()
    return True
