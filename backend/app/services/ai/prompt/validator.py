import re
from typing import List, Dict
from app.schemas.prompt_schema import PromptValidationResult

class PromptValidator:
    """
    Validates the assembled prompt against quality and structural rules.
    Checks for empty contents, length, duplicate sections, and missing variables.
    """
    def __init__(self, max_length: int = 15000):
        self.max_length = max_length

    def validate_prompt(self, 
                        final_prompt: str, 
                        sections: Dict[str, str], 
                        template: str, 
                        question: str) -> PromptValidationResult:
        """
        Performs validation checks and returns a PromptValidationResult.
        """
        errors: List[str] = []
        warnings: List[str] = []
        is_valid = True

        # Check: Empty Prompt
        if not final_prompt or not final_prompt.strip():
            errors.append("Assembled prompt is completely empty.")
            is_valid = False

        # Check: Missing User Query
        if not question or not question.strip():
            errors.append("User query is missing or empty.")
            is_valid = False

        # Check: Missing System Prompt
        system_content = sections.get("SYSTEM", "")
        if not system_content or not system_content.strip():
            errors.append("System prompt section is missing or empty.")
            is_valid = False

        # Check: Invalid / Empty Templates
        if not template or not template.strip():
            warnings.append("The loaded prompt template is empty.")

        # Check: Missing/Unresolved Variables
        # Searches for unresolved double brace markers like {{name}}
        placeholder_pattern = r"\{\{\s*[a-zA-Z0-9_-]+\s*\}\}"
        unresolved_vars = re.findall(placeholder_pattern, final_prompt)
        if unresolved_vars:
            warnings.append(f"Prompt contains unresolved placeholders: {list(set(unresolved_vars))}")

        # Check: Duplicate Sections
        section_headers = [
            "SYSTEM", "PERSONA", "SAFETY", "CURRENT DATE", "STUDENT PROFILE",
            "CONVERSATION SUMMARY", "CURRENT CONTEXT", "RETRIEVED KNOWLEDGE",
            "FEW SHOT EXAMPLES", "TOOL", "OUTPUT FORMAT", "USER QUESTION"
        ]
        for header in section_headers:
            header_marker = f"=== {header} ==="
            occurrences = final_prompt.count(header_marker)
            if occurrences > 1:
                warnings.append(f"Section header '{header}' occurs {occurrences} times in the prompt.")

        # Check: Prompt Length
        prompt_len = len(final_prompt)
        if prompt_len > self.max_length:
            warnings.append(f"Prompt length of {prompt_len} characters exceeds limit of {self.max_length} characters.")

        if errors:
            is_valid = False

        return PromptValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings
        )
