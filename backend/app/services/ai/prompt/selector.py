from typing import Tuple
from app.core.prompt_config import TEMPLATE_IDENTIFIERS, DEFAULT_PERSONA

class PromptSelector:
    """
    Decides which Persona, Template, and Few-Shot count should be applied
    for a given student query intent.
    """
    def __init__(self):
        pass

    def select_config(self, intent: str) -> Tuple[str, str, int]:
        """
        Given an intent, returns a tuple of:
        (persona_name, template_name, few_shot_limit)
        """
        intent_lower = intent.lower()
        
        # Load from centralized configuration mapping
        if intent_lower in TEMPLATE_IDENTIFIERS:
            return TEMPLATE_IDENTIFIERS[intent_lower]
            
        # Default configuration fallback
        return DEFAULT_PERSONA, intent_lower, 1
