from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from server.models import (
    ChatMessageRequest, ChatResponse, User, SessionResponse, 
    SessionHistoryResponse, SessionCreate, SessionUpdate
)
from server import session_manager
from server.dependencies import get_current_user
from server.database import get_db
from typing import List, Optional
# from server.rag_pipeline import run_rag

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(
    msg: ChatMessageRequest, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message and get a response from the RAG system."""
    try:
        # Create session if not provided
        if not msg.session_id:
            session_id = session_manager.create_session(str(current_user.id), db)
        else:
            # Verify the session belongs to the current user
            session = session_manager.get_session_by_id(msg.session_id, str(current_user.id), db)
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this session"
                )
            session_id = msg.session_id

        # Store user message
        session_manager.add_message(
            session_id, 
            "user", 
            msg.message, 
            db, 
            str(current_user.id)
        )
        
        # Get chat history for context
        history = session_manager.get_history(session_id, db, str(current_user.id))

        # Get RAG response (placeholder for now)
        # answer, sources = run_rag(msg.message, history)
        answer = "This is a test response from the enhanced chat system"
        sources = ["test.com"]
        
        # Store bot reply with metadata
        message_data = {"sources": sources}
        session_manager.add_message(
            session_id, 
            "bot", 
            answer, 
            db, 
            str(current_user.id),
            message_data
        )

        return ChatResponse(session_id=session_id, response=answer, sources=sources)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        )

@router.get("/sessions", response_model=List[SessionResponse])
def get_user_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """Get all chat sessions for the current user."""
    try:
        sessions = session_manager.get_user_sessions(str(current_user.id), db, limit, offset)
        return sessions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sessions"
        )

@router.get("/sessions/{session_id}/history", response_model=SessionHistoryResponse)
def get_session_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat history for a specific session."""
    try:
        history = session_manager.get_history(session_id, db, str(current_user.id))
        return SessionHistoryResponse(session_id=session_id, history=history)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve session history"
        )

@router.post("/sessions", response_model=dict)
def create_new_session(
    session_data: SessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new chat session for the current user."""
    try:
        session_id = session_manager.create_session(str(current_user.id), db, session_data.title)
        return {"session_id": session_id, "message": "New session created successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create new session"
        )

@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a chat session."""
    try:
        success = session_manager.delete_session(session_id, str(current_user.id), db)
        if success:
            return {"message": "Session deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or access denied"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete session"
        )

@router.put("/sessions/{session_id}/title")
def update_session_title(
    session_id: str,
    session_update: SessionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the title of a chat session."""
    try:
        success = session_manager.update_session_title(session_id, str(current_user.id), session_update.title, db)
        if success:
            return {"message": "Session title updated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or access denied"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update session title"
        )
