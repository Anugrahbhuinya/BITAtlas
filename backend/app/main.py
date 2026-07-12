import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.routes.chat import router
from app.routes.history import router as history_router
from app.routes.admin import router as admin_router
from app.routes.websites import router as websites_router
from app.routes.knowledge import router as knowledge_router
from app.auth.routes import router as auth_router
from app.student.routes import router as student_router
from app.student_preferences.routes import router as preferences_router
from app.routes.academics import router as academics_router
from app.routes.timetable import router as timetable_router
from app.routes.attendance import router as attendance_router
from app.routes.planner import router as planner_router
from app.routes.academic_dashboard import router as academic_dashboard_router
from app.navigation import navigation_router

# Health & Monitoring Router
from app.security.monitoring.health import router as health_router

from app.services.admin_service import seed_admin_user
from app.services.websites.scheduler import start_scheduler, stop_scheduler

# Security & Middleware imports
from app.security.config.settings import settings
from app.core.port_checker import check_port_conflicts
if os.getenv("APP_ENV", "development").lower() != "testing":
    if not os.environ.get("UVICORN_PORT_CHECKED"):
        check_port_conflicts([settings.PORT, 5180])
        os.environ["UVICORN_PORT_CHECKED"] = "1"
from app.security.monitoring.logging import setup_structured_logging
from app.security.core.middleware.request_id import RequestIDMiddleware
from app.security.core.middleware.timing import RequestTimingMiddleware
from app.security.core.middleware.security import SecurityHeadersMiddleware
from app.security.core.middleware.logging import StructuredLoggingMiddleware

from app.security.core.exceptions.handlers import (
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    rate_limit_exception_handler
)
from app.security.rate_limit.rate_limiter import RateLimitException

# Initialize structured logging on startup configuration
setup_structured_logging(settings.LOG_LEVEL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup activities
    os.makedirs("uploads/profile_pictures", exist_ok=True)
    await seed_admin_user()
    
    # Pre-load Cross-Encoder reranker model to avoid first-request lazy loading latency
    try:
        from app.services.rag.reranker import load_reranker
        load_reranker()
    except Exception as e:
        print(f"Failed to pre-load Cross-Encoder reranker: {e}")
    
    # Initialize MongoDB Indexes to avoid collection scans
    try:
        from app.core.database import get_database
        db = get_database()
        collections_and_indexes = [
            ("nodes", [("id", True)]),
            ("students", [("email", True), ("roll_number", True)]),
            ("student_preferences", [("student_id", True)]),
            ("academic_workspaces", [("student_id", True)]),
            ("timetables", [("student_id", True)]),
            ("sessions", [("sessionId", True)]),
            ("indexed_documents", [("hash", True), ("id", True)]),
            ("knowledge_items", [("status", False), ("category", False), ("source_type", False)]),
            ("knowledge_versions", [("knowledge_id", False)]),
        ]
        for coll_name, index_fields in collections_and_indexes:
            for field, unique in index_fields:
                try:
                    await db[coll_name].create_index(field, unique=unique)
                except Exception:
                    try:
                        await db[coll_name].create_index(field, unique=False)
                    except Exception:
                        pass
        # Create text index for full-text search on knowledge items
        try:
            await db.knowledge_items.create_index([("title", "text"), ("content", "text")])
        except Exception:
            pass
    except Exception as e:
        print(f"Failed to initialize database indexes: {e}")

    async def run_diagnostics():
        mongo_status = "Disconnected"
        chroma_status = "Disconnected"
        knowledge_status = "Not Ready"
        auth_status = "Not Ready"
        chat_status = "Not Ready"
        admin_status = "Not Ready"
        
        # 1. MongoDB
        try:
            from app.core.database import get_database
            db = get_database()
            ping_res = await db.command("ping")
            if ping_res.get("ok") == 1.0:
                mongo_status = "Connected"
        except Exception as e:
            mongo_status = f"Failed ({str(e)})"
            
        # 2. ChromaDB
        try:
            from app.services.rag.vector_store import get_vector_store
            vs = get_vector_store()
            count = vs._collection.count()
            chroma_status = f"Connected ({count} vectors)"
        except Exception as e:
            chroma_status = f"Failed ({str(e)})"
            
        # 3. Knowledge
        if mongo_status.startswith("Connected") and not chroma_status.startswith("Failed"):
            try:
                doc_count = await db.knowledge_items.count_documents({})
                knowledge_status = f"Ready ({doc_count} items)"
            except Exception as e:
                knowledge_status = f"Failed ({str(e)})"
                
        # 4. Authentication & Admin
        if mongo_status.startswith("Connected"):
            try:
                admin_count = await db.admin_users.count_documents({})
                if admin_count > 0:
                    auth_status = "Ready"
                    admin_status = "Ready"
                else:
                    auth_status = "Ready (No Admin Seeded)"
                    admin_status = "Ready"
            except Exception as e:
                auth_status = f"Failed ({str(e)})"
                admin_status = f"Failed ({str(e)})"
                
        # 5. Chat
        if mongo_status.startswith("Connected") and settings.GEMINI_API_KEY:
            chat_status = "Ready"
        elif not settings.GEMINI_API_KEY:
            chat_status = "Ready (LLM Key Missing)"
        else:
            chat_status = "Not Ready"
            
        print("\n" + "="*48, flush=True)
        print("BIT Mesra AI Agent", flush=True)
        print(f"Environment:     {settings.ENV.capitalize()}", flush=True)
        print(f"Backend:         http://{settings.HOST}:{settings.PORT}", flush=True)
        print(f"Allowed Origins: {', '.join(settings.CORS_ORIGINS)}", flush=True)
        print(f"MongoDB:         {mongo_status}", flush=True)
        print(f"ChromaDB:        {chroma_status}", flush=True)
        print(f"Knowledge:       {knowledge_status}", flush=True)
        print(f"Authentication:  {auth_status}", flush=True)
        print(f"Chat:            {chat_status}", flush=True)
        print(f"Admin:           {admin_status}", flush=True)
        print("="*48 + "\n", flush=True)

    await start_scheduler()
    await run_diagnostics()
    yield
    # Shutdown activities
    await stop_scheduler()

app = FastAPI(
    title="BIT Mesra AI Assistant",
    lifespan=lifespan
)

# Attach Middlewares (Note: Order of execution is bottom-to-top for Starlette middlewares)
# 1. Request ID (innermost, adds state.request_id)
app.add_middleware(RequestIDMiddleware)
# 2. Timing
app.add_middleware(RequestTimingMiddleware)
# 3. Security headers (OWASP)
app.add_middleware(SecurityHeadersMiddleware)
# 4. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 5. Logging (outermost, tracks execution duration and logs path/method)
app.add_middleware(StructuredLoggingMiddleware)

# Mount media static directories
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Exception Handlers
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(RateLimitException, rate_limit_exception_handler)

# Include API Routers
app.include_router(health_router) # Exposes /health & /ready
app.include_router(router)
app.include_router(history_router)
app.include_router(admin_router)
app.include_router(websites_router)
app.include_router(knowledge_router)
app.include_router(auth_router)
app.include_router(student_router)
app.include_router(preferences_router)
app.include_router(academics_router)
app.include_router(timetable_router)
app.include_router(attendance_router)
app.include_router(planner_router)
app.include_router(academic_dashboard_router)
app.include_router(navigation_router)

@app.get("/")
def root():
    return {
        "message": "BIT Mesra AI Assistant API Running"  # Reloaded config
    }