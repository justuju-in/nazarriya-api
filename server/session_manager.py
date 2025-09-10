import hashlib
from sqlalchemy.orm import Session
from sqlalchemy import and_
from .models import ChatSession, ChatMessage
from typing import List, Optional, Dict, Any
from sqlalchemy.sql import func
from datetime import datetime

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

def add_message(session_id: str, sender: str, encrypted_content: bytes, encryption_metadata: Dict[str, Any], content_hash: str, db: Session, user_id: str, message_data: Optional[dict] = None):
    """Add an encrypted message to a chat session with user verification."""
    # Verify the session belongs to the user
    session = db.query(ChatSession).filter(
        and_(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        )
    ).first()
    
    if not session:
        raise ValueError("Session not found or access denied")
    
    # Verify content hash for integrity
    # if not _verify_content_hash(encrypted_content, content_hash):
    #     raise ValueError("Content hash verification failed")
    
    message = ChatMessage(
        session_id=session_id,
        sender_type=sender,
        encrypted_content=encrypted_content,
        encryption_metadata=encryption_metadata,
        content_hash=content_hash,
        message_data=message_data
    )
    db.add(message)
    
    # Update session timestamp
    session.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(message)
    return message

def get_history(session_id: str, db: Session, user_id: str) -> List[dict]:
    """Get encrypted chat history for a session with user verification."""
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
    
    import base64
    return [
        {
            "id": str(msg.id),
            "session_id": str(msg.session_id),
            "sender_type": msg.sender_type,
            "encrypted_content": base64.b64encode(msg.encrypted_content).decode('utf-8'),
            "encryption_metadata": msg.encryption_metadata,
            "content_hash": msg.content_hash,
            "message_data": msg.message_data,
            "created_at": msg.created_at.isoformat() if msg.created_at else None
        } 
        for msg in messages
    ]

def get_user_sessions(user_id: str, db: Session, limit: int = 50, offset: int = 0) -> List[dict]:
    """Get all chat sessions for a user with pagination."""
    try:
        # Convert string user_id to UUID if needed
        import uuid as uuid_module
        try:
            user_uuid = uuid_module.UUID(user_id)
        except ValueError as exc:
            raise ValueError(f"Invalid UUID format: {user_id}") from exc
        
        # Use a subquery to count messages for each session
        from sqlalchemy import func as sql_func
        sessions_with_count = db.query(
            ChatSession,
            sql_func.count(ChatMessage.id).label('message_count')
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
        
    except Exception:
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
    session.updated_at = datetime.utcnow()
    db.commit()
    return True



def _verify_content_hash(encrypted_content: bytes, content_hash: str) -> bool:
    """Verify the SHA-256 hash of encrypted content."""
    if not encrypted_content or not content_hash:
        return False
    
    calculated_hash = hashlib.sha256(encrypted_content).hexdigest()
    
    # Debug logging
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Hash verification - Expected: {content_hash}")
    logger.info(f"Hash verification - Calculated: {calculated_hash}")
    logger.info(f"Hash verification - Match: {calculated_hash == content_hash}")
    logger.info(f"Hash verification - Content length: {len(encrypted_content)}")
    
    return calculated_hash == content_hash

def add_encrypted_session_data(
    session_id: str, 
    user_id: str, 
    encrypted_data: bytes, 
    encryption_metadata: Dict[str, Any],
    db: Session
) -> bool:
    """Add encrypted session data with user verification."""
    session = db.query(ChatSession).filter(
        and_(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        )
    ).first()
    
    if not session:
        return False
    
    session.encrypted_session_data = encrypted_data
    session.session_encryption_metadata = encryption_metadata
    session.updated_at = func.now()
    db.commit()
    return True

def get_encrypted_session_data(session_id: str, user_id: str, db: Session) -> Optional[Dict[str, Any]]:
    """Get encrypted session data with user verification."""
    session = db.query(ChatSession).filter(
        and_(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        )
    ).first()
    
    if not session:
        return None
    
    return {
        "encrypted_session_data": session.encrypted_session_data,
        "session_encryption_metadata": session.session_encryption_metadata
    }
