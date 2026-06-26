import time
import re
from google import genai
import logging
from app.core.config import GEMINI_API_KEY, GEMINI_MODEL

# Configure logger
logger = logging.getLogger("gemini_service")

# Singleton Client instance
_client = None

def get_client() -> genai.Client:
    """Returns the singleton GenAI client instance."""
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY is not set in configuration!")
            raise ValueError("GEMINI_API_KEY is missing from environment/config")
        logger.info("Initializing singleton Google GenAI client.")
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client

def generate_response(prompt: str) -> str:
    """
    Generates a response from Gemini using the configured model.
    Falls back to a safe message on error. Supports retries on 429 rate limit errors.
    """
    max_retries = 3
    base_delay = 10
    
    for attempt in range(max_retries):
        try:
            client = get_client()
            model_name = GEMINI_MODEL or "gemini-2.5-flash"
            logger.info(f"Generating content using model: {model_name} (Attempt {attempt + 1}/{max_retries})")
            
            print("\n========== GEMINI SERVICE ==========")
            print(f"Calling Gemini... (Attempt {attempt + 1}/{max_retries})")
            print(f"Prompt Length:\n{len(prompt)}")
            
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            
            print("Gemini Response Received")
            print("====================================\n")
            
            if response and response.text:
                return response.text.strip()
            else:
                logger.warning("Gemini returned an empty response.")
                return "I could not find that information in the BIT Mesra knowledge base."
                
        except Exception as e:
            err_msg = str(e)
            is_rate_limit = False
            
            # Check for 429 status code or rate limit messages
            if hasattr(e, "code") and e.code == 429:
                is_rate_limit = True
            elif hasattr(e, "status_code") and e.status_code == 429:
                is_rate_limit = True
            elif "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "quota exceeded" in err_msg.lower():
                is_rate_limit = True
                
            if is_rate_limit and attempt < max_retries - 1:
                # Extract wait time if present, e.g. "Please retry in 20.107336386s."
                wait_time = base_delay * (2 ** attempt)
                match = re.search(r"Please retry in ([\d\.]+)s", err_msg)
                if match:
                    try:
                        wait_time = float(match.group(1)) + 1.0  # Add 1s buffer
                    except ValueError:
                        pass
                
                logger.warning(f"Rate limited (429) by Gemini API. Waiting {wait_time:.2f} seconds before retry...")
                print(f"Rate limited (429). Retrying in {wait_time:.2f}s...")
                time.sleep(wait_time)
                continue
            else:
                logger.error(f"Error during Gemini response generation (Final attempt failed): {e}", exc_info=True)
                raise e
                
    return "I could not find that information in the BIT Mesra knowledge base."