"""
Context Merger.

Merges prioritized, deduplicated ProviderResults into a single
ContextPackage with well-ordered sections.

Section order is canonical:
  system → profile → conversation → workspace → navigation → rag

Each section preserves its metadata and source provider ID.
"""
from __future__ import annotations

import logging
from typing import List, Optional, Tuple

from app.services.context.models import (
    ContextPackage,
    ContextSection,
    ProviderResult,
    ProviderStatus,
)
from app.services.context.utils.tokenizer import estimate_tokens

logger = logging.getLogger("context.merger")

# Canonical section order in the assembled context package
_SECTION_ORDER = [
    "system",
    "profile",
    "conversation",
    "workspace",
    "navigation",
    "rag",
]


class ContextMerger:
    """
    Merges ProviderResult sections into a unified ContextPackage.

    Maintains canonical section ordering.
    Preserves all metadata from each section.
    Computes total token count across the package.
    """

    def merge(
        self,
        scored_results: List[Tuple[float, ProviderResult]],
        all_results: List[ProviderResult],
    ) -> ContextPackage:
        """
        Builds a ContextPackage from scored (prioritized) provider results.

        Args:
            scored_results: (score, ProviderResult) pairs in priority order.
            all_results:    All results including SKIPPED/FAILED, for diagnostics.

        Returns:
            ContextPackage with ordered sections.
        """
        # Index successful sections by name
        sections_by_name: dict[str, ContextSection] = {}
        nav_early_exit: Optional[str] = None
        nav_early_exit_msg: Optional[str] = None
        nav_data: Optional[dict] = None

        for _, result in scored_results:
            if result.section is None:
                continue
            name = result.section.name
            if name not in sections_by_name:
                sections_by_name[name] = result.section
            else:
                # Merge duplicate-named sections (shouldn't happen normally)
                sections_by_name[name].items.extend(result.section.items)
                sections_by_name[name].total_tokens += result.section.total_tokens

        # Check all results for nav early exits
        for result in all_results:
            if result.nav_early_exit:
                nav_early_exit = result.nav_early_exit
                nav_early_exit_msg = result.metadata.error_detail
            if result.nav_ctx_dict and not nav_data:
                nav_data = result.nav_ctx_dict

        # Extract navigation structured data for prompt injection
        nav_section = sections_by_name.get("navigation")
        if nav_section and nav_section.items:
            nav_meta = nav_section.items[0].metadata
            if nav_meta.get("nav_ctx_dict"):
                nav_data = nav_meta["nav_ctx_dict"]

        # Assemble sections in canonical order
        ordered_sections: List[ContextSection] = []
        for name in _SECTION_ORDER:
            section = sections_by_name.get(name)
            if section and section.items:
                ordered_sections.append(section)

        # Compute total tokens
        total_tokens = sum(s.total_tokens for s in ordered_sections)

        package = ContextPackage(
            sections=ordered_sections,
            total_tokens=total_tokens,
            navigation_data=nav_data,
            nav_early_exit=nav_early_exit,
            nav_early_exit_msg=nav_early_exit_msg,
            provider_results=all_results,
        )

        logger.info(
            "Merge complete: %d sections, %d total tokens",
            len(ordered_sections),
            total_tokens,
        )
        return package
