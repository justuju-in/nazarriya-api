import uuid
from collections import defaultdict

_sessions = defaultdict(list)

def create_session(user_id: str) -> str:
    session_id = str(uuid.uuid4())
    _sessions[session_id] = []
    return session_id

def add_message(session_id: str, sender: str, text: str):
    _sessions[session_id].append({"sender": sender, "text": text})

def get_history(session_id: str):
    return _sessions.get(session_id, [])
