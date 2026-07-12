import hashlib
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status
from app.auth.repository import RefreshTokenRepository
from app.student.repository import StudentRepository
from app.auth.jwt_service import JWTService
from app.auth.password_service import PasswordService

def hash_token(token: str) -> str:
    """
    Computes SHA-256 hash of a string token to avoid storing plaintext in database.
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

class AuthenticationService:
    def __init__(self, student_repo: StudentRepository, refresh_repo: RefreshTokenRepository):
        self.student_repo = student_repo
        self.refresh_repo = refresh_repo

    async def login_student(self, email: str, password: str, ip: str | None = None, device: str | None = None) -> dict:
        """
        Validates credentials, checks status, and issues access/refresh tokens.
        """
        student = await self.student_repo.get_by_email(email)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if student.get("status") != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is inactive. Please contact administration."
            )

        # Verify password using bcrypt
        if not PasswordService.verify_password(password, student.get("password_hash", "")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        student_id = str(student["_id"])
        
        # Generate new JWTs
        access_token = JWTService.create_access_token(student_id, role="student")
        refresh_token = JWTService.create_refresh_token(student_id, role="student")

        # Save hashed refresh token to Mongo
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        token_data = {
            "token_hash": hash_token(refresh_token),
            "user_id": student_id,
            "role": "student",
            "expires_at": expires_at,
            "created_at": datetime.now(timezone.utc),
            "ip": ip,
            "device": device
        }
        await self.refresh_repo.create(token_data)

        # Clean student doc to return
        user_profile = student.copy()
        user_profile["_id"] = student_id
        if "password_hash" in user_profile:
            del user_profile["password_hash"]

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user_profile
        }

class RefreshService:
    def __init__(self, student_repo: StudentRepository, refresh_repo: RefreshTokenRepository):
        self.student_repo = student_repo
        self.refresh_repo = refresh_repo

    async def refresh_tokens(self, refresh_token: str, ip: str | None = None, device: str | None = None) -> dict:
        """
        Validates refresh token, rotates session (invalidating old refresh token), and issues new ones.
        """
        try:
            payload = JWTService.decode_token(refresh_token, expected_type="refresh")
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            user_id = payload.get("sub")
            role = payload.get("role")
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )

        # Check DB to verify token is not revoked/already rotated
        token_hash = hash_token(refresh_token)
        stored_token = await self.refresh_repo.get_by_hash(token_hash)
        if not stored_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is invalid or has been revoked"
            )

        # Verify database expiration
        expires_at = stored_token["expires_at"]
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
            
        if datetime.now(timezone.utc) > expires_at:
            await self.refresh_repo.revoke(token_hash)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired"
            )

        # Revoke/Delete old refresh token (enforce rotation)
        await self.refresh_repo.revoke(token_hash)

        # Issue new access/refresh pair
        new_access_token = JWTService.create_access_token(user_id, role=role)
        new_refresh_token = JWTService.create_refresh_token(user_id, role=role)

        # Save new hashed refresh token
        new_expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        new_token_data = {
            "token_hash": hash_token(new_refresh_token),
            "user_id": user_id,
            "role": role,
            "expires_at": new_expires_at,
            "created_at": datetime.now(timezone.utc),
            "ip": ip,
            "device": device
        }
        await self.refresh_repo.create(new_token_data)

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token
        }

class LogoutService:
    def __init__(self, refresh_repo: RefreshTokenRepository):
        self.refresh_repo = refresh_repo

    async def logout_student(self, refresh_token: str) -> bool:
        """
        Revokes a specific active refresh token session.
        """
        token_hash = hash_token(refresh_token)
        return await self.refresh_repo.revoke(token_hash)
