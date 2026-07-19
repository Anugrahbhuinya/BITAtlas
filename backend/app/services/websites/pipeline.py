import hashlib
from typing import Any
import logging
from datetime import datetime, timezone
from urllib.parse import urlparse
import uuid

from app.core import config
from app.core.database import get_database
from app.services.websites.validator import validate_url, normalize_url
from app.services.websites.crawler import crawl_single_page
from app.services.websites.extractor import extract_clean_text
from app.services.websites.metadata import extract_metadata, get_word_count
from app.services.rag.chunking_service import create_chunks
from app.services.rag.vector_store import get_vector_store
from langchain_core.documents import Document

logger = logging.getLogger("website_pipeline")

async def run_pipeline(url: str, created_by: str = "admin", overwrite_id: str | None = None) -> dict:
    """
    Runs the full ingestion pipeline for a single website:
    URL Validation → Crawling/Scraping → Content Extraction → Metadata Parsing →
    Duplicate Detection → Chunking → Embeddings Generation & Chroma Ingestion →
    MongoDB Metadata Logging → Indexing Summary.
    """
    db = get_database()
    vector_store = get_vector_store()

    # 1. URL Validation
    if not validate_url(url):
        raise ValueError("Invalid URL schema. Only HTTP and HTTPS protocols are supported.")

    normalized_url = normalize_url(url)
    domain = urlparse(normalized_url).netloc

    # 2. Download HTML
    html_content = await crawl_single_page(normalized_url, original_url=url)
    if not html_content or not html_content.strip():
        raise ValueError("Crawled website content is empty.")

    # 3. Content Extraction
    cleaned_text = extract_clean_text(html_content)
    if not cleaned_text or not cleaned_text.strip():
        raise ValueError("The webpage contains no extractable body text (headings, paragraphs, lists, or tables).")

    # 4. Content Hash & Duplicate Detection
    content_hash = hashlib.sha256(cleaned_text.encode("utf-8")).hexdigest()
    
    from app.services.websites.content_normalizer import normalize_content
    norm_text, _ = normalize_content(cleaned_text)
    normalized_content_hash = hashlib.sha256(norm_text.encode("utf-8")).hexdigest()
    
    # Exclude current overwrite ID if reindexing to avoid self-collision
    dup_query: dict[str, Any] = {"content_hash": content_hash}
    if overwrite_id:
        dup_query["_id"] = {"$ne": overwrite_id}
        
    duplicate = await db.websites.find_one(dup_query)
    if duplicate:
        logger.info(f"Duplicate website content detected. URL: {normalized_url} matches existing URL: {duplicate['url']}")
        return {
            "status": "Duplicate",
            "message": "Already indexed.",
            "detail": f"Content is identical to already indexed website: {duplicate['url']}",
            "website_id": str(duplicate["_id"])
        }

    # 5. Metadata Parsing
    page_metadata = extract_metadata(html_content, fallback_url=normalized_url)
    word_count = get_word_count(cleaned_text)
    title = page_metadata["title"] or domain

    # Enforce minimum 100-word limit constraint
    if word_count < 100:
        import os
        try:
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            debug_dir = os.path.join(backend_dir, "debug_extraction")
            os.makedirs(debug_dir, exist_ok=True)
            debug_file = os.path.join(debug_dir, f"extract_debug_low_words_{uuid.uuid4().hex[:8]}.txt")
            with open(debug_file, "w", encoding="utf-8") as f:
                f.write(f"=== CRAWLED URL ===\n{normalized_url}\n\n")
                f.write(f"=== WORD COUNT ===\n{word_count}\n\n")
                f.write("=== CLEANED TEXT ===\n")
                f.write(cleaned_text)
            logger.warning(f"Webpage content has only {word_count} words (minimum 100 required). Saved cleaned text to: {debug_file}")
        except Exception as e:
            logger.error(f"Failed to write low words debug file: {e}")
            
        raise ValueError(f"The webpage contains insufficient text content ({word_count} words). A minimum of 100 words is required for indexing.")

    # 6. Chunking
    chunks = create_chunks(cleaned_text)
    if not chunks:
        raise ValueError("No text chunks could be generated from the extracted content.")

    # Limit chunks size to prevent resource overflow
    max_chunks = getattr(config, "MAX_CHUNKS", 500)
    if len(chunks) > max_chunks:
        logger.warning(f"Chunks count ({len(chunks)}) exceeds limits. Truncating to {max_chunks}.")
        chunks = chunks[:max_chunks]
        
    chunk_count = len(chunks)

    # 7. Embed & Ingest into ChromaDB
    website_id = overwrite_id or str(uuid.uuid4())
    chroma_docs = []
    vector_ids = []

    for i, chunk in enumerate(chunks):
        chunk_id = f"web_{website_id}_chunk_{i}"
        vector_ids.append(chunk_id)

        # Set up compatibility and custom metadata:
        # source="kb_document" for retriever logic, filename & page for citation formatting
        doc = Document(
            page_content=chunk,
            metadata={
                "source": "kb_document",
                "source_type": "website",
                "source_name": title,
                "title": title,
                "url": normalized_url,
                "filename": f"{title} ({normalized_url})",
                "page": f"Chunk {i + 1}",
                "chunk_index": i,
                "chunk_number": i,
                "doc_id": website_id,
                "document_id": website_id,
                "indexed_at": datetime.now(timezone.utc).isoformat()
            }
        )
        chroma_docs.append(doc)

    logger.info(f"Adding {chunk_count} document chunks to ChromaDB collection for site: {title}")
    # langchain Chroma handles embedding generation and ingestion automatically
    vector_store.add_documents(chroma_docs, ids=vector_ids)

    # 8. Store in MongoDB 'websites' collection
    existing_doc = None
    if overwrite_id:
        existing_doc = await db.websites.find_one({"_id": website_id})

    mongo_doc = {
        "url": normalized_url,
        "domain": domain,
        "title": title,
        "description": page_metadata["description"] or "",
        "canonical_url": page_metadata["canonical_url"] or normalized_url,
        "language": page_metadata["language"] or "en",
        "word_count": word_count,
        "chunk_count": chunk_count,
        "content_hash": content_hash,
        "normalized_content_hash": normalized_content_hash,
        "indexed_at": existing_doc.get("indexed_at", datetime.now(timezone.utc)) if existing_doc else datetime.now(timezone.utc),
        "last_crawled": datetime.now(timezone.utc),
        "status": "Indexed",
        "created_by": created_by,
        "vector_ids": vector_ids,
        # Extended Sync Status Fields
        "last_checked": datetime.now(timezone.utc),
        "last_changed": datetime.now(timezone.utc) if not existing_doc or existing_doc.get("content_hash") != content_hash else existing_doc.get("last_changed", datetime.now(timezone.utc)),
        "sync_status": "Healthy",
        "sync_enabled": existing_doc.get("sync_enabled", True) if existing_doc else True,
        "last_error": None,
        "check_count": (existing_doc.get("check_count", 0) + 1) if existing_doc else 1,
        "successful_checks": (existing_doc.get("successful_checks", 0) + 1) if existing_doc else 1,
        "failed_checks": existing_doc.get("failed_checks", 0) if existing_doc else 0
    }

    if overwrite_id:
        await db.websites.update_one({"_id": website_id}, {"$set": mongo_doc})
    else:
        mongo_doc["_id"] = website_id
        await db.websites.insert_one(mongo_doc)

    # Log Admin activity
    from app.services.admin_service import log_admin_activity
    await log_admin_activity(
        action="Website Indexed" if not overwrite_id else "Website Re-indexed",
        username=created_by,
        details={
            "url": normalized_url,
            "title": title,
            "chunks": chunk_count,
            "word_count": word_count
        }
    )

    return {
        "status": "Completed",
        "message": "Website indexed successfully.",
        "website_id": website_id,
        "url": normalized_url,
        "title": title,
        "domain": domain,
        "word_count": word_count,
        "chunk_count": chunk_count,
        "indexed_at": mongo_doc["indexed_at"]
    }
