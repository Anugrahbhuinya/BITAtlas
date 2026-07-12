import logging
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from langchain_core.documents import Document
from app.core.database import get_database
from app.services.rag.vector_store import get_vector_store
from app.services.rag.chunking_service import create_chunks
from app.services.ai.cache import clear_response_cache
from app.services.admin_service import log_admin_activity
from app.services.knowledge import version_service

logger = logging.getLogger("knowledge_service")

# Helper to index published item in ChromaDB
def _index_item_in_chroma(item_id: str, title: str, content: str, source_type: str, category: str, department: str, tags: List[str], priority: int, language: str, author: str) -> List[str]:
    vector_store = get_vector_store()
    chunks = create_chunks(content)
    if not chunks:
        return []
        
    vector_ids = []
    chroma_docs = []
    
    for i, chunk in enumerate(chunks):
        chunk_id = f"kn_{item_id}_chunk_{i}"
        vector_ids.append(chunk_id)
        
        doc = Document(
            page_content=chunk,
            metadata={
                "document_id": item_id,
                "filename": title,
                "page": f"Chunk {i + 1}",
                "source": "kb_document",
                "source_type": source_type,
                "chunk_number": i,
                "name": title,
                "title": title,
                "doc_id": item_id,
                "type": source_type,
                "category": category,
                "department": department,
                "tags": tags,
                "priority": priority,
                "status": "published",
                "language": language,
                "author": author,
                "indexed_at": datetime.now(timezone.utc).isoformat()
            }
        )
        chroma_docs.append(doc)
        
    vector_store.add_documents(chroma_docs, ids=vector_ids)
    logger.info(f"Indexed {len(chroma_docs)} chunks into ChromaDB for knowledge '{title}' ({item_id})")
    return vector_ids

# Helper to remove vectors from ChromaDB
def _remove_item_from_chroma(vector_ids: List[str], item_id: str):
    if not vector_ids:
        # Fallback query if vector_ids not saved
        try:
            vector_store = get_vector_store()
            chroma_res = vector_store.get(where={"doc_id": item_id})
            vector_ids = chroma_res.get("ids", [])
        except Exception as e:
            logger.error(f"Failed to query ChromaDB for fallback deletion of item {item_id}: {e}")
            
    if vector_ids:
        try:
            vector_store = get_vector_store()
            vector_store.delete(ids=vector_ids)
            logger.info(f"Deleted {len(vector_ids)} vectors from ChromaDB for item {item_id}")
        except Exception as e:
            logger.error(f"Failed to delete ChromaDB vectors for item {item_id}: {e}")

async def create_knowledge(data: Dict[str, Any], author: str = "admin") -> Dict[str, Any]:
    db = get_database()
    item_id = f"kn_{uuid.uuid4()}"
    now = datetime.now(timezone.utc)
    
    expires_at = data.get("expires_at")
    if isinstance(expires_at, str) and expires_at:
        expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        
    doc = {
        "_id": item_id,
        "title": data["title"],
        "content": data["content"],
        "content_clean": data["content"], # For simplicity/manual entry
        "content_markdown": data.get("content_markdown", ""),
        "source_type": data.get("source_type", "manual"),
        "category": data.get("category", "Other"),
        "department": data.get("department", ""),
        "tags": data.get("tags", []),
        "author": author,
        "status": data.get("status", "draft"),
        "priority": data.get("priority", 3),
        "version": 1,
        "language": data.get("language", "en"),
        "created_at": now,
        "updated_at": now,
        "expires_at": expires_at,
        "chunks_count": 0,
        "vector_ids": [],
        "original_filename": data.get("original_filename"),
        "file_hash": data.get("file_hash"),
        "metadata": data.get("metadata", {})
    }
    
    # Generate vectors if status is published
    if doc["status"] == "published":
        vector_ids = _index_item_in_chroma(
            item_id=item_id,
            title=doc["title"],
            content=doc["content"],
            source_type=doc["source_type"],
            category=doc["category"],
            department=doc["department"],
            tags=doc["tags"],
            priority=doc["priority"],
            language=doc["language"],
            author=author
        )
        doc["vector_ids"] = vector_ids
        doc["chunks_count"] = len(vector_ids)
        clear_response_cache()
        
    # Save to MongoDB
    await db.knowledge_items.insert_one(doc)
    
    # Save initial version snapshot
    await version_service.create_version(item_id, doc, author=author)
    
    await log_admin_activity(
        action="Knowledge Created",
        username=author,
        details={"title": doc["title"], "status": doc["status"], "id": item_id}
    )
    
    return doc

async def update_knowledge(item_id: str, data: Dict[str, Any], author: str = "admin") -> Optional[Dict[str, Any]]:
    db = get_database()
    existing = await db.knowledge_items.find_one({"_id": item_id})
    if not existing:
        return None
        
    # 1. Save version snapshot of current state
    await version_service.create_version(item_id, existing, author=author)
    
    now = datetime.now(timezone.utc)
    new_version = existing.get("version", 1) + 1
    
    # Prepare update fields
    updates = {}
    for field in ["title", "content", "content_markdown", "category", "department", "tags", "priority", "language", "metadata", "status"]:
        if field in data and data[field] is not None:
            updates[field] = data[field]
            
    expires_at = data.get("expires_at")
    if expires_at is not None:
        if isinstance(expires_at, str) and expires_at:
            expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        updates["expires_at"] = expires_at
        
    # Merge existing and update values to know final state
    updated_state = {**existing, **updates}
    updated_state["version"] = new_version
    
    # Manage vectors
    prev_status = existing.get("status")
    new_status = updated_state.get("status")
    prev_vector_ids = existing.get("vector_ids", [])
    
    if prev_status == "published":
        # Always remove old vectors to avoid duplication/orphans
        _remove_item_from_chroma(prev_vector_ids, item_id)
        updates["vector_ids"] = []
        updates["chunks_count"] = 0
        
    if new_status == "published":
        # Index updated content
        vector_ids = _index_item_in_chroma(
            item_id=item_id,
            title=updated_state["title"],
            content=updated_state["content"],
            source_type=updated_state["source_type"],
            category=updated_state["category"],
            department=updated_state["department"],
            tags=updated_state["tags"],
            priority=updated_state["priority"],
            language=updated_state["language"],
            author=author
        )
        updates["vector_ids"] = vector_ids
        updates["chunks_count"] = len(vector_ids)
        clear_response_cache()
        
    updates["version"] = new_version
    updates["updated_at"] = now
    
    await db.knowledge_items.update_one({"_id": item_id}, {"$set": updates})
    
    # Retrieve updated doc
    updated_doc = await db.knowledge_items.find_one({"_id": item_id})
    
    await log_admin_activity(
        action="Knowledge Updated",
        username=author,
        details={"title": updated_state["title"], "status": new_status, "id": item_id, "version": new_version}
    )
    
    return updated_doc

async def delete_knowledge(item_id: str, author: str = "admin") -> bool:
    db = get_database()
    existing = await db.knowledge_items.find_one({"_id": item_id})
    if not existing:
        return False
        
    # 1. Clean ChromaDB vectors
    _remove_item_from_chroma(existing.get("vector_ids", []), item_id)
    
    # 2. Delete MongoDB document
    await db.knowledge_items.delete_one({"_id": item_id})
    
    # 3. Delete versions
    await db.knowledge_versions.delete_many({"knowledge_id": item_id})
    
    clear_response_cache()
    
    await log_admin_activity(
        action="Knowledge Deleted",
        username=author,
        details={"title": existing.get("title"), "id": item_id}
    )
    return True

async def get_knowledge(item_id: str) -> Optional[Dict[str, Any]]:
    db = get_database()
    return await db.knowledge_items.find_one({"_id": item_id})

async def list_knowledge(filters: Dict[str, Any], page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    db = get_database()
    skip = (page - 1) * page_size
    
    # Build query from filters
    query = {}
    if filters.get("status"):
        query["status"] = filters["status"]
    if filters.get("category"):
        query["category"] = filters["category"]
    if filters.get("source_type"):
        query["source_type"] = filters["source_type"]
    if filters.get("priority"):
        query["priority"] = int(filters["priority"])
    if filters.get("department"):
        query["department"] = filters["department"]
    if filters.get("author"):
        query["author"] = filters["author"]
    if filters.get("tag"):
        query["tags"] = filters["tag"]
        
    cursor = db.knowledge_items.find(query).sort("updated_at", -1).skip(skip).limit(page_size)
    items = await cursor.to_list(length=page_size)
    total = await db.knowledge_items.count_documents(query)
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }

async def search_knowledge(search_query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    db = get_database()
    query = {}
    
    # Add text search or regex match
    if search_query:
        query["$or"] = [
            {"title": {"$regex": search_query, "$options": "i"}},
            {"content": {"$regex": search_query, "$options": "i"}}
        ]
        
    # Apply filters
    if filters:
        for k, v in filters.items():
            if v:
                if k == "priority":
                    query[k] = int(v)
                elif k == "tags":
                    query[k] = {"$in": v if isinstance(v, list) else [v]}
                else:
                    query[k] = v
                    
    cursor = db.knowledge_items.find(query).sort("updated_at", -1).limit(50)
    return await cursor.to_list(length=50)

async def restore_version(item_id: str, version_number: int, author: str = "admin") -> Optional[Dict[str, Any]]:
    db = get_database()
    existing = await db.knowledge_items.find_one({"_id": item_id})
    if not existing:
        return None
        
    version_doc = await version_service.get_version_by_number(item_id, version_number)
    if not version_doc:
        raise ValueError(f"Version {version_number} not found for item {item_id}")
        
    # Save snapshot of current state as a version before restoring
    await version_service.create_version(item_id, existing, author=author)
    
    new_version = existing.get("version", 1) + 1
    
    # Restore doc state fields
    restore_fields = {
        "title": version_doc["title"],
        "content": version_doc["content"],
        "content_clean": version_doc.get("content_clean", version_doc["content"]),
        "content_markdown": version_doc.get("content_markdown", ""),
        "category": version_doc["category"],
        "department": version_doc["department"],
        "tags": version_doc["tags"],
        "priority": version_doc["priority"],
        "version": new_version,
        "updated_at": datetime.now(timezone.utc)
    }
    
    # Manage vectors for active restoration
    prev_status = existing.get("status")
    prev_vector_ids = existing.get("vector_ids", [])
    
    if prev_status == "published":
        _remove_item_from_chroma(prev_vector_ids, item_id)
        restore_fields["vector_ids"] = []
        restore_fields["chunks_count"] = 0
        
    if existing.get("status") == "published":
        vector_ids = _index_item_in_chroma(
            item_id=item_id,
            title=restore_fields["title"],
            content=restore_fields["content"],
            source_type=existing.get("source_type", "manual"),
            category=restore_fields["category"],
            department=restore_fields["department"],
            tags=restore_fields["tags"],
            priority=restore_fields["priority"],
            language=existing.get("language", "en"),
            author=author
        )
        restore_fields["vector_ids"] = vector_ids
        restore_fields["chunks_count"] = len(vector_ids)
        clear_response_cache()
        
    await db.knowledge_items.update_one({"_id": item_id}, {"$set": restore_fields})
    
    restored_doc = await db.knowledge_items.find_one({"_id": item_id})
    
    await log_admin_activity(
        action="Version Restored",
        username=author,
        details={"title": restored_doc["title"], "id": item_id, "restored_version": version_number, "new_version": new_version}
    )
    
    return restored_doc

async def get_statistics() -> Dict[str, Any]:
    db = get_database()
    
    total_items = await db.knowledge_items.count_documents({})
    published = await db.knowledge_items.count_documents({"status": "published"})
    drafts = await db.knowledge_items.count_documents({"status": "draft"})
    archived = await db.knowledge_items.count_documents({"status": "archived"})
    expired = await db.knowledge_items.count_documents({"status": "expired"})
    
    pdfs_count = await db.knowledge_items.count_documents({"source_type": "pdf"})
    # Fetch from indexed_documents too
    try:
        pdfs_count += await db.indexed_documents.count_documents({})
    except Exception:
        pass
        
    websites_count = await db.knowledge_items.count_documents({"source_type": "website"})
    try:
        websites_count += await db.websites.count_documents({})
    except Exception:
        pass
        
    txt_count = await db.knowledge_items.count_documents({"source_type": "txt"})
    markdown_count = await db.knowledge_items.count_documents({"source_type": "markdown"})
    docx_count = await db.knowledge_items.count_documents({"source_type": "docx"})
    manual_count = await db.knowledge_items.count_documents({"source_type": "manual"})
    
    # Category counts
    category_counts = {}
    categories = [
        "Academic", "Notice", "Event", "Department", "Hostel", "Placement", 
        "Club", "Faculty", "Library", "Transport", "Policy", "Admission", 
        "Scholarship", "FAQ", "Research", "Other"
    ]
    for cat in categories:
        count = await db.knowledge_items.count_documents({"category": cat})
        category_counts[cat] = count
        
    # Chroma stats
    vector_count = 0
    embedding_count = 0
    try:
        vector_store = get_vector_store()
        vector_count = vector_store._collection.count()
        embedding_count = vector_count # 1-to-1 in Chroma typically
    except Exception:
        pass
        
    storage_used_bytes = 0
    # Estimate storage based on document sizes
    cursor = db.knowledge_items.find({}, {"content": 1})
    async for doc in cursor:
        storage_used_bytes += len(doc.get("content", "").encode("utf-8"))
        
    # Recent updates
    cursor_recent = db.knowledge_items.find({}).sort("updated_at", -1).limit(10)
    recent_updates = []
    async for doc in cursor_recent:
        recent_updates.append({
            "id": str(doc["_id"]),
            "title": doc.get("title", ""),
            "status": doc.get("status", ""),
            "source_type": doc.get("source_type", ""),
            "updated_at": doc.get("updated_at").isoformat() if doc.get("updated_at") else None,
            "author": doc.get("author", "")
        })
        
    return {
        "total_items": total_items,
        "published": published,
        "drafts": drafts,
        "archived": archived,
        "expired": expired,
        "pdfs_count": pdfs_count,
        "websites_count": websites_count,
        "txt_count": txt_count,
        "markdown_count": markdown_count,
        "docx_count": docx_count,
        "manual_count": manual_count,
        "category_counts": category_counts,
        "vector_count": vector_count,
        "embedding_count": embedding_count,
        "storage_used_bytes": storage_used_bytes,
        "recent_updates": recent_updates
    }

async def bulk_publish(ids: List[str], author: str = "admin") -> int:
    count = 0
    for item_id in ids:
        try:
            res = await update_knowledge(item_id, {"status": "published"}, author=author)
            if res:
                count += 1
        except Exception as e:
            logger.error(f"Bulk publish failed for {item_id}: {e}")
    return count

async def bulk_archive(ids: List[str], author: str = "admin") -> int:
    count = 0
    for item_id in ids:
        try:
            res = await update_knowledge(item_id, {"status": "archived"}, author=author)
            if res:
                count += 1
        except Exception as e:
            logger.error(f"Bulk archive failed for {item_id}: {e}")
    return count

async def bulk_delete(ids: List[str], author: str = "admin") -> int:
    count = 0
    for item_id in ids:
        try:
            res = await delete_knowledge(item_id, author=author)
            if res:
                count += 1
        except Exception as e:
            logger.error(f"Bulk delete failed for {item_id}: {e}")
    return count

async def bulk_reindex(ids: List[str], author: str = "admin") -> int:
    db = get_database()
    count = 0
    for item_id in ids:
        try:
            existing = await db.knowledge_items.find_one({"_id": item_id})
            if existing and existing.get("status") == "published":
                # Re-index content
                _remove_item_from_chroma(existing.get("vector_ids", []), item_id)
                vector_ids = _index_item_in_chroma(
                    item_id=item_id,
                    title=existing["title"],
                    content=existing["content"],
                    source_type=existing["source_type"],
                    category=existing["category"],
                    department=existing["department"],
                    tags=existing["tags"],
                    priority=existing["priority"],
                    language=existing.get("language", "en"),
                    author=author
                )
                await db.knowledge_items.update_one(
                    {"_id": item_id},
                    {"$set": {"vector_ids": vector_ids, "chunks_count": len(vector_ids)}}
                )
                count += 1
        except Exception as e:
            logger.error(f"Bulk reindex failed for {item_id}: {e}")
    clear_response_cache()
    return count
