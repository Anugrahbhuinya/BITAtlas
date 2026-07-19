import logging
from typing import List, Optional
from app.core.database import get_database
from app.services.websites.pipeline import run_pipeline
from app.services.rag.vector_store import get_vector_store
from app.services.admin_service import log_admin_activity

logger = logging.getLogger("website_service")

async def add_website(url: str, created_by: str = "admin") -> dict:
    """
    Validates, scrapes, chunks, embeds, and indexes a website page.
    """
    logger.info(f"Adding website {url} initiated by {created_by}")
    return await run_pipeline(url, created_by=created_by)

async def list_websites() -> List[dict]:
    """
    Lists all indexed websites from the database.
    """
    db = get_database()
    cursor = db.websites.find({})
    websites = []
    async for doc in cursor:
        doc["id"] = str(doc.get("_id"))
        websites.append(doc)
    return websites

async def get_website(website_id: str) -> Optional[dict]:
    """
    Retrieves details of a single indexed website document.
    """
    db = get_database()
    doc = await db.websites.find_one({"_id": website_id})
    if doc:
        doc["id"] = str(doc.get("_id"))
        return doc
    return None

async def delete_website(website_id: str, purge: bool = True, username: str = "admin") -> bool:
    """
    Deletes the website record.
    If purge=True, deletes everything (metadata, crawl history, Chroma vectors).
    If purge=False, deletes website metadata only, keeping the Chroma vectors.
    """
    db = get_database()
    vector_store = get_vector_store()

    from app.core import config
    if config.IS_DEV_MODE:
        logger.info(f"[DEV DEBUG] Delete Trace: Deletion strategy: {'Purge (everything)' if purge else 'Keep Content (metadata only)'}")

    # 1. Fetch website document
    doc = await db.websites.find_one({"_id": website_id})
    if not doc:
        logger.warning(f"Website ID {website_id} not found in database for deletion.")
        return False

    url = doc.get("url")
    title = doc.get("title", "unknown")
    vector_ids = doc.get("vector_ids", [])

    if purge:
        logger.info("Deleting website metadata...")
        logger.info("Deleting Chroma vectors...")
        logger.info("Deleting chunk metadata...")
        logger.info("Deleting embeddings...")
        logger.info("Deleting indexed documents...")
        
        # If vector_ids is empty or not tracked, try fallback using Chroma filter
        if not vector_ids:
            try:
                chroma_res = vector_store.get(where={"doc_id": website_id})
                vector_ids = chroma_res.get("ids", [])
            except Exception as e:
                logger.error(f"Failed to query ChromaDB for fallback deletion of website {website_id}: {e}")

        num_vectors_removed = 0
        if vector_ids:
            try:
                logger.info(f"Deleting {len(vector_ids)} vectors from ChromaDB for website: {title}")
                vector_store.delete(ids=vector_ids)
                num_vectors_removed = len(vector_ids)
            except Exception as e:
                logger.error(f"Failed to delete ChromaDB vectors for website {website_id}: {e}")

        if config.IS_DEV_MODE:
            logger.info(f"[DEV DEBUG] Delete Trace: Vectors removed: {num_vectors_removed}")

        # Delete MongoDB website crawl history
        try:
            await db.website_crawl_history.delete_many({"website_id": website_id})
            logger.info(f"Deleted MongoDB crawl history for website ID {website_id}.")
        except Exception as e:
            logger.error(f"Failed to delete MongoDB crawl history for website {website_id}: {e}")

        # Delete MongoDB website record
        try:
            await db.websites.delete_one({"_id": website_id})
            logger.info(f"Deleted MongoDB metadata for website ID {website_id}.")
        except Exception as e:
            logger.error(f"Failed to delete MongoDB metadata for website {website_id}: {e}")

        logger.info("Deletion completed.")
        logger.info(f"Number of vectors removed: {num_vectors_removed}")
    else:
        logger.info("Deleting website metadata only...")
        
        # Delete MongoDB website record
        try:
            await db.websites.delete_one({"_id": website_id})
            logger.info("Website removed from Admin Dashboard.")
            logger.info("Knowledge retained.")
            logger.info("Vector count unchanged.")
        except Exception as e:
            logger.error(f"Failed to delete MongoDB metadata for website {website_id}: {e}")

    # 4. Log Admin Activity
    await log_admin_activity(
        action="Website Purged" if purge else "Website Metadata Deleted",
        username=username,
        details={"url": url, "title": title, "website_id": website_id}
    )
    return True

async def reindex_website(website_id: str, username: str = "admin") -> dict:
    """
    Triggers reindexing for a website: pulls the page HTML, deletes previous Chroma chunks,
    runs the embeddings generation pipeline, and updates the MongoDB document.
    """
    db = get_database()
    doc = await db.websites.find_one({"_id": website_id})
    if not doc:
        raise ValueError(f"Website ID {website_id} not found.")

    url = doc.get("url")
    old_vector_ids = doc.get("vector_ids", [])

    # Delete old vectors from ChromaDB
    if old_vector_ids:
        try:
            vector_store = get_vector_store()
            logger.info(f"Cleaning up {len(old_vector_ids)} old vectors from ChromaDB before reindexing website {website_id}")
            vector_store.delete(ids=old_vector_ids)
        except Exception as e:
            logger.error(f"Failed to delete old ChromaDB vectors during website reindexing: {e}")

    # Re-run pipeline to index latest content
    return await run_pipeline(url, created_by=username, overwrite_id=website_id)

async def sync_website(website_id: str, username: str = "system") -> dict:
    """
    Synchronizes a single website page. Checks for content changes via SHA-256 hash.
    Deletes old Chroma chunks and re-indexes only if content changes are detected.
    """
    import hashlib
    import asyncio
    from datetime import datetime, timezone
    from app.core import config
    from app.services.websites.crawler import crawl_single_page
    from app.services.websites.extractor import extract_clean_text
    from app.services.websites.scheduler import check_robots_txt, log_crawl_history, get_active_syncs, get_sync_semaphore
    
    db = get_database()
    website = await db.websites.find_one({"_id": website_id})
    if not website:
        raise ValueError(f"Website ID {website_id} not found.")

    url = website["url"]
    old_hash = website.get("content_hash", "")
    old_norm_hash = website.get("normalized_content_hash")
    old_chunks = website.get("chunk_count", 0)
    title = website.get("title", url)
    
    active_syncs = get_active_syncs()
    sync_semaphore = get_sync_semaphore()
    
    if website_id in active_syncs:
        logger.warning(f"Sync already running for {url}. Skipping.")
        return {"status": "Skipped", "message": "Sync already in progress."}
        
    active_syncs.add(website_id)
    start_time = datetime.now(timezone.utc)
    
    # Fallback semaphore if run outside task loop
    sem = sync_semaphore or asyncio.Semaphore(1)
    
    try:
        async with sem:
            # 1. Robots.txt Compliance Check
            if config.RESPECT_ROBOTS_TXT:
                allowed = await asyncio.to_thread(check_robots_txt, url, config.USER_AGENT)
                if not allowed:
                    raise ValueError(f"Crawling disallowed by robots.txt rule for url: {url}")
                    
            # 2. Download and Extract Webpage Text
            html = await crawl_single_page(url)
            cleaned_text = extract_clean_text(html)
            
            if not cleaned_text or not cleaned_text.strip():
                raise ValueError("The webpage contains no extractable body text.")
                
            word_count = len(cleaned_text.split())
            
            # Enforce minimum 100-word limit
            if word_count < 100:
                raise ValueError(f"Webpage content length is insufficient ({word_count} words). Minimum 100 required.")
                
            new_hash = hashlib.sha256(cleaned_text.encode("utf-8")).hexdigest()
            
            from app.services.websites.content_normalizer import normalize_content
            norm_text, norm_stats = normalize_content(cleaned_text)
            new_norm_hash = hashlib.sha256(norm_text.encode("utf-8")).hexdigest()
            
            raw_hash_changed = (new_hash != old_hash)
            
            # 3. Check for Content Changes using Normalized Hash
            reindex_triggered = False
            reason = "No changes detected."
            
            if old_norm_hash is None:
                # Backward compatibility check
                if not raw_hash_changed:
                    reindex_triggered = False
                    reason = "No changes detected. Initialized normalized hash."
                else:
                    reindex_triggered = True
                    reason = "Content updated. Initialized normalized hash."
            else:
                normalized_hash_changed = (new_norm_hash != old_norm_hash)
                if not normalized_hash_changed:
                    reindex_triggered = False
                    if raw_hash_changed:
                        reason = "Only volatile content changed."
                    else:
                        reason = "No changes detected."
                else:
                    reindex_triggered = True
                    reason = "Website content updated."

            # Log rich statistics about normalization
            logger.info(
                f"Website Checked: {url}\n"
                f"  Original Text Length: {norm_stats['original_len']} chars\n"
                f"  Normalized Text Length: {norm_stats['normalized_len']} chars\n"
                f"  Removed Characters: {norm_stats['chars_removed']} chars\n"
                f"  Removed Dates/Copyrights: {norm_stats['dates_removed'] + norm_stats['copyrights_removed']}\n"
                f"  Removed Timestamps: {norm_stats['times_removed']}\n"
                f"  Removed Counters: {norm_stats['counters_removed']}\n"
                f"  Final Normalized Hash: {new_norm_hash}\n"
                f"  Decision - Raw Hash Changed: {raw_hash_changed}, Normalized Hash Changed: {new_norm_hash != old_norm_hash if old_norm_hash else True}, Re-index: {'YES' if reindex_triggered else 'NO'}, Reason: {reason}"
            )
            
            if not reindex_triggered:
                # Content has not changed or only volatile changed
                update_fields = {
                    "last_checked": datetime.now(timezone.utc),
                    "sync_status": "Healthy",
                    "last_error": None
                }
                # Backfill normalized content hash if it wasn't present
                if old_norm_hash is None:
                    update_fields["normalized_content_hash"] = new_norm_hash
                    
                await db.websites.update_one(
                    {"_id": website_id},
                    {
                        "$set": update_fields,
                        "$inc": {
                            "check_count": 1,
                            "successful_checks": 1
                        }
                    }
                )
                
                duration = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
                await log_crawl_history(
                    website_id=website_id,
                    url=url,
                    started_at=start_time,
                    completed_at=datetime.now(timezone.utc),
                    duration_ms=duration,
                    status="success",
                    content_changed=False,
                    old_hash=old_hash,
                    new_hash=new_hash,
                    old_chunks=old_chunks,
                    new_chunks=old_chunks,
                    message=reason,
                    raw_hash_changed=raw_hash_changed,
                    normalized_hash_changed=(new_norm_hash != old_norm_hash) if old_norm_hash else True,
                    reindex_triggered=False,
                    reason=reason
                )
                return {"status": "Unchanged", "message": reason}
            else:
                # Content has changed: Trigger incremental re-indexing
                logger.info(f"Meaningful content changes detected for {url}. Initiating incremental re-indexing.")
                
                res = await reindex_website(website_id, username=username)
                new_chunks = res.get("chunk_count", 0)
                
                await db.websites.update_one(
                    {"_id": website_id},
                    {
                        "$set": {
                            "content_hash": new_hash,
                            "normalized_content_hash": new_norm_hash,
                            "last_checked": datetime.now(timezone.utc),
                            "last_changed": datetime.now(timezone.utc),
                            "sync_status": "Healthy",
                            "last_error": None
                        },
                        "$inc": {
                            "check_count": 1,
                            "successful_checks": 1
                        }
                    }
                )
                
                duration = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
                await log_crawl_history(
                    website_id=website_id,
                    url=url,
                    started_at=start_time,
                    completed_at=datetime.now(timezone.utc),
                    duration_ms=duration,
                    status="success",
                    content_changed=True,
                    old_hash=old_hash,
                    new_hash=new_hash,
                    old_chunks=old_chunks,
                    new_chunks=new_chunks,
                    message="Website updated.",
                    raw_hash_changed=raw_hash_changed,
                    normalized_hash_changed=True,
                    reindex_triggered=True,
                    reason=reason
                )
                return {"status": "Updated", "message": "Website updated.", "chunks": new_chunks}
                
    except Exception as e:
        logger.error(f"Failed to synchronize website {url}: {e}", exc_info=True)
        # Record failure states inside MongoDB metadata
        await db.websites.update_one(
            {"_id": website_id},
            {
                "$set": {
                    "last_checked": datetime.now(timezone.utc),
                    "sync_status": "Failed",
                    "last_error": str(e)
                },
                "$inc": {
                    "check_count": 1,
                    "failed_checks": 1
                }
            }
        )
        
        duration = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        await log_crawl_history(
            website_id=website_id,
            url=url,
            started_at=start_time,
            completed_at=datetime.now(timezone.utc),
            duration_ms=duration,
            status="failed",
            content_changed=False,
            old_hash=old_hash,
            new_hash="",
            old_chunks=old_chunks,
            new_chunks=0,
            message=str(e),
            raw_hash_changed=False,
            normalized_hash_changed=False,
            reindex_triggered=False,
            reason=f"Failed: {str(e)}"
        )
        return {"status": "Failed", "message": str(e)}
    finally:
        active_syncs.remove(website_id)

async def sync_all_websites(username: str = "system") -> dict:
    """
    Synchronizes all websites concurrently within semaphore limits.
    """
    import asyncio
    import time
    start_time = time.time()
    db = get_database()
    
    cursor = db.websites.find({})
    websites = await cursor.to_list(length=1000)
    
    sync_tasks = []
    for site in websites:
        if site.get("sync_enabled", True):
            sync_tasks.append(sync_website(site["_id"], username=username))
            
    if not sync_tasks:
        return {
            "checked": 0,
            "updated": 0,
            "unchanged": 0,
            "failed": 0,
            "duration": "0s"
        }
        
    results = await asyncio.gather(*sync_tasks, return_exceptions=True)
    
    checked = len(results)
    updated = 0
    unchanged = 0
    failed = 0
    
    for res in results:
        if isinstance(res, Exception):
            failed += 1
        elif isinstance(res, dict):
            status = res.get("status")
            if status == "Updated":
                updated += 1
            elif status == "Unchanged":
                unchanged += 1
            else:
                failed += 1
                
    elapsed = time.time() - start_time
    duration_str = f"{int(elapsed)}s"
    
    return {
        "checked": checked,
        "updated": updated,
        "unchanged": unchanged,
        "failed": failed,
        "duration": duration_str
    }

async def toggle_auto_sync(website_id: str, enabled: bool, username: str = "admin") -> bool:
    """
    Enables or disables auto sync checks for a website.
    """
    db = get_database()
    res = await db.websites.update_one(
        {"_id": website_id},
        {"$set": {"sync_enabled": enabled}}
    )
    if res.matched_count == 0:
        return False
        
    status_str = "enabled" if enabled else "disabled"
    await log_admin_activity(
        action=f"Website Auto-Sync {status_str.capitalize()}",
        username=username,
        details={"website_id": website_id}
    )
    return True

async def get_sync_statistics() -> dict:
    """
    Retrieves aggregated dashboard synchronization statistics.
    """
    from datetime import datetime, timezone
    db = get_database()
    
    indexed_websites = await db.websites.count_documents({})
    healthy_websites = await db.websites.count_documents({"sync_status": "Healthy", "sync_enabled": True})
    pending_updates = await db.websites.count_documents({"sync_status": "Pending", "sync_enabled": True})
    failed_websites = await db.websites.count_documents({"sync_status": "Failed", "sync_enabled": True})
    
    # Calculate today's crawls & updates (from midnight UTC)
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_crawls = await db.website_crawl_history.count_documents({"started_at": {"$gte": today_start}})
    today_updates = await db.website_crawl_history.count_documents({
        "started_at": {"$gte": today_start},
        "status": "success",
        "content_changed": True
    })
    
    # Calculate average crawl duration (ms)
    pipeline_time = [{"$group": {"_id": None, "avg_time": {"$avg": "$duration_ms"}}}]
    cursor_time = db.website_crawl_history.aggregate(pipeline_time)
    avg_crawl_time = 0
    async for doc in cursor_time:
        avg_crawl_time = int(doc.get("avg_time", 0) or 0)
        
    # Calculate average chunks count
    pipeline_chunks = [{"$group": {"_id": None, "avg_chunks": {"$avg": "$chunk_count"}}}]
    cursor_chunks = db.websites.aggregate(pipeline_chunks)
    avg_chunks = 0
    async for doc in cursor_chunks:
        avg_chunks = int(doc.get("avg_chunks", 0) or 0)
        
    return {
        "indexed_websites": indexed_websites,
        "healthy_websites": healthy_websites,
        "pending_updates": pending_updates,
        "failed_websites": failed_websites,
        "today_crawls": today_crawls,
        "today_updates": today_updates,
        "avg_crawl_time_ms": avg_crawl_time,
        "avg_chunk_count": avg_chunks
    }
