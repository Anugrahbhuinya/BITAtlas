"""
Base provider helpers for the Context Engine.

Provides factory functions for constructing standardized
ProviderResult objects, reducing boilerplate in each provider.
"""
from __future__ import annotations

import time
from typing import List, Optional

from app.services.context.models import (
    ContextItem,
    ContextSection,
    ProviderMetadata,
    ProviderResult,
    ProviderStatus,
)
from app.services.context.utils.tokenizer import estimate_tokens


def build_provider_result(
    provider_id: str,
    section_name: str,
    items: List[ContextItem],
    confidence: float = 1.0,
    priority_weight: float = 0.0,
    execution_time_s: float = 0.0,
    section_metadata: Optional[dict] = None,
) -> ProviderResult:
    """
    Constructs a successful ProviderResult from a list of ContextItems.

    Args:
        provider_id:      Unique identifier for the provider.
        section_name:     Name of the context section being produced.
        items:            List of ContextItem objects.
        confidence:       Provider confidence score (0.0–1.0).
        priority_weight:  Base priority weight of this provider.
        execution_time_s: How long the provider took to execute.
        section_metadata: Optional additional metadata for the section.

    Returns:
        A ProviderResult with status=SUCCESS.
    """
    # Compute token counts per item
    for item in items:
        if item.token_count == 0 and item.content:
            item.token_count = estimate_tokens(item.content)

    total_tokens = sum(item.token_count for item in items)

    section = ContextSection(
        name=section_name,
        provider_id=provider_id,
        items=items,
        total_tokens=total_tokens,
        metadata=section_metadata or {},
    )

    metadata = ProviderMetadata(
        provider_id=provider_id,
        status=ProviderStatus.SUCCESS,
        execution_time_s=execution_time_s,
        confidence=confidence,
        priority_weight=priority_weight,
    )

    return ProviderResult(metadata=metadata, section=section)


def FailedProviderResult(
    provider_id: str,
    priority_weight: float,
    error_detail: str,
    execution_time_s: float = 0.0,
) -> ProviderResult:
    """
    Constructs a failed ProviderResult.

    Args:
        provider_id:      Unique identifier for the provider.
        priority_weight:  Base priority weight of this provider.
        error_detail:     Description of the failure.
        execution_time_s: How long the provider ran before failing.

    Returns:
        A ProviderResult with status=FAILED and no section.
    """
    metadata = ProviderMetadata(
        provider_id=provider_id,
        status=ProviderStatus.FAILED,
        execution_time_s=execution_time_s,
        confidence=0.0,
        priority_weight=priority_weight,
        error_detail=error_detail,
    )
    return ProviderResult(metadata=metadata, section=None)


def SkippedProviderResult(
    provider_id: str,
    priority_weight: float,
    reason: str,
) -> ProviderResult:
    """
    Constructs a skipped ProviderResult.

    Args:
        provider_id:    Unique identifier for the provider.
        priority_weight: Base priority weight of this provider.
        reason:         Why this provider was skipped.

    Returns:
        A ProviderResult with status=SKIPPED and no section.
    """
    metadata = ProviderMetadata(
        provider_id=provider_id,
        status=ProviderStatus.SKIPPED,
        execution_time_s=0.0,
        confidence=0.0,
        priority_weight=priority_weight,
        skip_reason=reason,
    )
    return ProviderResult(metadata=metadata, section=None)
