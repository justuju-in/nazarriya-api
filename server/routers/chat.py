from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from server.models import ChatMessageRequest, ChatResponse, User
from server import session_manager
from server.dependencies import get_current_user
from server.database import get_db
# from server.rag_pipeline import run_rag

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(
    msg: ChatMessageRequest, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Create session if not provided
    if not msg.session_id:
        session_id = session_manager.create_session(str(current_user.id), db)
    else:
        session_id = msg.session_id

    # Store user message
    session_manager.add_message(session_id, "user", msg.message, db)
    history = session_manager.get_history(session_id, db)

    # Get RAG response
    # answer, sources = run_rag(msg.message, history)
    answer = "This is a test response"
    sources = ["test.com"]
    
    # Store bot reply
    session_manager.add_message(session_id, "bot", answer, db)

    return ChatResponse(session_id=session_id, response=answer, sources=sources)
