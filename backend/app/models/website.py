from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class AddWebsiteRequest(BaseModel):
    url: str = Field(..., description="The absolute HTTP/HTTPS URL of the website to index")

class WebsiteResponse(BaseModel):
    id: str = Field(..., validation_alias="_id", description="Unique ID of the indexed website")
    url: str = Field(..., description="Normalized URL of the website")
    domain: str = Field(..., description="Domain name of the website")
    title: str = Field(..., description="Extracted HTML title")
    description: Optional[str] = Field("", description="Extracted meta description")
    canonical_url: Optional[str] = Field("", description="Extracted canonical URL")
    language: Optional[str] = Field("en", description="Detected language of the webpage")
    word_count: int = Field(..., description="Total word count of the cleaned text")
    chunk_count: int = Field(..., description="Number of vector chunks generated")
    content_hash: str = Field(..., description="SHA-256 hash of the cleaned text")
    indexed_at: datetime = Field(..., description="Timestamp when the website was first indexed")
    last_crawled: datetime = Field(..., description="Timestamp of the last crawling request")
    status: str = Field(..., description="Current status of the indexed website")
    created_by: str = Field(..., description="Admin username who indexed this website")
    # Extended Sync Fields
    last_checked: Optional[datetime] = Field(None, description="Timestamp of the last sync check")
    last_changed: Optional[datetime] = Field(None, description="Timestamp of the last content change check")
    sync_status: Optional[str] = Field("Healthy", description="Sync health state (Healthy, Pending, Failed)")
    sync_enabled: Optional[bool] = Field(True, description="Whether auto-sync checks are active")
    last_error: Optional[str] = Field(None, description="Sync error log description")
    check_count: Optional[int] = Field(0, description="Total sync checks performed")
    successful_checks: Optional[int] = Field(0, description="Total successful check cycles")
    failed_checks: Optional[int] = Field(0, description="Total failed check cycles")
    normalized_content_hash: Optional[str] = Field(None, description="SHA-256 hash of the normalized content")

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class WebsiteListResponse(BaseModel):
    websites: List[WebsiteResponse]
    total: int

class IndexSummaryResponse(BaseModel):
    status: str = Field(..., description="Operation status (Completed, Duplicate, Failed)")
    message: str = Field(..., description="User friendly description of the operation outcome")
    website_id: Optional[str] = Field(None, description="The ID of the website document")
    url: Optional[str] = Field(None, description="The URL that was indexed")
    title: Optional[str] = Field(None, description="The title of the website")
    domain: Optional[str] = Field(None, description="The domain of the website")
    word_count: Optional[int] = Field(None, description="The word count of the webpage content")
    chunk_count: Optional[int] = Field(None, description="The number of generated chunks")
    indexed_at: Optional[datetime] = Field(None, description="The timestamp when indexing finished")
