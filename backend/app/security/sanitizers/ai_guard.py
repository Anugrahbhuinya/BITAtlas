import re
import logging
from fastapi import HTTPException, status
from app.security.config.settings import settings

logger = logging.getLogger("security.ai_guard")

# Compile common injection/jailbreak attack keywords
INJECTION_KEYWORDS = [
    r"ignore\s+(?:all\s+)?previous\s+instructions",
    r"bypass\s+guidelines",
    r"system\s+override",
    r"you\s+are\s+now\s+a",
    r"act\s+as\s+a",
    r"ignore\s+system\s+(?:prompt|rules)",
    r"stop\s+following\s+rules",
    r"forget\s+(?:everything\s+)?you\s+know",
    r"new\s+rule:",
    r"do\s+not\s+follow\s+previous\s+rules"
]

INJECTION_PATTERNS = [re.compile(p, re.IGNORECASE) for p in INJECTION_KEYWORDS]

def validate_chat_query(message: str) -> None:
    """
    Validates user query input against length budgets and prompt injection/jailbreak attempts.
    """
    if not message or not message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chat message cannot be empty"
        )
        
    # Check token budget / request size constraint
    if len(message) > 2000:
        logger.warning(f"Rejected oversized chat message ({len(message)} chars)")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chat message exceeds maximum allowed input size of 2000 characters"
        )
        
    # Scan for injection signatures
    for pattern in INJECTION_PATTERNS:
        if pattern.search(message):
            logger.error(f"Potential prompt injection attack intercepted: '{message[:100]}...'")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Security violation: Potential prompt injection detected."
            )
            
def sanitize_retrieved_context(context_text: str) -> str:
    """
    Sanitizes retrieved RAG content from ChromaDB to prevent indirect prompt injection.
    Strips out directives that look like system prompts.
    """
    if not context_text:
        return ""
        
    # Remove obvious instruction prefixes inside retrieved chunks
    cleaned = context_text
    for pattern in INJECTION_PATTERNS:
        cleaned = pattern.sub("[REDACTED INSTRUCTION]", cleaned)
        
    return cleaned
