import logging
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.core.database import get_database

logger = logging.getLogger("version_service")

async def create_version(knowledge_id: str, doc_state: Dict[str, Any], author: str = "admin") -> str:
    """
    Creates a new snapshot entry in the `knowledge_versions` collection.
    """
    db = get_database()
    version_id = f"ver_{uuid.uuid4()}"
    
    version_entry = {
        "_id": version_id,
        "knowledge_id": knowledge_id,
        "version": doc_state.get("version", 1),
        "title": doc_state.get("title", ""),
        "content": doc_state.get("content", ""),
        "content_clean": doc_state.get("content_clean", ""),
        "content_markdown": doc_state.get("content_markdown", ""),
        "category": doc_state.get("category", "Other"),
        "department": doc_state.get("department", ""),
        "tags": doc_state.get("tags", []),
        "priority": doc_state.get("priority", 3),
        "author": author,
        "created_at": datetime.now(timezone.utc),
        "metadata": doc_state.get("metadata", {})
    }
    
    try:
        await db.knowledge_versions.insert_one(version_entry)
        logger.info(f"Saved version snapshot {version_entry['version']} for knowledge {knowledge_id}")
        return version_id
    except Exception as e:
        logger.error(f"Failed to create version entry for {knowledge_id}: {e}")
        raise e

async def get_versions(knowledge_id: str) -> List[Dict[str, Any]]:
    """
    Retrieves all version snapshots for a given knowledge item, sorted desc.
    """
    db = get_database()
    versions = []
    try:
        cursor = db.knowledge_versions.find({"knowledge_id": knowledge_id}).sort("version", -1)
        async for doc in cursor:
            versions.append(doc)
    except Exception as e:
        logger.error(f"Failed to fetch versions for {knowledge_id}: {e}")
    return versions

async def get_version_by_number(knowledge_id: str, version_number: int) -> Optional[Dict[str, Any]]:
    """
    Gets a specific version snapshot.
    """
    db = get_database()
    return await db.knowledge_versions.find_one({"knowledge_id": knowledge_id, "version": version_number})
