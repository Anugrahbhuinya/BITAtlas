import logging
import hashlib
from typing import Dict, Any, Optional, List
from app.core.database import get_database
from app.services.knowledge.txt_processor import process_txt
from app.services.knowledge.markdown_processor import process_markdown
from app.services.knowledge.docx_processor import process_docx
from app.services.knowledge import knowledge_service

logger = logging.getLogger("file_upload_service")

def calculate_sha256(content: bytes) -> str:
    sha256_hash = hashlib.sha256()
    sha256_hash.update(content)
    return sha256_hash.hexdigest()

async def upload_knowledge_file(
    file_content: bytes,
    filename: str,
    category: str,
    department: str = "",
    tags: List[str] = None,
    priority: int = 3,
    expires_at: Optional[str] = None,
    author: str = "admin",
    overwrite: bool = False
) -> Dict[str, Any]:
    """
    Handles file upload, content parsing (TXT/MD/DOCX), duplicate detection, and indexes into KMS.
    """
    if tags is None:
        tags = []
        
    db = get_database()
    file_hash = calculate_sha256(file_content)
    
    # 1. Duplicate Detection
    existing_doc = await db.knowledge_items.find_one({"file_hash": file_hash})
    if existing_doc:
        if not overwrite:
            return {
                "status": "Duplicate",
                "message": f"A document with the same content already exists: {existing_doc['title']}",
                "id": str(existing_doc["_id"])
            }
        else:
            # Delete duplicate doc first
            logger.info(f"Overwriting existing knowledge file: {existing_doc['title']}")
            await knowledge_service.delete_knowledge(existing_doc["_id"], author=author)
            
    # 2. Process file based on extension
    ext = filename.split(".")[-1].lower()
    content = ""
    content_markdown = ""
    source_type = "manual"
    
    if ext == "txt":
        content = process_txt(file_content, filename)
        source_type = "txt"
    elif ext == "md":
        content_markdown, content = process_markdown(file_content, filename)
        source_type = "markdown"
    elif ext == "docx":
        content = process_docx(file_content, filename)
        source_type = "docx"
    else:
        raise ValueError("Unsupported file format. Only TXT, MD, and DOCX files are supported.")
        
    if not content or not content.strip():
        raise ValueError("No extractable text found in the file.")
        
    # 3. Create KMS Knowledge Item
    payload = {
        "title": filename,
        "content": content,
        "content_markdown": content_markdown,
        "source_type": source_type,
        "category": category,
        "department": department,
        "tags": tags,
        "status": "published", # Uploaded files published by default
        "priority": priority,
        "language": "en",
        "expires_at": expires_at,
        "original_filename": filename,
        "file_hash": file_hash,
        "metadata": {
            "file_size_bytes": len(file_content)
        }
    }
    
    doc = await knowledge_service.create_knowledge(payload, author=author)
    return {
        "status": "Completed",
        "message": f"Successfully processed and indexed {filename}.",
        "id": doc["_id"],
        "title": doc["title"],
        "chunks_count": doc["chunks_count"]
    }
