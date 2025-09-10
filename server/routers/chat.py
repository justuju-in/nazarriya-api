from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from server.models import (
    ChatMessageRequest, ChatResponse, User, SessionResponse, 
    SessionHistoryResponse, SessionCreate, SessionUpdate
)
from server import session_manager
from server.dependencies import get_current_user
from server.database import get_db
from server.utils.logging import logger, log_error
from server.utils.encryption import encrypt_message, decrypt_message
from typing import List, Optional
import hashlib
# from server.rag_pipeline import run_rag

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(
    msg: ChatMessageRequest, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message and get a response from the RAG system."""
    logger.info(f"Chat message from user {current_user.id}: [ENCRYPTED_MESSAGE]")
    logger.info(f"Session ID: {msg.session_id or 'new'}")
    
    try:
        # Create session if not provided
        if not msg.session_id:
            # Use client-provided title or generate a default one
            session_title = msg.title or "New Chat Session"
            session_id = session_manager.create_session(str(current_user.id), db, session_title)
            logger.info(f"Created new session: {session_id} with title: {session_title}")
        else:
            # Verify the session belongs to the current user
            session = session_manager.get_session_by_id(msg.session_id, str(current_user.id), db)
            if not session:
                logger.warning(f"Access denied to session {msg.session_id} for user {current_user.id}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this session"
                )
            session_id = msg.session_id
            logger.info(f"Using existing session: {session_id}")

        # Decode base64-encoded encrypted message
        import base64
        encrypted_message_bytes = base64.b64decode(msg.encrypted_message)
        
        # Store encrypted user message
        session_manager.add_message(
            session_id, 
            "user", 
            encrypted_message_bytes, 
            msg.encryption_metadata,
            msg.content_hash,
            db, 
            str(current_user.id)
        )
        logger.info(f"Stored user message in session {session_id}")
        
        # Get encrypted chat history for context
        history = session_manager.get_history(session_id, db, str(current_user.id))
        logger.info(f"Retrieved {len(history)} encrypted messages from history")

        # Prepare encrypted history for LLM service
        encrypted_history = []
        for hist_msg in history:
            if hist_msg.get("encrypted_content") and hist_msg.get("encryption_metadata"):
                encrypted_history.append({
                    "role": hist_msg["sender_type"],
                    "encrypted_content": hist_msg["encrypted_content"],  # Already base64-encoded
                    "encryption_metadata": hist_msg["encryption_metadata"],
                    "content_hash": hist_msg["content_hash"]
                })

        # Get RAG response from LLM service using plaintext data
        try:
            import requests
            import json
            
            # Decrypt the user message for RAG processing
            decrypted_message = decrypt_message(encrypted_message_bytes, msg.encryption_metadata)
            
            # Prepare plaintext history for RAG service
            plaintext_history = []
            for hist_msg in history:
                if hist_msg.get("encrypted_content") and hist_msg.get("encryption_metadata"):
                    # Decrypt history message
                    hist_encrypted_bytes = base64.b64decode(hist_msg["encrypted_content"])
                    hist_decrypted = decrypt_message(hist_encrypted_bytes, hist_msg["encryption_metadata"])
                    plaintext_history.append({
                        "role": hist_msg["sender_type"],
                        "content": hist_decrypted
                    })
            
            # Call LLM service with plaintext data
            from ..config import settings
            response = requests.post(
                f"{settings.LLM_SERVICE_URL}/rag/query-plaintext",
                json={
                    "query": decrypted_message,
                    "history": plaintext_history,
                    "max_tokens": 1000
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                rag_response = response.json()
                plaintext_answer = rag_response["answer"]
                sources = [source["metadata"]["source"] for source in rag_response["sources"]]
                
                # Actually encrypt the response using AES-GCM
                encrypted_answer, answer_metadata = encrypt_message(plaintext_answer, msg.encryption_metadata)
                encrypted_answer_b64 = base64.b64encode(encrypted_answer).decode('utf-8')
                answer_hash = hashlib.sha256(plaintext_answer.encode('utf-8')).hexdigest()
            else:
                logger.warning(f"LLM service error: {response.status_code}")
                # Fallback to placeholder response
                placeholder_text = "I'm having trouble accessing my knowledge base right now. Please try again later."
                encrypted_answer, answer_metadata = encrypt_message(placeholder_text, msg.encryption_metadata)
                encrypted_answer_b64 = base64.b64encode(encrypted_answer).decode('utf-8')
                sources = []
                answer_hash = hashlib.sha256(placeholder_text.encode('utf-8')).hexdigest()
                
        except Exception as e:
            logger.error(f"Error calling LLM service: {str(e)}")
            # Fallback to placeholder response
            placeholder_text = "I'm experiencing technical difficulties. Please try again later."
            encrypted_answer, answer_metadata = encrypt_message(placeholder_text, msg.encryption_metadata)
            encrypted_answer_b64 = base64.b64encode(encrypted_answer).decode('utf-8')
            sources = []
            answer_hash = hashlib.sha256(placeholder_text.encode('utf-8')).hexdigest()
        
        # Store encrypted bot reply with metadata (decode base64 for storage)
        encrypted_answer_bytes = base64.b64decode(encrypted_answer_b64)
        message_data = {"sources": sources}
        session_manager.add_message(
            session_id, 
            "bot", 
            encrypted_answer_bytes,
            answer_metadata,
            answer_hash,
            db, 
            str(current_user.id),
            message_data
        )
        logger.info(f"Stored bot response in session {session_id}")

        logger.info(f"Chat request completed successfully for session {session_id}")
        return ChatResponse(
            session_id=session_id, 
            encrypted_response=encrypted_answer_b64,  # Return base64-encoded
            encryption_metadata=answer_metadata,
            content_hash=answer_hash,
            sources=sources
        )
    
    except ValueError as e:
        logger.warning(f"Validation error in chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, "chat_endpoint", user_id=str(current_user.id), message="[ENCRYPTED_MESSAGE]", session_id=msg.session_id)
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
