"""
Context Token Budget Manager.

Enforces section-specific and global token limits on the ContextPackage,
resolving overflows using a priority-based resolution order.
"""
from __future__ import annotations

import logging
from typing import Dict

from app.services.context.configs.context_config import (
    OVERFLOW_RESOLUTION_ORDER,
    TOKEN_BUDGET,
    TOTAL_CONTEXT_TOKEN_LIMIT,
)
from app.services.context.models import BudgetAllocation, ContextPackage
from app.services.context.utils.tokenizer import estimate_tokens

logger = logging.getLogger("context.token_budget")


class TokenBudgetManager:
    """
    Manages and enforces token budgets across all context sections.
    
    If the total context size exceeds the global budget limit,
    this manager selectively trims/compresses sections in the
    canonical resolution order until the limit is respected.
    """

    def enforce_budget(self, package: ContextPackage) -> BudgetAllocation:
        """
        Enforces the global token budget on the ContextPackage.

        Trims sections in-place according to OVERFLOW_RESOLUTION_ORDER
        if the total token count exceeds TOTAL_CONTEXT_TOKEN_LIMIT.

        Args:
            package: ContextPackage to enforce budget on.

        Returns:
            BudgetAllocation object describing the final allocation stats.
        """
        initial_tokens = package.total_tokens
        limit = TOTAL_CONTEXT_TOKEN_LIMIT
        
        overflow = initial_tokens > limit
        overflow_by = max(0, initial_tokens - limit)

        logger.info(
            "Enforcing budget. Initial tokens: %d, Limit: %d, Overflow: %s (by %d)",
            initial_tokens,
            limit,
            overflow,
            overflow_by,
        )

        if overflow:
            self._resolve_overflow(package, overflow_by)

        # Build allocation map for diagnostics
        allocations: Dict[str, int] = {
            section.name: section.total_tokens for section in package.sections
        }

        # Add any missing standard sections as 0
        for name in TOKEN_BUDGET.keys():
            if name != "prompt_reserve" and name not in allocations:
                allocations[name] = 0

        # Enforce reserve diagnostic
        allocations["prompt_reserve"] = TOKEN_BUDGET.get("prompt_reserve", 300)

        allocation = BudgetAllocation(
            allocations=allocations,
            total_budget=limit,
            overflow=overflow,
            overflow_by=overflow_by,
        )

        return allocation

    def _resolve_overflow(self, package: ContextPackage, overflow_by: int) -> None:
        """Trims sections in resolution order until overflow is resolved."""
        limit = TOTAL_CONTEXT_TOKEN_LIMIT
        
        for section_name in OVERFLOW_RESOLUTION_ORDER:
            current_total = sum(s.total_tokens for s in package.sections)
            if current_total <= limit:
                break

            section = package.get_section(section_name)
            if not section or not section.items:
                continue

            needed_reduction = current_total - limit
            logger.debug(
                "Resolving overflow: section '%s' has %d tokens. Need reduction of %d",
                section_name,
                section.total_tokens,
                needed_reduction,
            )

            if section_name == "conversation":
                # Special handling for conversation: try formatting with 2 turns, then 1 turn
                item = section.items[0]
                raw_messages = item.metadata.get("messages")
                is_navigation = item.metadata.get("is_navigation", False)

                if raw_messages:
                    from app.services.context.providers.conversation_provider import (
                        _format_general_history,
                        _format_navigation_history,
                    )
                    
                    # Try 2 turns first
                    for turns in [2, 1]:
                        if is_navigation:
                            new_content = _format_navigation_history(raw_messages, turns)
                        else:
                            new_content = _format_general_history(raw_messages, turns)
                            
                        new_tokens = estimate_tokens(new_content)
                        reduction = item.token_count - new_tokens
                        
                        item.content = new_content
                        item.token_count = new_tokens
                        section.total_tokens = sum(i.token_count for i in section.items)
                        
                        current_total = sum(s.total_tokens for s in package.sections)
                        if current_total <= limit:
                            break
                            
            else:
                # List-based sections (rag, workspace, navigation, profile):
                # Remove items from the end of the section one by one
                while section.items and sum(s.total_tokens for s in package.sections) > limit:
                    removed_item = section.items.pop()
                    section.total_tokens -= removed_item.token_count
                    logger.debug(
                        "Removed item from section '%s'. Section tokens: %d",
                        section_name,
                        section.total_tokens,
                    )

        # Update package final total
        package.total_tokens = sum(s.total_tokens for s in package.sections)
        logger.info("Overflow resolved. Final tokens: %d", package.total_tokens)
