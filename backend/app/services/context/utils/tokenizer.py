"""
Lightweight token counting utility for the Context Engine.

Uses a character-based approximation (chars / 4) consistent with
the rest of the codebase's token estimation approach.
For production accuracy, swap out estimate_tokens() with tiktoken
or the Gemini tokenizer without changing any callers.
"""


def estimate_tokens(text: str) -> int:
    """
    Estimates the number of tokens in a text string.

    Uses the industry-standard approximation of 4 characters per token,
    consistent with how the rest of this codebase estimates tokens.

    Args:
        text: The text string to estimate.

    Returns:
        Estimated token count (minimum 0).
    """
    if not text:
        return 0
    return max(0, len(text) // 4)


def estimate_tokens_for_sections(sections: dict[str, str]) -> dict[str, int]:
    """
    Estimates token counts for a dictionary of named text sections.

    Args:
        sections: Mapping of section_name → text content.

    Returns:
        Mapping of section_name → estimated_token_count.
    """
    return {name: estimate_tokens(text) for name, text in sections.items()}


def total_tokens(text_parts: list[str]) -> int:
    """
    Estimates the total token count across multiple text strings.

    Args:
        text_parts: List of text strings.

    Returns:
        Sum of estimated token counts.
    """
    return sum(estimate_tokens(part) for part in text_parts if part)
