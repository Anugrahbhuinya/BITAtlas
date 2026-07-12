import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form

from app.core.auth import get_current_admin
from app.security.rate_limit.rate_limiter import rate_limit_admin, rate_limit_search
from app.models.knowledge import (
    KnowledgeItemCreate,
    KnowledgeItemUpdate,
    KnowledgeItemResponse,
    KnowledgeListResponse,
    KnowledgeVersionResponse,
    KnowledgeStatsResponse,
    BulkActionRequest
)
from app.services.knowledge import knowledge_service, file_upload_service, version_service

logger = logging.getLogger("knowledge_routes")

router = APIRouter(
    prefix="/api/admin/knowledge",
    tags=["Knowledge Management"],
    dependencies=[Depends(get_current_admin), Depends(rate_limit_admin)]
)

@router.post("", response_model=KnowledgeItemResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge(
    payload: KnowledgeItemCreate,
    current_user: str = Depends(get_current_admin)
):
    try:
        doc = await knowledge_service.create_knowledge(payload.dict(), author=current_user)
        return doc
    except Exception as e:
        logger.error(f"Failed to create knowledge item: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create knowledge item: {str(e)}"
        )

@router.get("", response_model=KnowledgeListResponse)
async def list_knowledge(
    status: Optional[str] = None,
    category: Optional[str] = None,
    source_type: Optional[str] = None,
    priority: Optional[int] = None,
    department: Optional[str] = None,
    author: Optional[str] = None,
    tag: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    current_user: str = Depends(get_current_admin)
):
    filters = {
        "status": status,
        "category": category,
        "source_type": source_type,
        "priority": priority,
        "department": department,
        "author": author,
        "tag": tag
    }
    try:
        return await knowledge_service.list_knowledge(filters, page=page, page_size=page_size)
    except Exception as e:
        logger.error(f"Failed to list knowledge items: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve knowledge items list: {str(e)}"
        )

@router.get("/stats", response_model=KnowledgeStatsResponse)
async def get_stats(current_user: str = Depends(get_current_admin)):
    try:
        return await knowledge_service.get_statistics()
    except Exception as e:
        logger.error(f"Failed to aggregate statistics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )

@router.get("/search", response_model=List[KnowledgeItemResponse], dependencies=[Depends(rate_limit_search)])
async def search_knowledge(
    q: Optional[str] = "",
    status: Optional[str] = None,
    category: Optional[str] = None,
    source_type: Optional[str] = None,
    priority: Optional[int] = None,
    department: Optional[str] = None,
    author: Optional[str] = None,
    tag: Optional[str] = None,
    current_user: str = Depends(get_current_admin)
):
    filters = {
        "status": status,
        "category": category,
        "source_type": source_type,
        "priority": priority,
        "department": department,
        "author": author,
        "tags": tag
    }
    # Clean filters
    filters = {k: v for k, v in filters.items() if v is not None}
    try:
        return await knowledge_service.search_knowledge(q, filters)
    except Exception as e:
        logger.error(f"Failed search: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )

@router.get("/{id}", response_model=KnowledgeItemResponse)
async def get_knowledge(
    id: str,
    current_user: str = Depends(get_current_admin)
):
    doc = await knowledge_service.get_knowledge(id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge item with ID {id} not found."
        )
    return doc

@router.put("/{id}", response_model=KnowledgeItemResponse)
async def update_knowledge(
    id: str,
    payload: KnowledgeItemUpdate,
    current_user: str = Depends(get_current_admin)
):
    try:
        doc = await knowledge_service.update_knowledge(id, payload.dict(exclude_unset=True), author=current_user)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Knowledge item with ID {id} not found."
            )
        return doc
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update knowledge item {id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update knowledge item: {str(e)}"
        )

@router.delete("/{id}")
async def delete_knowledge(
    id: str,
    current_user: str = Depends(get_current_admin)
):
    success = await knowledge_service.delete_knowledge(id, author=current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge item with ID {id} not found."
        )
    return {"status": "success", "message": "Knowledge item and associated data deleted successfully."}

@router.post("/{id}/publish", response_model=KnowledgeItemResponse)
async def publish_knowledge(
    id: str,
    current_user: str = Depends(get_current_admin)
):
    try:
        doc = await knowledge_service.update_knowledge(id, {"status": "published"}, author=current_user)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Knowledge item with ID {id} not found."
            )
        return doc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{id}/archive", response_model=KnowledgeItemResponse)
async def archive_knowledge(
    id: str,
    current_user: str = Depends(get_current_admin)
):
    try:
        doc = await knowledge_service.update_knowledge(id, {"status": "archived"}, author=current_user)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Knowledge item with ID {id} not found."
            )
        return doc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{id}/restore", response_model=KnowledgeItemResponse)
async def restore_knowledge(
    id: str,
    current_user: str = Depends(get_current_admin)
):
    try:
        doc = await knowledge_service.update_knowledge(id, {"status": "draft"}, author=current_user)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Knowledge item with ID {id} not found."
            )
        return doc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{id}/versions", response_model=List[KnowledgeVersionResponse])
async def get_versions(
    id: str,
    current_user: str = Depends(get_current_admin)
):
    try:
        return await version_service.get_versions(id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{id}/versions/{version}/restore", response_model=KnowledgeItemResponse)
async def restore_version(
    id: str,
    version: int,
    current_user: str = Depends(get_current_admin)
):
    try:
        doc = await knowledge_service.restore_version(id, version, author=current_user)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Knowledge item with ID {id} not found or version {version} not found."
            )
        return doc
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    category: str = Form(...),
    department: str = Form(""),
    tags: str = Form(""),
    priority: int = Form(3),
    expires_at: Optional[str] = Form(None),
    overwrite: bool = Form(False),
    current_user: str = Depends(get_current_admin)
):
    try:
        # Parse tags
        parsed_tags = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
        file_content = await file.read()
        
        result = await file_upload_service.upload_knowledge_file(
            file_content=file_content,
            filename=file.filename,
            category=category,
            department=department,
            tags=parsed_tags,
            priority=priority,
            expires_at=expires_at,
            author=current_user,
            overwrite=overwrite
        )
        return result
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Failed file upload {file.filename}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File ingestion failed: {str(e)}"
        )

@router.post("/bulk/publish")
async def bulk_publish(payload: BulkActionRequest, current_user: str = Depends(get_current_admin)):
    count = await knowledge_service.bulk_publish(payload.ids, author=current_user)
    return {"status": "success", "published_count": count}

@router.post("/bulk/archive")
async def bulk_archive(payload: BulkActionRequest, current_user: str = Depends(get_current_admin)):
    count = await knowledge_service.bulk_archive(payload.ids, author=current_user)
    return {"status": "success", "archived_count": count}

@router.post("/bulk/delete")
async def bulk_delete(payload: BulkActionRequest, current_user: str = Depends(get_current_admin)):
    count = await knowledge_service.bulk_delete(payload.ids, author=current_user)
    return {"status": "success", "deleted_count": count}

@router.post("/bulk/reindex")
async def bulk_reindex(payload: BulkActionRequest, current_user: str = Depends(get_current_admin)):
    count = await knowledge_service.bulk_reindex(payload.ids, author=current_user)
    return {"status": "success", "reindexed_count": count}
