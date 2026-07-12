"""
Context Deduplicator.

Removes exact and near-duplicate context items from ProviderResults
before merging. Citations are ALWAYS preserved — items with unique
citations are never removed even if content overlaps significantly.

Deduplication operates at the ContextItem level within ProviderResults.
"""
from __future__ import annotations

import logging
from typing import List, Set, Tuple

from app.services.context.configs.context_config import (
    DEDUP_EXACT_ENABLED,
    DEDUP_NEAR_ENABLED,
    DEDUP_SIMILARITY_THRESHOLD,
)
from app.services.context.models import ContextItem, ProviderResult
from app.services.context.utils.similarity import content_hash, is_near_duplicate

logger = logging.getLogger("context.deduplicator")


class ContextDeduplicator:
    """
    Removes duplicate context items while preserving citations.

    Two-pass deduplication:
    1. Exact: Items with identical normalized content (hash-based) are removed.
    2. Near: Items above the Jaccard similarity threshold are removed,
             UNLESS they carry unique citations.

    The highest-priority item is kept when duplicates are found.
    """

    def deduplicate(
        self,
        results: List[ProviderResult],
    ) -> Tuple[List[ProviderResult], int]:
        """
        Deduplicates context items across all ProviderResults.

        Modifies the sections in-place (items list is filtered).

        Args:
            results: List of ProviderResult objects (already prioritized).

        Returns:
            Tuple of (deduplicated results, total duplicate count removed).
        """
        seen_hashes: Set[str] = set()
        seen_texts: List[str] = []  # for near-duplicate comparison
        total_removed = 0

        for result in results:
            if result.section is None:
                continue

            filtered_items: List[ContextItem] = []

            for item in result.section.items:
                if not item.content.strip():
                    total_removed += 1
                    continue

                # --- Pass 1: Exact duplicate removal ---
                if DEDUP_EXACT_ENABLED:
                    h = content_hash(item.content)
                    if h in seen_hashes:
                        logger.debug(
                            "Exact duplicate removed from %s: %.40s…",
                            result.metadata.provider_id,
                            item.content,
                        )
                        total_removed += 1
                        continue
                    seen_hashes.add(h)

                # --- Pass 2: Near-duplicate removal ---
                if DEDUP_NEAR_ENABLED:
                    is_dup = False
                    for existing_text in seen_texts:
                        if is_near_duplicate(
                            item.content, existing_text, DEDUP_SIMILARITY_THRESHOLD
                        ):
                            # Only remove if no unique citation
                            if not item.citation:
                                logger.debug(
                                    "Near-duplicate removed from %s (threshold=%.2f): %.40s…",
                                    result.metadata.provider_id,
                                    DEDUP_SIMILARITY_THRESHOLD,
                                    item.content,
                                )
                                total_removed += 1
                                is_dup = True
                                break
                            else:
                                logger.debug(
                                    "Near-duplicate RETAINED due to unique citation: %s",
                                    item.citation,
                                )
                    if is_dup:
                        continue

                seen_texts.append(item.content)
                filtered_items.append(item)

            removed_from_section = len(result.section.items) - len(filtered_items)
            if removed_from_section:
                logger.info(
                    "Deduplicator: %d item(s) removed from section '%s'",
                    removed_from_section,
                    result.section.name,
                )

            # Update section with filtered items and recalculate token count
            result.section.items = filtered_items
            result.section.total_tokens = sum(i.token_count for i in filtered_items)

        logger.info("Deduplication complete. Total removed: %d", total_removed)
        return results, total_removed
