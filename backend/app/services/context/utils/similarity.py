"""
Text similarity utilities for the Context Engine deduplicator.

Provides lightweight, dependency-free similarity measures suitable
for near-duplicate detection on short-to-medium text blocks.
No external ML models are required.
"""
from __future__ import annotations

import re
from typing import Set


def normalize_text(text: str) -> str:
    """
    Normalizes text for comparison by lowercasing, collapsing whitespace,
    and stripping punctuation.

    Args:
        text: Raw text string.

    Returns:
        Normalized text suitable for similarity comparison.
    """
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _word_set(text: str) -> Set[str]:
    """Returns the set of unique words in normalized text."""
    return set(normalize_text(text).split())


def jaccard_similarity(text_a: str, text_b: str) -> float:
    """
    Computes Jaccard similarity between two text strings.

    Jaccard(A, B) = |A ∩ B| / |A ∪ B|

    Range: 0.0 (completely different) to 1.0 (identical word sets).
    Empty strings are considered identical (returns 1.0).

    Args:
        text_a: First text string.
        text_b: Second text string.

    Returns:
        Jaccard similarity score in [0.0, 1.0].
    """
    if not text_a and not text_b:
        return 1.0
    if not text_a or not text_b:
        return 0.0

    set_a = _word_set(text_a)
    set_b = _word_set(text_b)

    if not set_a and not set_b:
        return 1.0

    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def is_near_duplicate(text_a: str, text_b: str, threshold: float = 0.85) -> bool:
    """
    Returns True if two texts are near-duplicates according to Jaccard similarity.

    Args:
        text_a:    First text string.
        text_b:    Second text string.
        threshold: Similarity threshold above which texts are considered duplicates.

    Returns:
        True if similarity >= threshold.
    """
    return jaccard_similarity(text_a, text_b) >= threshold


def content_hash(text: str) -> str:
    """
    Returns a stable hash for exact deduplication of context items.

    Uses normalized text to avoid false negatives from whitespace differences.

    Args:
        text: Raw text content.

    Returns:
        Hex digest string.
    """
    import hashlib
    normalized = normalize_text(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
