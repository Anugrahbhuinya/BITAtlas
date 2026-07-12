import os
from app.security.config.settings import settings

# Load profile values to preserve compatibility with all existing modules
MONGO_URI = settings.MONGO_URI
MONGO_DB = settings.MONGO_DB
GEMINI_API_KEY = settings.GEMINI_API_KEY
GEMINI_MODEL = settings.GEMINI_MODEL

# Website Ingestion Configurations
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))
MAX_PAGE_SIZE = int(os.getenv("MAX_PAGE_SIZE", "5242880"))
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
MAX_CHUNKS = int(os.getenv("MAX_CHUNKS", "500"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# Website Synchronization Configurations
WEBSITE_SYNC_ENABLED = os.getenv("WEBSITE_SYNC_ENABLED", "True").lower() == "true"
WEBSITE_SYNC_INTERVAL_MINUTES = int(os.getenv("WEBSITE_SYNC_INTERVAL_MINUTES", "60"))
MAX_CONCURRENT_WEBSITE_SYNCS = int(os.getenv("MAX_CONCURRENT_WEBSITE_SYNCS", "3"))
RESPECT_ROBOTS_TXT = os.getenv("RESPECT_ROBOTS_TXT", "False").lower() == "true"

# Website Content Normalization Configurations
ENABLE_NORMALIZED_HASH = os.getenv("ENABLE_NORMALIZED_HASH", "True").lower() == "true"
IGNORE_DATES = os.getenv("IGNORE_DATES", "True").lower() == "true"
IGNORE_TIMESTAMPS = os.getenv("IGNORE_TIMESTAMPS", "True").lower() == "true"
IGNORE_COUNTERS = os.getenv("IGNORE_COUNTERS", "True").lower() == "true"
IGNORE_SESSION_IDS = os.getenv("IGNORE_SESSION_IDS", "True").lower() == "true"
IGNORE_EXTRA_WHITESPACE = os.getenv("IGNORE_EXTRA_WHITESPACE", "True").lower() == "true"

# Prompt Pipeline Configuration
ENABLE_PROMPT_PIPELINE = os.getenv("ENABLE_PROMPT_PIPELINE", "False").lower() == "true"
ENABLE_NAVIGATION_DEBUG = os.getenv("ENABLE_NAVIGATION_DEBUG", "False").lower() == "true"
IS_DEV_MODE = settings.DEBUG

# AI Pipeline Performance & Reliability Configurations
GEMINI_TIMEOUT = settings.GEMINI_TIMEOUT
GEMINI_MAX_RETRIES = settings.GEMINI_MAX_RETRIES
GEMINI_RETRY_DELAY = settings.GEMINI_RETRY_DELAY
CIRCUIT_BREAKER_COOLDOWN = settings.CIRCUIT_BREAKER_COOLDOWN
MAX_PROMPT_SIZE = settings.MAX_PROMPT_SIZE
CACHE_TTL = settings.CACHE_TTL
ROUTING_CONFIDENCE_THRESHOLD = settings.ROUTING_CONFIDENCE_THRESHOLD
DEBUG_RAG = settings.DEBUG_RAG

# KMS Configurations
KNOWLEDGE_MAX_FILE_SIZE = int(os.getenv("KNOWLEDGE_MAX_FILE_SIZE", str(10 * 1024 * 1024)))
KNOWLEDGE_EXPIRY_CHECK_ENABLED = os.getenv("KNOWLEDGE_EXPIRY_CHECK_ENABLED", "True").lower() == "true"