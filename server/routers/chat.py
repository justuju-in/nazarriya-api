from fastapi import APIRouter
from server.models import ChatMessage, ChatResponse
from server import session_manager
# from server.rag_pipeline import run_rag

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(msg: ChatMessage):
    # Create session if not provided
    if not msg.session_id:
        session_id = session_manager.create_session(msg.user_id)
    else:
        session_id = msg.session_id

    # Store user message
    session_manager.add_message(session_id, "user", msg.message)
    history = session_manager.get_history(session_id)

    # Get RAG response
    # answer, sources = run_rag(msg.message, history)
    answer = "This is a test response"
    sources = ["test.com"]
    
    # Store bot reply
    session_manager.add_message(session_id, "bot", answer)

    return ChatResponse(session_id=session_id, response=answer, sources=sources)
