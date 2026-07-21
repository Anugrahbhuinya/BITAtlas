import time
from typing import Any
import re
import logging
import threading
from google import genai
from google.genai import types
from app.core.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_TIMEOUT,
    GEMINI_MAX_RETRIES,
    GEMINI_RETRY_DELAY,
    CIRCUIT_BREAKER_COOLDOWN
)

# Configure logger
logger = logging.getLogger("gemini_service")

# Singleton Client instance
_client = None

# Circuit Breaker state
_circuit_state = "CLOSED"
_last_failure_time = 0.0
_consecutive_failures = 0

# Thread local to store retry count
_local_data = threading.local()

def get_client() -> genai.Client:
    """Returns the singleton GenAI client instance."""
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY is not set in configuration!")
            raise ValueError("GEMINI_API_KEY is missing from environment/config")
        logger.info("Initializing singleton Google GenAI client.")
        import httpx
        timeout_config = httpx.Timeout(
            connect=15.0,
            read=float(GEMINI_TIMEOUT),
            write=float(GEMINI_TIMEOUT),
            pool=30.0
        )
        httpx_client = httpx.Client(timeout=timeout_config)
        _client = genai.Client(
            api_key=GEMINI_API_KEY,
            http_options=types.HttpOptions(httpxClient=httpx_client)
        )

    return _client


def get_circuit_breaker_status() -> str:
    """Returns 'CLOSED' or 'OPEN' depending on circuit status and cooldown."""
    global _circuit_state, _last_failure_time
    if _circuit_state == "OPEN":
        if time.time() - _last_failure_time > CIRCUIT_BREAKER_COOLDOWN:
            logger.info("Circuit Breaker cooldown expired. Resetting circuit to CLOSED.")
            reset_circuit_breaker()
            return "CLOSED"
        return "OPEN"
    return "CLOSED"

def is_circuit_closed() -> bool:
    return get_circuit_breaker_status() == "CLOSED"

def record_success():
    global _consecutive_failures, _circuit_state
    _consecutive_failures = 0
    _circuit_state = "CLOSED"

def record_failure(is_quota_exhausted: bool = False):
    global _consecutive_failures, _circuit_state, _last_failure_time
    _last_failure_time = time.time()
    _consecutive_failures += 1
    if is_quota_exhausted or _consecutive_failures >= 3:
        logger.warning(f"Tripping circuit breaker to OPEN. Quota Exhausted: {is_quota_exhausted}, Consecutive Failures: {_consecutive_failures}")
        _circuit_state = "OPEN"

def reset_circuit_breaker():
    global _circuit_state, _last_failure_time, _consecutive_failures
    _circuit_state = "CLOSED"
    _last_failure_time = 0.0
    _consecutive_failures = 0

def get_last_retry_count() -> int:
    return getattr(_local_data, "retry_count", 0)

def _is_quota_error(e: Exception) -> bool:
    err_msg = str(e)
    if hasattr(e, "code") and e.code == 429:
        return True
    if hasattr(e, "status_code") and e.status_code == 429:
        return True
    if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "quota exceeded" in err_msg.lower():
        return True
    return False

def get_last_llm_usage() -> tuple[str, Any]:
    """Retrieve last Gemini call's model name and usage_metadata."""
    return getattr(_local_data, "last_model", ""), getattr(_local_data, "last_usage", None)


def generate_response(prompt: str) -> str:
    """
    Generates a response from Gemini using the configured model.
    Checks circuit breaker before calling Gemini. Supports retries only for transient failures.
    """
    _local_data.retry_count = 0
    _local_data.last_model = ""
    _local_data.last_usage = None
    
    if not is_circuit_closed():
        logger.warning("Circuit Breaker is OPEN. Skipping Gemini call.")
        raise RuntimeError("Circuit Breaker is OPEN: Gemini is currently unavailable")

    max_retries = GEMINI_MAX_RETRIES
    base_delay = GEMINI_RETRY_DELAY
    
    for attempt in range(max_retries + 1):
        try:
            client = get_client()
            model_name = GEMINI_MODEL or "gemini-2.5-flash"
            logger.info(f"Generating content using model: {model_name} (Attempt {attempt + 1}/{max_retries + 1})")
            
            print("\n========== GEMINI SERVICE ==========")
            print(f"Calling Gemini... (Attempt {attempt + 1}/{max_retries + 1})")
            print(f"Prompt Length:\n{len(prompt)}")
            
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=1500,
                    thinking_config=types.ThinkingConfig(thinking_budget=0)
                )
            )



            
            print("Gemini Response Received")
            print("====================================\n")
            
            if response and response.text:
                _local_data.last_model = model_name
                _local_data.last_usage = getattr(response, "usage_metadata", None)
                record_success()
                return response.text.strip()
            else:
                logger.warning("Gemini returned an empty response.")
                raise ValueError("Gemini returned empty response text")
                
        except Exception as e:
            err_msg = str(e)
            is_quota = _is_quota_error(e)
            
            if is_quota:
                logger.error(f"Quota limits exhausted on attempt {attempt + 1}: {err_msg}")
                record_failure(is_quota_exhausted=True)
                raise RuntimeError(f"Gemini API Quota Exhausted: {err_msg}")
                
            if attempt < max_retries:
                _local_data.retry_count += 1
                logger.warning(f"Transient error on attempt {attempt + 1}: {err_msg}. Retrying in {base_delay}s...")
                time.sleep(base_delay)
                continue
            else:
                logger.error(f"Error during Gemini response generation (Final attempt failed): {e}", exc_info=True)
                record_failure(is_quota_exhausted=False)
                raise e
                
    return "I could not find that information in the BITATLAS knowledge base."