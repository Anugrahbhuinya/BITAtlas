from typing import Dict
from app.core.prompt_config import FORMATTING_RULES

class ResponseFormatter:
    """
    Automatically injects structured markdown layout instructions into the prompt
    based on the active intent, guaranteeing standard response sections in the UI.
    """
    def __init__(self):
        self.formats: Dict[str, str] = FORMATTING_RULES

    def get_formatting_instructions(self, intent: str) -> str:
        """
        Retrieves the exact markdown formatting template for the selected intent.
        Defaults to the 'general' intent format.
        """
        intent_key = intent.lower()
        if intent_key == "rag":
            # RAG uses academic structure by default
            intent_key = "academic"
            
        return self.formats.get(intent_key, self.formats.get("general", ""))
