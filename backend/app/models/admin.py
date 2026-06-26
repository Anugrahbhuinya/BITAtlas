from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class AdminLoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str

class SystemStatusComponent(BaseModel):
    name: str
    status: str  # "Connected", "Disconnected", "Error"
    details: Optional[str] = None

class SystemStatusResponse(BaseModel):
    components: List[SystemStatusComponent]

class AdminActivityLog(BaseModel):
    id: str = Field(alias="_id")
    action: str
    username: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ActivityLogResponse(BaseModel):
    logs: List[AdminActivityLog]
    total: int

class AdminDocument(BaseModel):
    id: str
    filename: str
    type: str  # "pdf", "json", "txt", etc.
    status: str  # "Indexed", "Pending", "Failed"
    created: datetime
    size_bytes: int

class DocumentListResponse(BaseModel):
    documents: List[AdminDocument]
    total: int

class DashboardStatsResponse(BaseModel):
    knowledgeSources: int
    documents: int
    activeSessions: int
    systemHealth: str  # "Excellent" | "Good" | "Critical"
    averageResponseTime: float  # in seconds
    todayActivity: int

class AdminSettingsResponse(BaseModel):
    embeddingModel: str
    geminiModel: str
    mongoUri: str
    mongoDb: str
    chromaCollection: str
    chunkSize: int
    chunkOverlap: int
    systemVersion: str
