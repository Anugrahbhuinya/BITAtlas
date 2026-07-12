"""
Ranking utility helpers for the Context Engine prioritizer.

Provides score normalization and ordering utilities used when
sorting ProviderResults before merging.
"""
from __future__ import annotations

from typing import List, Tuple


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    """
    Clamps a float value to the [low, high] range.

    Args:
        value: Input value.
        low:   Minimum bound (default 0.0).
        high:  Maximum bound (default 1.0).

    Returns:
        Clamped value.
    """
    return max(low, min(high, value))


def normalize_scores(scores: List[float]) -> List[float]:
    """
    Min-max normalizes a list of scores to the [0.0, 1.0] range.

    If all scores are equal, returns a list of 1.0 (full weight for all).

    Args:
        scores: List of raw priority scores.

    Returns:
        Normalized scores in [0.0, 1.0].
    """
    if not scores:
        return []
    min_s = min(scores)
    max_s = max(scores)
    if max_s == min_s:
        return [1.0] * len(scores)
    return [(s - min_s) / (max_s - min_s) for s in scores]


def ranked_indices(scores: List[float], descending: bool = True) -> List[int]:
    """
    Returns the indices that would sort the scores list.

    Args:
        scores:     List of numeric scores.
        descending: If True, highest score = first index.

    Returns:
        List of integer indices in sorted order.
    """
    indexed: List[Tuple[float, int]] = [(s, i) for i, s in enumerate(scores)]
    indexed.sort(key=lambda x: x[0], reverse=descending)
    return [i for _, i in indexed]


def freshness_factor(age_seconds: float, decay_half_life: float = 300.0) -> float:
    """
    Computes a freshness factor using exponential decay.

    Newer content scores closer to 1.0; older content decays toward 0.0.

    Args:
        age_seconds:      Age of the content in seconds.
        decay_half_life:  Half-life for decay (default 5 minutes).

    Returns:
        Freshness score in (0.0, 1.0].
    """
    import math
    if age_seconds <= 0:
        return 1.0
    return math.exp(-age_seconds * math.log(2) / decay_half_life)
