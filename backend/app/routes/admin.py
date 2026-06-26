from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List
from app.core.database import get_database
from app.core.auth import verify_password, create_access_token, get_current_admin
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
