import os
from typing import List
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

class BaseSecuritySettings:
    """
    Base configuration options for application security and hardening parameters.
    """
    # Environment mode
    ENV: str = os.getenv("APP_ENV", "development").lower()
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Core Server configuration
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8001"))
    API_PREFIX: str = os.getenv("API_PREFIX", "/api")
    
    # Secrets
    JWT_SECRET: str = os.getenv("JWT_SECRET", "bit_mesra_admin_secret_key_2026")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")) # 24 hours
    
    # CORS & Network Boundaries
    ALLOWED_HOSTS: List[str] = [x.strip() for x in os.getenv("ALLOWED_HOSTS", "*").split(",") if x.strip()]
    CORS_ORIGINS: List[str] = []
    SECURE_HEADERS_ENABLED: bool = True
    
    # MongoDB & ChromaDB Connections
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB: str = os.getenv("MONGO_DB", "bit_mesra_db")
    
    # Vector DB Path
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "chroma_db"))
    
    # Gemini configurations
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    GEMINI_TIMEOUT: float = float(os.getenv("GEMINI_TIMEOUT", "10.0"))
    GEMINI_MAX_RETRIES: int = int(os.getenv("GEMINI_MAX_RETRIES", "1"))
    GEMINI_RETRY_DELAY: float = float(os.getenv("GEMINI_RETRY_DELAY", "1.0"))
    
    # Reliability Settings
    CIRCUIT_BREAKER_COOLDOWN: float = float(os.getenv("CIRCUIT_BREAKER_COOLDOWN", "30.0"))
    CACHE_TTL: float = float(os.getenv("CACHE_TTL", "300.0"))
    
    # Input Constraints & Resource Protection
    MAX_CONTENT_LENGTH: int = int(os.getenv("MAX_CONTENT_LENGTH", "5242880")) # 5MB payload limit
    MAX_PROMPT_SIZE: int = int(os.getenv("MAX_PROMPT_SIZE", "5000"))
    ROUTING_CONFIDENCE_THRESHOLD: float = float(os.getenv("ROUTING_CONFIDENCE_THRESHOLD", "0.45"))
    DEBUG_RAG: bool = os.getenv("DEBUG_RAG", "False").lower() == "true"
    
    # Rate Limiting configuration
    RATE_LIMIT_CHAT_LIMIT: int = int(os.getenv("RATE_LIMIT_CHAT_LIMIT", "20"))
    RATE_LIMIT_CHAT_WINDOW: int = int(os.getenv("RATE_LIMIT_CHAT_WINDOW", "60"))
    RATE_LIMIT_ADMIN_LIMIT: int = int(os.getenv("RATE_LIMIT_ADMIN_LIMIT", "10"))
    RATE_LIMIT_ADMIN_WINDOW: int = int(os.getenv("RATE_LIMIT_ADMIN_WINDOW", "60"))
    
    # Logging & Monitoring
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    STRUCTURED_LOGGING: bool = os.getenv("STRUCTURED_LOGGING", "True").lower() == "true"

    def _parse_origins(self) -> List[str]:
        raw_origins = os.getenv("CORS_ORIGINS", "")
        return [x.strip() for x in raw_origins.split(",") if x.strip() and x.strip() != "*"]

class DevelopmentSettings(BaseSecuritySettings):
    ENV: str = "development"
    DEBUG: bool = True
    SECURE_HEADERS_ENABLED: bool = False
    
    def __init__(self):
        self.CORS_ORIGINS = self._parse_origins()
        dev_origins = ["http://localhost:5180", "http://127.0.0.1:5180"]
        for o in dev_origins:
            if o not in self.CORS_ORIGINS:
                self.CORS_ORIGINS.append(o)

class TestingSettings(BaseSecuritySettings):
    ENV: str = "testing"
    DEBUG: bool = True
    MONGO_DB: str = "bit_mesra_test_db"
    SECURE_HEADERS_ENABLED: bool = False
    RATE_LIMIT_CHAT_LIMIT: int = 999999 # effectively bypass in tests
    RATE_LIMIT_ADMIN_LIMIT: int = 999999
    
    def __init__(self):
        self.CORS_ORIGINS = self._parse_origins()
        dev_origins = ["http://localhost:5180", "http://127.0.0.1:5180"]
        for o in dev_origins:
            if o not in self.CORS_ORIGINS:
                self.CORS_ORIGINS.append(o)

class ProductionSettings(BaseSecuritySettings):
    ENV: str = "production"
    DEBUG: bool = False
    SECURE_HEADERS_ENABLED: bool = True
    
    def __init__(self):
        self.CORS_ORIGINS = self._parse_origins()

def get_settings() -> BaseSecuritySettings:
    """
    Factory helper returning active configuration profile based on APP_ENV.
    """
    env = os.getenv("APP_ENV", "development").lower()
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    return DevelopmentSettings()

settings = get_settings()
