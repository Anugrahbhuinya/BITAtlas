"""
Context Prioritizer.

Computes weighted priority scores for ProviderResults and returns
them in descending priority order. The Merger uses this ordering
to produce a well-structured ContextPackage.

Priority formula:
    score = (routing_confidence × w_routing)
          + (provider_confidence × w_provider)
          + (freshness_factor × w_freshness)
          + (source_reliability × w_reliability)

All weights are configurable via context_config.
"""
from __future__ import annotations

import logging
import time
from typing import List, Tuple

from app.services.context.configs.context_config import (
    PRIORITY_W_FRESHNESS,
    PRIORITY_W_PROVIDER,
    PRIORITY_W_RELIABILITY,
    PRIORITY_W_ROUTING,
    SOURCE_RELIABILITY,
)
from app.services.context.models import ProviderResult, ProviderStatus
from app.services.context.utils.ranking import clamp, freshness_factor

logger = logging.getLogger("context.prioritizer")


class ContextPrioritizer:
    """
    Assigns weighted priority scores to ProviderResults and returns
    them sorted highest → lowest priority.

    Only results with status=SUCCESS are scored; FAILED/SKIPPED
    results are excluded from the output list.
    """

    def prioritize(
        self,
        results: List[ProviderResult],
        routing_confidence: float = 1.0,
        request_timestamp: float = 0.0,
    ) -> List[Tuple[float, ProviderResult]]:
        """
        Scores and sorts ProviderResults by computed priority.

        Args:
            results:            List of raw ProviderResult objects from pipeline.
            routing_confidence: Confidence from RoutingDecision (0.0–1.0).
            request_timestamp:  Unix timestamp of the original request (for freshness).

        Returns:
            List of (score, ProviderResult) tuples sorted descending by score.
            Only includes results with status=SUCCESS.
        """
        scored: List[Tuple[float, ProviderResult]] = []
        now = time.time()

        for result in results:
            if result.metadata.status != ProviderStatus.SUCCESS:
                logger.debug(
                    "Skipping prioritization for %s (status=%s)",
                    result.metadata.provider_id,
                    result.metadata.status,
                )
                continue

            score = self._compute_score(result, routing_confidence, now, request_timestamp)
            result.metadata.confidence = clamp(result.metadata.confidence)

            # Annotate each item with the computed priority
            if result.section:
                for item in result.section.items:
                    item.priority = score

            scored.append((score, result))
            logger.debug(
                "Provider %s → priority_score=%.4f",
                result.metadata.provider_id,
                score,
            )

        # Sort descending by score
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored

    def _compute_score(
        self,
        result: ProviderResult,
        routing_confidence: float,
        now: float,
        request_timestamp: float,
    ) -> float:
        """
        Computes the weighted priority score for a single ProviderResult.

        Args:
            result:             The ProviderResult to score.
            routing_confidence: Global routing confidence.
            now:                Current unix timestamp.
            request_timestamp:  Request start unix timestamp (0 = unknown).

        Returns:
            Priority score in [0.0, 1.0].
        """
        provider_id = result.metadata.provider_id

        # Component 1: routing confidence
        c_routing = clamp(routing_confidence) * PRIORITY_W_ROUTING

        # Component 2: provider self-assessed confidence
        c_provider = clamp(result.metadata.confidence) * PRIORITY_W_PROVIDER

        # Component 3: freshness (lower age = fresher = higher score)
        age_s = (now - request_timestamp) if request_timestamp > 0 else 0.0
        # Execution time acts as a freshness proxy — faster providers
        # were likely more cache-friendly / higher priority
        exec_age = result.metadata.execution_time_s
        c_freshness = freshness_factor(exec_age, decay_half_life=5.0) * PRIORITY_W_FRESHNESS

        # Component 4: source reliability
        reliability = SOURCE_RELIABILITY.get(provider_id, 0.70)
        c_reliability = clamp(reliability) * PRIORITY_W_RELIABILITY

        # Base weight boost
        base = result.metadata.priority_weight  # provider's baseline

        raw_score = (c_routing + c_provider + c_freshness + c_reliability) * base
        return clamp(raw_score)

    def get_scores_dict(
        self,
        scored: List[Tuple[float, ProviderResult]],
    ) -> dict:
        """
        Returns a provider_id → score mapping for diagnostics.

        Args:
            scored: Output of prioritize().

        Returns:
            Dict mapping provider_id → priority score.
        """
        return {result.metadata.provider_id: score for score, result in scored}
