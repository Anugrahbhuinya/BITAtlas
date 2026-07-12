import asyncio
import hashlib
import logging
from datetime import datetime, timezone
import urllib.parse
from urllib.robotparser import RobotFileParser
import uuid
from typing import Optional, Set

from app.core import config
from app.core.database import get_database

logger = logging.getLogger("website_scheduler")

# Background task state variables
_scheduler_task: Optional[asyncio.Task] = None
_scheduler_running: bool = False
_active_syncs: Set[str] = set()
_sync_semaphore: Optional[asyncio.Semaphore] = None

def check_robots_txt(url: str, user_agent: str = "*") -> bool:
    """
    Checks if crawling the target URL is permitted by its robots.txt rules.
    Standard convention defaults to allowed on parser exceptions or missing files.
    """
    try:
        parsed = urllib.parse.urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        rp = RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(user_agent, url)
    except Exception as e:
        logger.debug(f"Could not parse robots.txt for {url} ({str(e)}). Assuming allowed.")
        return True

async def start_scheduler():
    """
    Starts the background website sync task.
    Called on FastAPI application startup.
    """
    global _scheduler_task, _scheduler_running, _sync_semaphore
    if not config.WEBSITE_SYNC_ENABLED:
        logger.info("Website synchronization scheduler is disabled by config settings.")
        return

    if _scheduler_running:
        logger.warning("Website synchronization scheduler task is already active.")
        return

    _scheduler_running = True
    _sync_semaphore = asyncio.Semaphore(config.MAX_CONCURRENT_WEBSITE_SYNCS)
    _scheduler_task = asyncio.create_task(scheduler_loop())
    logger.info("Website synchronization scheduler task started successfully.")

async def stop_scheduler():
    """
    Cancels and stops the background website sync task.
    Called on FastAPI application shutdown.
    """
    global _scheduler_running, _scheduler_task
    if not _scheduler_running:
        return

    _scheduler_running = False
    logger.info("Stopping website synchronization scheduler task...")
    if _scheduler_task:
        _scheduler_task.cancel()
        try:
            await _scheduler_task
        except asyncio.CancelledError:
            pass
        _scheduler_task = None
    logger.info("Website synchronization scheduler task stopped.")

async def scheduler_loop():
    """
    Periodic check loop executing website sync cycles.
    """
    # Wait a small delay after startup before initiating first check cycle
    await asyncio.sleep(10)
    
    while _scheduler_running:
        try:
            logger.info("Scheduler Triggered: Beginning scheduled website synchronization cycle...")
            from app.services.websites.website_service import sync_all_websites
            await sync_all_websites(username="system")
            
            # Check KMS expired items
            if getattr(config, "KNOWLEDGE_EXPIRY_CHECK_ENABLED", True):
                logger.info("Scheduler Triggered: Checking for expired KMS items...")
                from app.services.knowledge.expiry_service import check_expired_items
                await check_expired_items()
        except Exception as e:
            logger.error(f"Error occurred in scheduler loop execution: {str(e)}", exc_info=True)

        # Sleep interval in small chunks to support responsive shutdown
        sleep_interval = config.WEBSITE_SYNC_INTERVAL_MINUTES * 60
        sleep_step = 5
        steps = int(sleep_interval / sleep_step)
        for _ in range(max(1, steps)):
            if not _scheduler_running:
                break
            await asyncio.sleep(sleep_step)

async def log_crawl_history(
    website_id: str,
    url: str,
    started_at: datetime,
    completed_at: datetime,
    duration_ms: int,
    status: str,
    content_changed: bool,
    old_hash: str,
    new_hash: str,
    old_chunks: int,
    new_chunks: int,
    message: str,
    raw_hash_changed: bool = False,
    normalized_hash_changed: bool = False,
    reindex_triggered: bool = False,
    reason: str = ""
):
    """
    Logs sync crawl attempts inside the `website_crawl_history` collection.
    """
    db = get_database()
    history_entry = {
        "_id": str(uuid.uuid4()),
        "website_id": website_id,
        "url": url,
        "started_at": started_at,
        "completed_at": completed_at,
        "duration_ms": duration_ms,
        "status": status,
        "content_changed": content_changed,
        "old_hash": old_hash,
        "new_hash": new_hash,
        "old_chunks": old_chunks,
        "new_chunks": new_chunks,
        "message": message,
        "raw_hash_changed": raw_hash_changed,
        "normalized_hash_changed": normalized_hash_changed,
        "reindex_triggered": reindex_triggered,
        "reason": reason
    }
    try:
        await db.website_crawl_history.insert_one(history_entry)
        logger.debug(f"Logged crawl attempt details to history collection for: {url}")
    except Exception as e:
        logger.error(f"Failed to save crawl history entry: {str(e)}")

def is_scheduler_running() -> bool:
    return _scheduler_running

def get_active_syncs() -> Set[str]:
    return _active_syncs

def get_sync_semaphore() -> Optional[asyncio.Semaphore]:
    return _sync_semaphore
