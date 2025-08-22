from pydantic import BaseModel
from typing import Optional, List

class ChatMessage(BaseModel):
    user_id: str
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    response: str
    sources: Optional[List[str]] = None
