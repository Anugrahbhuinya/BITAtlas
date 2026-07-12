from app.core.prompt_config import SAFETY_INSTRUCTIONS

class HallucinationGuard:
    """
    Injects strict negative constraints and behavior rules to prevent the LLM
    from hallucinating data that is not present in the retrieved context.
    """
    def __init__(self):
        pass

    def get_guard_instructions(self) -> str:
        """
        Returns a structured instruction string containing strict hallucination controls.
        """
        return SAFETY_INSTRUCTIONS
