"""
Mock implementation for Google GenAI Client and Gemini services.
"""
from __future__ import annotations

import logging
from unittest.mock import MagicMock

logger = logging.getLogger("mock_gemini")


class MockGenerateContentResponse:
    """Mock for the response returned by genai.Client.models.generate_content."""
    def __init__(self, text: str):
        self.text = text


class MockModelsService:
    """Mock for genai.Client.models."""
    def __init__(self):
        self.responses = {
            "mess": "Hostel mess timings are 8:00 AM to 10:00 AM for Breakfast.",
            "library": "The central library is open from 9:00 AM to 9:00 PM.",
            "calendar": "Mid-semester exams start on September 15th, 2026.",
            "default": "Mocked response from Gemini."
        }

    def generate_content(self, model, contents, config=None):
        logger.info(f"Mocked generate_content called with model: {model}, contents: {contents[:100]}...")
        text_lower = contents.lower()
        
        selected_text = self.responses["default"]
        for key, value in self.responses.items():
            if key in text_lower:
                selected_text = value
                break
                
        return MockGenerateContentResponse(selected_text)


class MockGenAIClient:
    """Mock for genai.Client."""
    def __init__(self, api_key=None):
        self.models = MockModelsService()


def patch_gemini_client():
    """Returns a patch context or direct mock for gemini_service._client."""
    mock_client = MockGenAIClient()
    return mock_client
