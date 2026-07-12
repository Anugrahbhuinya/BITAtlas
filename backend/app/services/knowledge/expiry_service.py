import logging
from datetime import datetime, timezone
from app.core.database import get_database
from app.services.rag.vector_store import get_vector_store
from app.services.ai.cache import clear_response_cache

logger = logging.getLogger("expiry_service")

async def check_expired_items():
    """
    Checks for published knowledge items that have expired, sets their status to 'expired',
    and removes their vectors from ChromaDB.
    """
    db = get_database()
    vector_store = get_vector_store()
    now = datetime.now(timezone.utc)
    
    try:
        # Find all published items where expires_at is in the past
        query = {
            "status": "published",
            "expires_at": {"$ne": None, "$lt": now}
        }
        
        expired_cursor = db.knowledge_items.find(query)
        expired_items = await expired_cursor.to_list(length=1000)
        
        if not expired_items:
            return
            
        logger.info(f"Found {len(expired_items)} expired knowledge items. Initiating cleanup.")
        
        for item in expired_items:
            item_id = item["_id"]
            title = item.get("title", "unknown")
            vector_ids = item.get("vector_ids", [])
            
            # 1. Remove vectors from ChromaDB
            if vector_ids:
                try:
                    vector_store.delete(ids=vector_ids)
                    logger.info(f"Removed {len(vector_ids)} expired vectors from ChromaDB for item: '{title}'")
                except Exception as ve:
                    logger.error(f"Failed to delete ChromaDB vectors for expired item {item_id}: {ve}")
            
            # 2. Update status in MongoDB
            await db.knowledge_items.update_one(
                {"_id": item_id},
                {
                    "$set": {
                        "status": "expired",
                        "updated_at": now
                    }
                }
            )
            logger.info(f"Marked knowledge item '{title}' ({item_id}) as expired in MongoDB.")
            
        clear_response_cache()
        
    except Exception as e:
        logger.error(f"Error checking expired knowledge items: {e}", exc_info=True)
