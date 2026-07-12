import os
import logging
from fastapi import APIRouter, status, HTTPException
from app.core.database import get_database
from app.services.rag.vector_store import get_vector_store
from app.security.config.settings import settings

logger = logging.getLogger("security.health")
router = APIRouter(tags=["Monitoring & System Health"])

@router.get("/health")
async def health_check():
    """
    Shallow health check endpoint verifying FastAPI app availability.
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENV,
        "port": settings.PORT
    }

@router.get("/system/status")
async def system_status():
    """
    Detailed system status check verifying database connections, allowed origins,
    RAG vector database metrics, and configuration profiles.
    """
    mongo_ok = False
    chroma_ok = False
    details = {}
    
    # 1. MongoDB Status
    try:
        db = get_database()
        res = await db.command("ping")
        if res.get("ok") == 1.0:
            mongo_ok = True
            doc_count = await db.knowledge_items.count_documents({})
            admin_count = await db.admin_users.count_documents({})
            details["mongodb"] = {
                "status": "connected",
                "knowledge_items": doc_count,
                "admin_seeded": admin_count > 0
            }
        else:
            details["mongodb"] = {"status": "unhealthy", "error": "ping returned not ok"}
    except Exception as e:
        details["mongodb"] = {"status": "error", "error": str(e)}
        
    # 2. ChromaDB Status
    try:
        store = get_vector_store()
        count = store._collection.count()
        chroma_ok = True
        details["chromadb"] = {
            "status": "connected",
            "vectors": count,
            "directory": settings.VECTOR_DB_PATH
        }
    except Exception as e:
        details["chromadb"] = {"status": "error", "error": str(e)}
        
    # 3. LLM Integration Status
    details["gemini"] = {
        "model": settings.GEMINI_MODEL,
        "configured": bool(settings.GEMINI_API_KEY)
    }
    
    # 4. Service readiness flags
    details["services"] = {
        "knowledge": "Ready" if (mongo_ok and chroma_ok) else "Not Ready",
        "authentication": "Ready" if mongo_ok else "Not Ready",
        "chat": "Ready" if (mongo_ok and bool(settings.GEMINI_API_KEY)) else "Not Ready",
        "admin": "Ready" if mongo_ok else "Not Ready"
    }
    
    return {
        "version": "1.0.0",
        "environment": settings.ENV,
        "current_port": settings.PORT,
        "allowed_origins": settings.CORS_ORIGINS,
        "mongodb_status": "Connected" if mongo_ok else "Disconnected",
        "chromadb_status": "Connected" if chroma_ok else "Disconnected",
        "knowledge_status": "Ready" if (mongo_ok and chroma_ok) else "Not Ready",
        "authentication_status": "Ready" if mongo_ok else "Not Ready",
        "admin_status": "Ready" if mongo_ok else "Not Ready",
        "details": details
    }

@router.get("/config")
async def config_info():
    """
    Exposes safe configuration profile parameters (excludes all secret keys/credentials).
    """
    return {
        "environment": settings.ENV,
        "debug_mode": settings.DEBUG,
        "current_port": settings.PORT,
        "host": settings.HOST,
        "allowed_origins": settings.CORS_ORIGINS,
        "api_prefix": settings.API_PREFIX,
        "vector_db_path": settings.VECTOR_DB_PATH,
        "gemini_model": settings.GEMINI_MODEL
    }

@router.get("/ready")
async def readiness_check():
    """
    Deep readiness check endpoint verifying MongoDB, ChromaDB, and Gemini dependencies.
    """
    mongo_ok = False
    chroma_ok = False
    gemini_ok = bool(settings.GEMINI_API_KEY)
    details = {}
    
    # 1. Validate MongoDB
    try:
        db = get_database()
        res = await db.command("ping")
        if res.get("ok") == 1.0:
            mongo_ok = True
            details["mongodb"] = "connected"
        else:
            details["mongodb"] = "ping returned not ok"
    except Exception as e:
        details["mongodb"] = f"error: {str(e)}"
        
    # 2. Validate ChromaDB
    try:
        store = get_vector_store()
        count = store._collection.count()
        chroma_ok = True
        details["chromadb"] = f"connected (vectors: {count})"
    except Exception as e:
        details["chromadb"] = f"error: {str(e)}"
        
    # 3. Validate Gemini
    details["gemini_config"] = "configured" if gemini_ok else "missing api key"
    
    overall_ok = mongo_ok and chroma_ok and gemini_ok
    
    if not overall_ok:
        logger.error(f"Readiness check failed: {details}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unready",
                "details": details
            }
        )
        
    return {
        "status": "ready",
        "details": details
    }
