from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class KnowledgeStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    EXPIRED = "expired"

class KnowledgeSourceType(str, Enum):
    MANUAL = "manual"
    TXT = "txt"
    MARKDOWN = "markdown"
    DOCX = "docx"
    PDF = "pdf"
    WEBSITE = "website"
    JSON_STATIC = "json_static"

class KnowledgeCategory(str, Enum):
    ACADEMIC = "Academic"
    NOTICE = "Notice"
    EVENT = "Event"
    DEPARTMENT = "Department"
    HOSTEL = "Hostel"
    PLACEMENT = "Placement"
    CLUB = "Club"
    FACULTY = "Faculty"
    LIBRARY = "Library"
    TRANSPORT = "Transport"
    POLICY = "Policy"
    ADMISSION = "Admission"
    SCHOLARSHIP = "Scholarship"
    FAQ = "FAQ"
    RESEARCH = "Research"
    OTHER = "Other"

class KnowledgeItemBase(BaseModel):
    title: str = Field(..., min_length=1, description="Title of the knowledge item")
    content: str = Field(..., min_length=1, description="Content / text of the knowledge item")
    source_type: KnowledgeSourceType = Field(KnowledgeSourceType.MANUAL, description="Source format/type")
    category: KnowledgeCategory = Field(KnowledgeCategory.OTHER, description="Category classification")
    department: Optional[str] = Field("", description="Target department")
    tags: List[str] = Field(default_factory=list, description="Tags associated with the knowledge")
    author: Optional[str] = Field("admin", description="Author or editor")
    status: KnowledgeStatus = Field(KnowledgeStatus.DRAFT, description="Status (draft/published/archived/expired)")
    priority: int = Field(3, ge=1, le=5, description="Priority level (1-5)")
    language: str = Field("en", description="Language of content")
    expires_at: Optional[datetime] = Field(None, description="Expiry timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional custom metadata")

class KnowledgeItemCreate(KnowledgeItemBase):
    pass

class KnowledgeItemUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[KnowledgeCategory] = None
    department: Optional[str] = None
    tags: Optional[List[str]] = None
    author: Optional[str] = None
    status: Optional[KnowledgeStatus] = None
    priority: Optional[int] = None
    language: Optional[str] = None
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class KnowledgeItemResponse(KnowledgeItemBase):
    id: str = Field(..., alias="_id", description="Unique ID of the knowledge item")
    version: int = Field(1, description="Current version number")
    created_at: datetime
    updated_at: datetime
    chunks_count: int = Field(0, description="Number of vector chunks generated")
    vector_ids: List[str] = Field(default_factory=list, description="Associated ChromaDB vector IDs")
    original_filename: Optional[str] = None
    file_hash: Optional[str] = None

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class KnowledgeListResponse(BaseModel):
    items: List[KnowledgeItemResponse]
    total: int
    page: int
    page_size: int

class KnowledgeVersionResponse(BaseModel):
    id: str = Field(..., alias="_id")
    knowledge_id: str
    version: int
    title: str
    content: str
    category: str
    department: str
    tags: List[str]
    priority: int
    author: str
    created_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class KnowledgeStatsResponse(BaseModel):
    total_items: int
    published: int
    drafts: int
    archived: int
    expired: int
    pdfs_count: int
    websites_count: int
    txt_count: int
    markdown_count: int
    docx_count: int
    manual_count: int
    category_counts: Dict[str, int]
    vector_count: int
    embedding_count: int
    storage_used_bytes: int
    recent_updates: List[Dict[str, Any]]

class BulkActionRequest(BaseModel):
    ids: List[str]
