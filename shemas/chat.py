from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class ChatMessageIn(BaseModel):
    conversation_id: str
    text: str

class ChatMessageOut(BaseModel):
    id: int
    conversation_id: str
    sender: str
    text: str
    created_at: datetime
    meta: Optional[Dict[str, Any]] = None