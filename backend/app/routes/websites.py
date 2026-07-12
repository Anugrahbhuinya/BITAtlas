import logging
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.auth import get_current_admin
from app.security.rate_limit.rate_limiter import rate_limit_admin, rate_limit_website_indexing
from app.services.websites import website_service
from app.models.website import AddWebsiteRequest, WebsiteResponse, WebsiteListResponse, IndexSummaryResponse
from app.services.websites.validator import validate_url
from app.core.database import get_database
from app.core import config
from app.models.website_sync import (
    ToggleSyncRequest, BulkSyncResponse, CrawlHistoryListResponse,
    WebsiteSyncStatsResponse, SystemSyncStatusResponse, WebsiteStatusItem, CrawlHistoryResponse
)

logger = logging.getLogger("website_routes")

router = APIRouter(
    prefix="/api/admin/websites",
    tags=["Websites Ingestion"],
    dependencies=[Depends(rate_limit_admin)]
)

@router.post("", response_model=IndexSummaryResponse, dependencies=[Depends(rate_limit_website_indexing)])
async def add_website(
    request: AddWebsiteRequest,
    current_user: str = Depends(get_current_admin)
):
    """
    Ingests and embeds a website page.
    """
    if not validate_url(request.url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid URL format. Only HTTP and HTTPS protocols are supported."
        )
    try:
        result = await website_service.add_website(request.url, created_by=current_user)
        return result
    except Exception as e:
        logger.error(f"Failed to add website {request.url}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to index website: {str(e)}"
        )

@router.get("", response_model=WebsiteListResponse)
async def list_websites(
    current_user: str = Depends(get_current_admin)
):
    """
    Lists all indexed websites.
    """
    try:
        websites = await website_service.list_websites()
        return WebsiteListResponse(websites=websites, total=len(websites))
    except Exception as e:
        logger.error(f"Failed to list websites: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve websites list: {str(e)}"
        )

@router.get("/stats", response_model=WebsiteSyncStatsResponse)
async def get_sync_stats(
    current_user: str = Depends(get_current_admin)
):
    try:
        return await website_service.get_sync_statistics()
    except Exception as e:
        logger.error(f"Failed to fetch sync statistics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve sync statistics: {str(e)}"
        )

@router.get("/status", response_model=SystemSyncStatusResponse)
async def get_system_sync_status(
    current_user: str = Depends(get_current_admin)
):
    from app.services.websites.scheduler import is_scheduler_running, get_active_syncs
    try:
        websites = await website_service.list_websites()
        websites_status = []
        for w in websites:
            websites_status.append(WebsiteStatusItem(
                id=w.get("id"),
                url=w.get("url"),
                title=w.get("title"),
                domain=w.get("domain", ""),
                word_count=w.get("word_count", 0),
                chunk_count=w.get("chunk_count", 0),
                indexed_at=w.get("indexed_at"),
                sync_status=w.get("sync_status", "Healthy"),
                sync_enabled=w.get("sync_enabled", True),
                last_checked=w.get("last_checked"),
                last_changed=w.get("last_changed"),
                last_error=w.get("last_error"),
                check_count=w.get("check_count", 0),
                successful_checks=w.get("successful_checks", 0),
                failed_checks=w.get("failed_checks", 0),
                normalized_content_hash=w.get("normalized_content_hash")
            ))
        
        return SystemSyncStatusResponse(
            scheduler_running=is_scheduler_running(),
            interval_minutes=config.WEBSITE_SYNC_INTERVAL_MINUTES,
            active_syncs_count=len(get_active_syncs()),
            websites_status=websites_status
        )
    except Exception as e:
        logger.error(f"Failed to fetch system sync status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve sync status: {str(e)}"
        )

@router.get("/history", response_model=CrawlHistoryListResponse)
async def get_crawl_history(
    current_user: str = Depends(get_current_admin)
):
    try:
        db = get_database()
        cursor = db.website_crawl_history.find({}).sort("started_at", -1)
        history = []
        async for doc in cursor:
            doc["_id"] = str(doc.get("_id"))
            history.append(CrawlHistoryResponse(**doc))
        return CrawlHistoryListResponse(history=history, total=len(history))
    except Exception as e:
        logger.error(f"Failed to get crawl history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve crawl history list: {str(e)}"
        )

@router.get("/history/{website_id}", response_model=CrawlHistoryListResponse)
async def get_website_crawl_history(
    website_id: str,
    current_user: str = Depends(get_current_admin)
):
    try:
        db = get_database()
        cursor = db.website_crawl_history.find({"website_id": website_id}).sort("started_at", -1)
        history = []
        async for doc in cursor:
            doc["_id"] = str(doc.get("_id"))
            history.append(CrawlHistoryResponse(**doc))
        return CrawlHistoryListResponse(history=history, total=len(history))
    except Exception as e:
        logger.error(f"Failed to get website crawl history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve website crawl history list: {str(e)}"
        )

@router.post("/sync-all", response_model=BulkSyncResponse, dependencies=[Depends(rate_limit_website_indexing)])
async def trigger_bulk_sync(
    current_user: str = Depends(get_current_admin)
):
    try:
        result = await website_service.sync_all_websites(username=current_user)
        return result
    except Exception as e:
        logger.error(f"Failed to execute bulk synchronization: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run bulk synchronization: {str(e)}"
        )

@router.post("/{id}/sync", dependencies=[Depends(rate_limit_website_indexing)])
async def trigger_manual_sync(
    id: str,
    current_user: str = Depends(get_current_admin)
):
    try:
        result = await website_service.sync_website(id, username=current_user)
        if result.get("status") == "Unchanged":
            from fastapi.responses import PlainTextResponse
            return PlainTextResponse("No changes detected.", status_code=200)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Manual sync check failed for website {id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Synchronization failed: {str(e)}"
        )

@router.post("/{id}/toggle-sync")
async def toggle_website_auto_sync(
    id: str,
    request: ToggleSyncRequest,
    current_user: str = Depends(get_current_admin)
):
    try:
        success = await website_service.toggle_auto_sync(id, request.sync_enabled, username=current_user)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Website ID {id} not found."
            )
        return {"status": "success", "sync_enabled": request.sync_enabled}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to toggle auto sync for website {id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle auto-sync: {str(e)}"
        )

@router.get("/{id}", response_model=WebsiteResponse)
async def get_website_details(
    id: str,
    current_user: str = Depends(get_current_admin)
):
    """
    Retrieves detailed metadata for a specific website index.
    """
    try:
        website = await website_service.get_website(id)
        if not website:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Website ID {id} not found."
            )
        return website
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get website details for {id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve website details: {str(e)}"
        )

@router.delete("/{id}")
async def delete_website(
    id: str,
    current_user: str = Depends(get_current_admin)
):
    """
    Deletes the website record and associated Chroma vectors.
    """
    try:
        success = await website_service.delete_website(id, username=current_user)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Website ID {id} not found."
            )
        return {"status": "success", "message": "Website and associated vector chunks deleted successfully."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete website {id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete website content: {str(e)}"
        )

@router.post("/{id}/reindex", response_model=IndexSummaryResponse, dependencies=[Depends(rate_limit_website_indexing)])
async def reindex_website(
    id: str,
    current_user: str = Depends(get_current_admin)
):
    """
    Pulls the latest HTML page contents, clears old vectors, and builds a fresh index.
    """
    try:
        result = await website_service.reindex_website(id, username=current_user)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to reindex website {id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to re-index website: {str(e)}"
        )
