def format_response(
    response: str,
    source: str
):

    icons = {
        "building": "📍",
        "hostel": "🏠",
        "facility": "🏥",
        "calendar": "📅",
        "notice": "📢",
        "department": "🎓",
        "club": "🎭",
        "faq": "❓"
    }

    icon = icons.get(source, "ℹ️")

    return f"{icon} {response}"

import re

def clean_gemini_response(text: str) -> str:
    """
    Cleans the Gemini response output by removing extra whitespace,
    standardizing newlines, and making sure the response is user-friendly.
    """
    if not text:
        return ""
    
    # Trim leading and trailing whitespace
    text = text.strip()
    
    # Normalize multiple newlines (max 2 consecutive newlines)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text