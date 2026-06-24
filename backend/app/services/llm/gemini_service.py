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
    Falls back to a safe message on error.
    """
    try:
        client = get_client()
        model_name = GEMINI_MODEL or "gemini-2.5-flash"
        logger.info(f"Generating content using model: {model_name}")
        
        print("\n========== GEMINI SERVICE ==========")
        print("Calling Gemini...")
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
        logger.error(f"Error during Gemini response generation: {e}", exc_info=True)
        return "I could not find that information in the BIT Mesra knowledge base."