from fastapi import APIRouter, Depends, Request, status, HTTPException
from app.security.rate_limit.rate_limiter import rate_limit_auth
from app.core.database import get_database

from app.student.schemas import StudentRegisterRequest, StudentResponse
from app.auth.schemas import StudentLoginRequest, LoginResponse, TokenRefreshRequest, TokenRefreshResponse

from app.student.repository import StudentRepository
from app.auth.repository import RefreshTokenRepository

from app.student.service import RegistrationService, ProfileService
from app.auth.service import AuthenticationService, RefreshService, LogoutService
from app.middleware.auth import get_current_user

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication System"]
)

# Repository / Service dependency providers
def get_student_repo() -> StudentRepository:
    return StudentRepository(get_database())

def get_refresh_repo() -> RefreshTokenRepository:
    return RefreshTokenRepository(get_database())

@router.post("/register", response_model=StudentResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(rate_limit_auth)])
async def register(
    request_data: StudentRegisterRequest,
    student_repo: StudentRepository = Depends(get_student_repo)
):
    """
    Registers a new student profile after validating uniqueness of email and roll number.
    """
    service = RegistrationService(student_repo)
    return await service.register_student(request_data)

@router.post("/login", response_model=LoginResponse, dependencies=[Depends(rate_limit_auth)])
async def login(
    request: Request,
    login_data: StudentLoginRequest,
    student_repo: StudentRepository = Depends(get_student_repo),
    refresh_repo: RefreshTokenRepository = Depends(get_refresh_repo)
):
    """
    Authenticates student credentials and generates session access and refresh tokens.
    """
    ip_addr = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    service = AuthenticationService(student_repo, refresh_repo)
    return await service.login_student(
        email=login_data.email,
        password=login_data.password,
        ip=ip_addr,
        device=user_agent
    )

@router.post("/logout")
async def logout(
    logout_data: TokenRefreshRequest,
    refresh_repo: RefreshTokenRepository = Depends(get_refresh_repo)
):
    """
    Revokes the provided refresh token session.
    """
    service = LogoutService(refresh_repo)
    revoked = await service.logout_student(logout_data.refresh_token)
    if not revoked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to logout: token not found or already revoked"
        )
    return {"status": "success", "message": "Session logged out successfully"}

@router.post("/refresh", response_model=TokenRefreshResponse, dependencies=[Depends(rate_limit_auth)])
async def refresh(
    request: Request,
    refresh_data: TokenRefreshRequest,
    student_repo: StudentRepository = Depends(get_student_repo),
    refresh_repo: RefreshTokenRepository = Depends(get_refresh_repo)
):
    """
    Rotates refresh and access tokens for session persistence.
    """
    ip_addr = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    service = RefreshService(student_repo, refresh_repo)
    return await service.refresh_tokens(
        refresh_token=refresh_data.refresh_token,
        ip=ip_addr,
        device=user_agent
    )

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Retrieves the active authenticated user profile (Student or Admin).
    """
    # Simply return the injected current user profile resolved by middleware
    return current_user
