from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    message: str
    sessionId: Optional[str] = None

class MessageSchema(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class HistoryResponse(BaseModel):
    sessionId: str
    messages: List[MessageSchema]