from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    message: str
    sessionId: Optional[str] = None
    currentLocationNodeId: Optional[str] = None
    currentDestinationNodeId: Optional[str] = None
    accessibilityMode: Optional[bool] = None

class MessageSchema(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    messageType: Optional[str] = "text"
    metadata: Optional[dict] = None

class HistoryResponse(BaseModel):
    sessionId: str
    messages: List[MessageSchema]