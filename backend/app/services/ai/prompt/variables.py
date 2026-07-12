import re
from datetime import datetime
from typing import Dict, Any

class VariableEngine:
    """
    Replaces template placeholders like {{student_name}} with actual context values.
    """
    def __init__(self):
        pass

    def inject_variables(self, text: str, context_vars: Dict[str, Any]) -> str:
        """
        Scans text for {{placeholder}} tokens and replaces them with values from context_vars.
        Automatically supplies dynamic defaults (e.g. today) if missing.
        """
        if not text:
            return ""

        # Normalize key names to lowercase for robust matching
        normalized_vars: Dict[str, str] = {}
        for key, val in context_vars.items():
            if val is not None:
                normalized_vars[key.lower()] = str(val)
            else:
                normalized_vars[key.lower()] = ""

        # Ensure 'today' variable is set
        if "today" not in normalized_vars or not normalized_vars["today"]:
            normalized_vars["today"] = datetime.now().strftime("%Y-%m-%d")

        # RegEx to find {{ placeholder_name }}
        pattern = r"\{\{\s*([a-zA-Z0-9_-]+)\s*\}\}"

        def replacer(match: re.Match) -> str:
            var_name = match.group(1).strip().lower()
            # If the variable exists in our context, replace it; otherwise, leave empty
            return normalized_vars.get(var_name, "")

        return re.sub(pattern, replacer, text)
