import os
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

# Ensure compatibility with core config
SECRET_KEY = os.getenv("JWT_SECRET", "bit_mesra_admin_secret_key_2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 7       # 7 days

class JWTService:
    @staticmethod
    def create_access_token(subject: str, role: str, expires_delta: Optional[timedelta] = None) -> str:
        """
        Generates a secure access JWT signed with HS256.
        """
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        payload = {
            "sub": subject,
            "role": role,
            "type": "access",
            "exp": expire
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def create_refresh_token(subject: str, role: str, expires_delta: Optional[timedelta] = None) -> str:
        """
        Generates a secure refresh JWT signed with HS256.
        """
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
        payload = {
            "sub": subject,
            "role": role,
            "type": "refresh",
            "exp": expire
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def decode_token(token: str, expected_type: str = "access") -> Dict[str, Any]:
        """
        Decodes a JWT and validates signature/expiration.
        Checks for missing claims (sub, role, type) and type match.
        """
        # pyjwt will raise ExpiredSignatureError or PyJWTError automatically
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if not payload.get("sub"):
            raise jwt.PyJWTError("Token is missing subject claim")
        if not payload.get("role"):
            raise jwt.PyJWTError("Token is missing role claim")
            
        # Verify type matching
        token_type = payload.get("type", "access")
        if token_type != expected_type:
            raise jwt.PyJWTError(f"Invalid token type: expected {expected_type}, got {token_type}")
            
        return payload
