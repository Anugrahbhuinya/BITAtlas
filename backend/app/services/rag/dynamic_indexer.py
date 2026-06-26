import os
import uuid
import hashlib
import logging
import json
from datetime import datetime, timezone
from typing import List, Tuple, AsyncGenerator, Dict, Any
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.services.rag.vector_store import get_vector_store, PERSIST_DIRECTORY
from app.core.database import get_database

logger = logging.getLogger("dynamic_indexer")

# Absolute path to upload directory
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
UPLOAD_DIR = os.path.join(BACKEND_DIR, "uploads", "pdfs")

def calculate_sha256(content: bytes) -> str:
    """Calculate SHA256 hash of file content."""
    sha256_hash = hashlib.sha256()
    sha256_hash.update(content)
    return sha256_hash.hexdigest()

def extract_pdf_text_by_page(file_path: str) -> List[Tuple[str, int]]:
    """
    Extracts text page-by-page from a PDF file.
    Returns a list of (page_text, page_number_1_indexed).
    """
    pages_data = []
    reader = PdfReader(file_path)
    
    if reader.is_encrypted:
        raise ValueError("PDF is encrypted. Decrypt the PDF before uploading.")
        
    for idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages_data.append((text.strip(), idx + 1))
        
    return pages_data

def chunk_pdf_pages(pages_data: List[Tuple[str, int]], source_name: str, doc_id: str, file_hash: str) -> List[Document]:
    """
    Chunks each page's text using RecursiveCharacterTextSplitter (chunk_size=500, chunk_overlap=100)
    preserving page numbers.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    
    documents = []
    chunk_idx = 0
    for text, page_num in pages_data:
        if not text:
            continue
        chunks = text_splitter.split_text(text)
        for chunk in chunks:
            # Set metadata standard keys + keep backward compatible ones
            doc = Document(
                page_content=chunk,
                metadata={
                    "document_id": doc_id,
                    "filename": source_name,
                    "page": page_num,
                    "source": "kb_document",
                    "source_type": "pdf",
                    "chunk_number": chunk_idx,
                    "sha256": file_hash,
                    # Backwards compatibility keys
                    "name": source_name,
                    "title": source_name,
                    "doc_id": doc_id,
                    "type": "pdf"
                }
            )
            documents.append(doc)
            chunk_idx += 1
            
    return documents

async def index_pdf_generator(
    file_content: bytes, 
    filename: str, 
    overwrite: bool = False
) -> AsyncGenerator[str, None]:
    """
    Validates, saves, extracts, chunks, embeds, and indexes a PDF.
    Yields progress status as line-delimited JSON.
    Supports atomic rollback in case of failure.
    """
    db = get_database()
    vector_store = get_vector_store()
    
    # 1. Start Uploading
    yield json.dumps({"status": "Uploading", "progress": 10}) + "\n"
    
    # Validation
    if not file_content.startswith(b"%PDF"):
        yield json.dumps({"status": "Failed", "detail": "Invalid file format. Only PDF files are supported."}) + "\n"
        return
        
    if len(file_content) > 10 * 1024 * 1024: # 10MB limit
        yield json.dumps({"status": "Failed", "detail": "File size exceeds 10MB limit."}) + "\n"
        return
        
    # Calculate SHA256 and check for duplicates
    file_hash = calculate_sha256(file_content)
    existing_doc = await db.indexed_documents.find_one({"hash": file_hash})
    
    if existing_doc:
        if not overwrite:
            yield json.dumps({
                "status": "Duplicate", 
                "detail": f"A document with the same content already exists: {existing_doc['filename']}",
                "doc_id": existing_doc["id"]
            }) + "\n"
            return
        else:
            # Overwrite requested. Delete the existing document first.
            yield json.dumps({"status": "Uploading", "detail": f"Overwriting existing document: {existing_doc['filename']}..."}) + "\n"
            try:
                await delete_indexed_document(existing_doc["id"])
            except Exception as e:
                logger.error(f"Error during overwrite deletion of {existing_doc['id']}: {e}")
                
    # Initialize variables for atomic rollback tracking
    doc_id = f"doc_{uuid.uuid4()}"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, f"{doc_id}.pdf")
    
    saved_on_disk = False
    vector_ids: List[str] = []
    metadata_saved = False
    
    try:
        # Write PDF to disk
        with open(file_path, "wb") as f:
            f.write(file_content)
        saved_on_disk = True
        
        # 2. Extracting text
        yield json.dumps({"status": "Extracting", "progress": 30}) + "\n"
        try:
            pages_data = extract_pdf_text_by_page(file_path)
        except ValueError as e:
            yield json.dumps({"status": "Failed", "detail": str(e)}) + "\n"
            # Cleanup immediately
            if os.path.exists(file_path):
                os.remove(file_path)
            return
            
        # 3. Chunking
        yield json.dumps({"status": "Chunking", "progress": 50}) + "\n"
        chunks = chunk_pdf_pages(pages_data, filename, doc_id, file_hash)
        
        if not chunks:
            yield json.dumps({"status": "Failed", "detail": "The PDF contains no extractable text."}) + "\n"
            if os.path.exists(file_path):
                os.remove(file_path)
            return
            
        # 4. Embedding
        yield json.dumps({"status": "Embedding", "progress": 70}) + "\n"
        # LangChain Chroma handles embedding internally, but we prepare vector IDs for tracking.
        vector_ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        
        # 5. Updating Chroma
        yield json.dumps({"status": "Updating Chroma", "progress": 85}) + "\n"
        # Sync-like execution block wrapped in try for ChromaDB insertion
        vector_store.add_documents(chunks, ids=vector_ids)
        
        # 6. Saving Metadata
        yield json.dumps({"status": "Saving Metadata", "progress": 95}) + "\n"
        metadata = {
            "id": doc_id,
            "filename": filename,
            "hash": file_hash,
            "filepath": file_path,
            "type": "pdf",
            "status": "Indexed",
            "created": datetime.now(timezone.utc),
            "size_bytes": len(file_content),
            "chunks_count": len(chunks),
            "vector_ids": vector_ids
        }
        await db.indexed_documents.insert_one(metadata)
        metadata_saved = True
        
        # Log Admin Activity
        from app.services.admin_service import log_admin_activity
        await log_admin_activity(
            action="Document Uploaded & Indexed",
            username="admin",  # Can be overridden or passed down
            details={"filename": filename, "doc_id": doc_id, "chunks": len(chunks)}
        )
        
        # 7. Completed
        yield json.dumps({
            "status": "Completed", 
            "progress": 100, 
            "doc_id": doc_id,
            "filename": filename,
            "size_bytes": len(file_content),
            "chunks_count": len(chunks)
        }) + "\n"
        
    except Exception as e:
        logger.error(f"Failed to index document {filename}: {str(e)}", exc_info=True)
        yield json.dumps({"status": "Failed", "detail": f"Failed during indexing: {str(e)}"}) + "\n"
        
        # ATOMIC ROLLBACK
        logger.warning(f"Starting atomic rollback for {filename} ({doc_id})")
        
        # Rollback metadata from MongoDB
        if metadata_saved:
            try:
                await db.indexed_documents.delete_one({"id": doc_id})
                logger.info("Rollback: MongoDB metadata deleted.")
            except Exception as me:
                logger.error(f"Rollback error: failed to delete MongoDB metadata: {me}")
                
        # Rollback ChromaDB vectors
        if vector_ids:
            try:
                # Retrieve actual vector store and delete
                vector_store.delete(ids=vector_ids)
                logger.info(f"Rollback: deleted {len(vector_ids)} vectors from ChromaDB.")
            except Exception as ve:
                logger.error(f"Rollback error: failed to delete ChromaDB vectors: {ve}")
                
        # Rollback PDF from disk
        if saved_on_disk and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info("Rollback: PDF deleted from disk.")
            except Exception as fe:
                logger.error(f"Rollback error: failed to delete PDF file: {fe}")

async def delete_indexed_document(doc_id: str) -> bool:
    """
    Deletes a document from disk, ChromaDB, and MongoDB metadata.
    """
    db = get_database()
    vector_store = get_vector_store()
    
    # 1. Fetch document metadata
    doc = await db.indexed_documents.find_one({"id": doc_id})
    if not doc:
        logger.warning(f"Document {doc_id} not found in database for deletion.")
        return False
        
    filename = doc.get("filename", "unknown")
    vector_ids = doc.get("vector_ids", [])
    file_path = doc.get("filepath")
    
    # 2. Delete vectors from ChromaDB
    # If vector_ids is empty, try fallback by querying Chroma for doc_id
    if not vector_ids:
        try:
            chroma_res = vector_store.get(where={"doc_id": doc_id})
            vector_ids = chroma_res.get("ids", [])
        except Exception as e:
            logger.error(f"Failed to query ChromaDB for fallback deletion of {doc_id}: {e}")
            
    if vector_ids:
        try:
            vector_store.delete(ids=vector_ids)
            logger.info(f"Deleted {len(vector_ids)} vectors from ChromaDB for doc {doc_id}.")
        except Exception as e:
            logger.error(f"Failed to delete ChromaDB vectors for {doc_id}: {e}")
            
    # 3. Delete file from disk
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            logger.info(f"Deleted physical file {file_path} for doc {doc_id}.")
        except Exception as e:
            logger.error(f"Failed to delete physical file {file_path}: {e}")
            
    # 4. Delete MongoDB metadata
    try:
        await db.indexed_documents.delete_one({"id": doc_id})
        logger.info(f"Deleted MongoDB metadata for doc {doc_id}.")
    except Exception as e:
        logger.error(f"Failed to delete MongoDB metadata for {doc_id}: {e}")
        
    # Log Admin Activity
    from app.services.admin_service import log_admin_activity
    await log_admin_activity(
        action="Document Deleted",
        username="admin",
        details={"filename": filename, "doc_id": doc_id}
    )
    
    return True

async def reindex_document_generator(doc_id: str) -> AsyncGenerator[str, None]:
    """
    Reindexes an existing PDF document from disk.
    Yields progress status as line-delimited JSON.
    """
    db = get_database()
    vector_store = get_vector_store()
    
    # 1. Fetch document metadata
    doc = await db.indexed_documents.find_one({"id": doc_id})
    if not doc:
        yield json.dumps({"status": "Failed", "detail": f"Document {doc_id} not found."}) + "\n"
        return
        
    filename = doc["filename"]
    file_path = doc["filepath"]
    old_vector_ids = doc.get("vector_ids", [])
    
    yield json.dumps({"status": "Extracting", "progress": 20}) + "\n"
    
    if not file_path or not os.path.exists(file_path):
        yield json.dumps({"status": "Failed", "detail": f"Physical file not found on disk at {file_path}."}) + "\n"
        # Update metadata status to Failed
        await db.indexed_documents.update_one(
            {"id": doc_id},
            {"$set": {"status": "Failed", "error": "Physical file missing"}}
        )
        return
        
    # Track states for fallback
    new_vector_ids: List[str] = []
    
    try:
        # Extract text page-by-page
        pages_data = extract_pdf_text_by_page(file_path)
        
        # 2. Chunking
        yield json.dumps({"status": "Chunking", "progress": 40}) + "\n"
        chunks = chunk_pdf_pages(pages_data, filename, doc_id, doc["hash"])
        
        if not chunks:
            yield json.dumps({"status": "Failed", "detail": "The PDF contains no extractable text."}) + "\n"
            return
            
        # 3. Embedding
        yield json.dumps({"status": "Embedding", "progress": 60}) + "\n"
        new_vector_ids = [f"{doc_id}_chunk_{i}_{int(datetime.now(timezone.utc).timestamp())}" for i in range(len(chunks))]
        
        # 4. Updating Chroma (Insert new vectors)
        yield json.dumps({"status": "Updating Chroma", "progress": 80}) + "\n"
        vector_store.add_documents(chunks, ids=new_vector_ids)
        
        # 5. Delete old vectors from ChromaDB (Clean up previous index)
        if old_vector_ids:
            try:
                vector_store.delete(ids=old_vector_ids)
                logger.info(f"Deleted {len(old_vector_ids)} old vectors from ChromaDB during reindexing of {doc_id}.")
            except Exception as e:
                logger.error(f"Failed to delete old ChromaDB vectors during reindexing of {doc_id}: {e}")
                
        # 6. Saving Metadata
        yield json.dumps({"status": "Saving Metadata", "progress": 95}) + "\n"
        await db.indexed_documents.update_one(
            {"id": doc_id},
            {
                "$set": {
                    "status": "Indexed",
                    "chunks_count": len(chunks),
                    "vector_ids": new_vector_ids,
                    "updated": datetime.now(timezone.utc)
                },
                "$unset": {"error": ""}
            }
        )
        
        # Log Admin Activity
        from app.services.admin_service import log_admin_activity
        await log_admin_activity(
            action="Document Reindexed",
            username="admin",
            details={"filename": filename, "doc_id": doc_id, "chunks": len(chunks)}
        )
        
        # 7. Completed
        yield json.dumps({
            "status": "Completed", 
            "progress": 100, 
            "doc_id": doc_id,
            "filename": filename,
            "chunks_count": len(chunks)
        }) + "\n"
        
    except Exception as e:
        logger.error(f"Failed to reindex document {filename} ({doc_id}): {str(e)}", exc_info=True)
        yield json.dumps({"status": "Failed", "detail": f"Failed during reindexing: {str(e)}"}) + "\n"
        
        # Rollback newly added vectors if failed
        if new_vector_ids:
            try:
                vector_store.delete(ids=new_vector_ids)
                logger.info(f"Reindex Rollback: deleted new vectors {len(new_vector_ids)} from ChromaDB.")
            except Exception as ve:
                logger.error(f"Reindex Rollback error: failed to delete new ChromaDB vectors: {ve}")
                
        # Update metadata status to Failed
        await db.indexed_documents.update_one(
            {"id": doc_id},
            {"$set": {"status": "Failed", "error": str(e)}}
        )
