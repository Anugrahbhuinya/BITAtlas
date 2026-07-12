from typing import Tuple

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
        
        # Default configuration
        persona = "bit_mesra_assistant"
        template = intent_lower
        few_shot_limit = 1
        
        if intent_lower == "navigation":
            persona = "campus_navigator"
            few_shot_limit = 1
        elif intent_lower == "academic":
            persona = "academic_tutor"
            few_shot_limit = 2
        elif intent_lower == "attendance":
            persona = "academic_tutor"
            few_shot_limit = 2
        elif intent_lower == "planner":
            persona = "bit_mesra_assistant"
            few_shot_limit = 1
        elif intent_lower == "rag":
            persona = "bit_mesra_assistant"
            few_shot_limit = 1
            
        return persona, template, few_shot_limit
