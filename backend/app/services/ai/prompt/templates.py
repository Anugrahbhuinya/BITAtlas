import os
import logging

logger = logging.getLogger("template_loader")

class TemplateLoader:
    """
    Loads prompt templates from disk based on intent and version.
    Supports fallback paths for development and production environments.
    """
    def __init__(self, base_dirs=None):
        if base_dirs is None:
            # Determine path relative to this file's location: backend/app/services/ai/prompt/templates.py
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up 3 levels to reach backend/app/
            app_dir = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
            # Search order:
            # 1. backend/app/prompts/
            # 2. backend/prompts/
            self.base_dirs = [
                os.path.join(app_dir, "prompts"),
                os.path.join(os.path.dirname(app_dir), "prompts"),
            ]
        else:
            self.base_dirs = base_dirs
        self._cache = {}
        self.hits = 0
        self.misses = 0

    def load_template(self, intent: str, version: str = "v1") -> str:
        """
        Loads the system.txt template for a specific intent and version.
        Falls back to non-versioned directory or hardcoded defaults if not found.
        """
        cache_key = (intent, version)
        if cache_key in self._cache:
            self.hits += 1
            logger.info(f"Template cache hit for intent='{intent}', version='{version}'")
            return self._cache[cache_key]

        self.misses += 1
        for base in self.base_dirs:
            # Try versioned path: base/v1/intent/system.txt
            version_path = os.path.join(base, version, intent, "system.txt")
            if os.path.exists(version_path):
                try:
                    with open(version_path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:
                            logger.info(f"Loaded template from versioned path: {version_path}")
                            self._cache[cache_key] = content
                            return content
                except Exception as e:
                    logger.warning(f"Error reading versioned template at {version_path}: {e}")

            # Try direct path: base/intent/system.txt
            direct_path = os.path.join(base, intent, "system.txt")
            if os.path.exists(direct_path):
                try:
                    with open(direct_path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:
                            logger.info(f"Loaded template from direct path: {direct_path}")
                            self._cache[cache_key] = content
                            return content
                except Exception as e:
                    logger.warning(f"Error reading direct template at {direct_path}: {e}")

        logger.warning(f"Could not find template files for intent '{intent}', version '{version}'. Using fallback.")
        content = self._get_fallback_template(intent)
        self._cache[cache_key] = content
        return content

    def _get_fallback_template(self, intent: str) -> str:
        """
        Hardcoded safe fallback template in case template files are missing on disk.
        """
        return f"""ROLE:
You are BITATLAS.

SYSTEM INSTRUCTIONS:
Help the student with their request concerning {intent}. Rely on the provided context if available.

BEHAVIOR RULES:
1. Be helpful, concise, and professional.

RESTRICTIONS:
1. Never speculate or fabricate information not in the knowledge base.
2. If unsure, state "I could not find that information in the BITATLAS knowledge base."

FORMATTING INSTRUCTIONS:
Format the response clearly for readability.
"""
