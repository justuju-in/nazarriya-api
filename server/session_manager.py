import uuid
from sqlalchemy.orm import Session
from .models import ChatSession, ChatMessage
from .database import get_db

def create_session(user_id: str, db: Session) -> str:
    """Create a new chat session for a user."""
    session = ChatSession(
        user_id=user_id,
        title="New Chat Session"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return str(session.id)

def add_message(session_id: str, sender: str, text: str, db: Session):
    """Add a message to a chat session."""
    message = ChatMessage(
        session_id=session_id,
        sender_type=sender,
        content=text
    )
    db.add(message)
    db.commit()
    db.refresh(message)

def get_history(session_id: str, db: Session):
    """Get chat history for a session."""
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).all()
    
    return [{"sender": msg.sender_type, "text": msg.content} for msg in messages]
