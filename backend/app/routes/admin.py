import os
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import List
from app.core.database import get_database
from app.core.auth import verify_password, create_access_token, get_current_admin
from app.core.rate_limiter import upload_rate_limiter
from app.services.rag.dynamic_indexer import (
    index_pdf_generator,
    delete_indexed_document,
    reindex_document_generator
)
from app.services.rag.vector_store import get_vector_store, PERSIST_DIRECTORY
from app.models.admin import (
    AdminLoginRequest,
    TokenResponse,
    SystemStatusResponse,
    ActivityLogResponse,
    DocumentListResponse,
    DashboardStatsResponse,
    AdminSettingsResponse
)
from app.services.admin_service import (
    log_admin_activity,
    get_dashboard_stats,
    get_system_status,
    get_activity_logs,
    get_documents,
    get_admin_settings
)

logger = logging.getLogger("admin_routes")

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin Portal"]
)

@router.post("/login", response_model=TokenResponse)
async def login(login_data: AdminLoginRequest, request: Request):
    db = get_database()
    username = login_data.username
    password = login_data.password

    # Find user in admin_users collection
    admin = await db.admin_users.find_one({"username": username})
    
    if not admin or not verify_password(password, admin["password_hash"]):
        # Log failed attempt
        await log_admin_activity(
            action="Admin Login Failed",
            username=username,
            details={"ip_address": request.client.host, "reason": "Invalid credentials"}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate access token
    access_token = create_access_token(data={"sub": username})
    
    # Log successful login
    await log_admin_activity(
        action="Admin Login",
        username=username,
        details={"ip_address": request.client.host}
    )

    return TokenResponse(
        access_token=access_token,
        username=username
    )

@router.post("/logout")
async def logout(current_user: str = Depends(get_current_admin)):
    await log_admin_activity("Admin Logout", current_user)
    return {"status": "success", "message": "Logged out successfully"}

@router.get("/dashboard", response_model=DashboardStatsResponse)
async def get_dashboard(current_user: str = Depends(get_current_admin)):
    stats = await get_dashboard_stats()
    return stats

@router.get("/statistics", response_model=DashboardStatsResponse)
async def get_statistics(current_user: str = Depends(get_current_admin)):
    stats = await get_dashboard_stats()
    return stats

@router.get("/system-status", response_model=SystemStatusResponse)
async def get_status(current_user: str = Depends(get_current_admin)):
    components = await get_system_status()
    return SystemStatusResponse(components=components)

@router.get("/activity", response_model=ActivityLogResponse)
async def get_activity(current_user: str = Depends(get_current_admin)):
    logs = await get_activity_logs()
    return ActivityLogResponse(logs=logs, total=len(logs))

@router.get("/documents", response_model=DocumentListResponse)
async def get_docs(current_user: str = Depends(get_current_admin)):
    docs = await get_documents()
    return DocumentListResponse(documents=docs, total=len(docs))

@router.get("/settings", response_model=AdminSettingsResponse)
async def get_settings(current_user: str = Depends(get_current_admin)):
    settings = get_admin_settings()
    return AdminSettingsResponse(**settings)

@router.post("/documents/upload")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    overwrite: bool = False,
    current_user: str = Depends(get_current_admin)
):
    """
    Upload and index a PDF document. Rate-limited to protect server resources.
    Streams progress statuses back to the client.
    """
    # Protect with rate limiter
    upload_rate_limiter.check_rate_limit(request.client.host)
    
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported."
        )
        
    file_content = await file.read()
    
    # Log initial intent
    await log_admin_activity(
        action="Document Upload Initiated",
        username=current_user,
        details={"filename": file.filename, "size_bytes": len(file_content)}
    )
    
    return StreamingResponse(
        index_pdf_generator(file_content, file.filename, overwrite),
        media_type="application/x-ndjson"
    )

@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: str,
    current_user: str = Depends(get_current_admin)
):
    """
    Delete metadata, saved files, and database vectors for an indexed document.
    """
    success = await delete_indexed_document(doc_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {doc_id} not found."
        )
    return {"status": "success", "message": "Document and associated vectors deleted successfully."}

@router.post("/documents/{doc_id}/reindex")
async def reindex_document(
    doc_id: str,
    current_user: str = Depends(get_current_admin)
):
    """
    Extract text, chunk and re-index an existing PDF file.
    Streams progress statuses back to the client.
    """
    # Log initial intent
    await log_admin_activity(
        action="Document Reindex Initiated",
        username=current_user,
        details={"doc_id": doc_id}
    )
    
    return StreamingResponse(
        reindex_document_generator(doc_id),
        media_type="application/x-ndjson"
    )

@router.get("/index-health")
async def get_index_health(
    current_user: str = Depends(get_current_admin)
):
    """
    Calculate and analyze index database health, orphans, missing vectors, and directories.
    """
    db = get_database()
    vector_store = get_vector_store()
    
    try:
        # 1. Count dynamic documents in MongoDB
        dynamic_docs_count = await db.indexed_documents.count_documents({})
        
        # 2. Query Chroma collection info
        total_vectors = 0
        try:
            total_vectors = vector_store._collection.count()
        except Exception as e:
            logger.error(f"Error getting Chroma count: {e}")
            
        # Get all vectors from ChromaDB to check for orphans
        chroma_res = vector_store.get(include=["metadatas"])
        chroma_ids = set(chroma_res.get("ids", []))
        chroma_metadatas = chroma_res.get("metadatas", [])
        
        # 3. Retrieve dynamic documents from MongoDB
        mongo_docs = []
        cursor = db.indexed_documents.find({})
        async for doc in cursor:
            mongo_docs.append(doc)
            
        mongo_doc_ids = {d["id"] for d in mongo_docs}
        mongo_vector_ids = set()
        for doc in mongo_docs:
            for vid in doc.get("vector_ids", []):
                mongo_vector_ids.add(vid)
                
        # 4. Find orphan vectors
        orphan_vectors = []
        for idx, vid in enumerate(chroma_res.get("ids", [])):
            metadata = chroma_metadatas[idx] if idx < len(chroma_metadatas) else {}
            if metadata and (metadata.get("source") == "kb_document" or "doc_id" in metadata):
                doc_id = metadata.get("doc_id")
                if not doc_id or doc_id not in mongo_doc_ids or vid not in mongo_vector_ids:
                    orphan_vectors.append({
                        "vector_id": vid,
                        "doc_id": doc_id,
                        "name": metadata.get("name", "unknown")
                    })
                    
        # 5. Find missing vectors
        missing_vectors = []
        for doc in mongo_docs:
            doc_id = doc["id"]
            filename = doc["filename"]
            for vid in doc.get("vector_ids", []):
                if vid not in chroma_ids:
                    missing_vectors.append({
                        "vector_id": vid,
                        "doc_id": doc_id,
                        "filename": filename
                    })
                    
        # 6. Calculate total size of ChromaDB directory on disk
        chroma_size_bytes = 0
        if os.path.exists(PERSIST_DIRECTORY):
            for root, _, files in os.walk(PERSIST_DIRECTORY):
                for f in files:
                    fp = os.path.join(root, f)
                    try:
                        chroma_size_bytes += os.path.getsize(fp)
                    except Exception:
                        pass
                        
        health_state = "Healthy"
        details = "Vector storage and metadata are fully synchronized."
        
        if orphan_vectors or missing_vectors:
            health_state = "Degraded"
            details = f"Synchronization issues detected: {len(orphan_vectors)} orphan vectors and {len(missing_vectors)} missing vectors."
            
        return {
            "status": "success",
            "health_state": health_state,
            "details": details,
            "total_vectors": total_vectors,
            "dynamic_documents": dynamic_docs_count,
            "orphan_vectors_count": len(orphan_vectors),
            "orphan_vectors": orphan_vectors,
            "missing_vectors_count": len(missing_vectors),
            "missing_vectors": missing_vectors,
            "chroma_size_bytes": chroma_size_bytes
        }
    except Exception as e:
        logger.error(f"Index health diagnostics failed: {e}", exc_info=True)
        return {
            "status": "error",
            "health_state": "Critical",
            "details": f"Index health diagnostics failed: {str(e)}",
            "total_vectors": 0,
            "dynamic_documents": 0,
            "orphan_vectors_count": 0,
            "orphan_vectors": [],
            "missing_vectors_count": 0,
            "missing_vectors": [],
            "chroma_size_bytes": 0
        }
