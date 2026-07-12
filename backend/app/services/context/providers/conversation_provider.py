"""
Conversation Context Provider.

Retrieves and formats conversation history from the session store.

Uses the existing history_service (get_chat_history, format_chat_history)
and the navigation-specific formatter from chat.py (moved here cleanly).
"""
from __future__ import annotations

import logging
import time
from typing import List, Optional

from app.services.context.configs.context_config import (
    MAX_CONVERSATION_TURNS,
    PROVIDER_WEIGHTS,
)
from app.services.context.interfaces import BaseContextProvider
from app.services.context.models import ContextItem, ContextRequest, ProviderResult
from app.services.context.providers.base import (
    FailedProviderResult,
    SkippedProviderResult,
    build_provider_result,
)

logger = logging.getLogger("context.conversation_provider")

# Keywords that indicate a failed navigation exchange (should be excluded from history)
_NAV_FAILURE_KEYWORDS = [
    "could not find",
    "does not exist",
    "multiple locations match",
    "which one did you mean",
    "no route found",
    "invalid",
    "error",
]


def _format_navigation_history(messages: List[dict], max_turns: int) -> str:
    """
    Formats navigation-specific history, excluding failure messages.

    Mirrors the format_navigation_chat_history() function in chat.py,
    consolidated here as the single authoritative implementation.

    Args:
        messages:  Raw session message list.
        max_turns: Maximum number of messages to include.

    Returns:
        Formatted history string (last 2 successful navigation exchanges).
    """
    cleaned = []
    failure_lower = [kw.lower() for kw in _NAV_FAILURE_KEYWORDS]
    for msg in messages:
        content = msg.get("content", "")
        if any(kw in content.lower() for kw in failure_lower):
            continue
        role = msg.get("role", "user")
        cleaned.append(f"{role}: {content}")
    return "\n".join(cleaned[-2:])


def _format_general_history(messages: List[dict], max_turns: int) -> str:
    """
    Formats general conversation history (last N turns).

    Args:
        messages:  Raw session message list.
        max_turns: Maximum number of messages to include.

    Returns:
        Formatted history string.
    """
    if not messages:
        return ""
    last = messages[-max_turns:] if len(messages) > max_turns else messages
    formatted = []
    for msg in last:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        formatted.append(f"{role}: {content}")
    return "\n".join(formatted)


class ConversationProvider(BaseContextProvider):
    """
    Provides conversation memory context from the session store.

    Skips cleanly when no session_id is present.
    Never calls Gemini. Never builds prompts.
    """

    @property
    def provider_id(self) -> str:
        return "conversation"

    @property
    def priority_weight(self) -> float:
        return PROVIDER_WEIGHTS.get("conversation", 0.80)

    async def get_context(self, request: ContextRequest) -> ProviderResult:
        """
        Retrieves and formats chat history for the given session.

        If request.history is pre-populated (passed in from the orchestrator),
        uses that directly to avoid a redundant DB call.

        Args:
            request: ContextRequest with session_id and intent.

        Returns:
            ProviderResult with conversation section, or SKIPPED if no session.
        """
        t0 = time.monotonic()

        if not request.session_id:
            return SkippedProviderResult(
                provider_id=self.provider_id,
                priority_weight=self.priority_weight,
                reason="No session_id provided",
            )

        try:
            # Use pre-fetched history if available, otherwise fetch from DB
            if request.history is not None:
                history = request.history
            else:
                from app.services.history_service import get_chat_history
                history = await get_chat_history(request.session_id)

            if not history or len(history) <= 1:
                return SkippedProviderResult(
                    provider_id=self.provider_id,
                    priority_weight=self.priority_weight,
                    reason="No meaningful history (0 or 1 messages)",
                )

            # Exclude the most recent user message (it's the current query)
            prior_messages = history[:-1]

            is_navigation = (request.intent == "navigation")
            if is_navigation:
                history_text = _format_navigation_history(prior_messages, MAX_CONVERSATION_TURNS)
            else:
                history_text = _format_general_history(prior_messages, MAX_CONVERSATION_TURNS)

            if not history_text.strip():
                return SkippedProviderResult(
                    provider_id=self.provider_id,
                    priority_weight=self.priority_weight,
                    reason="History text is empty after formatting",
                )

            items = [
                ContextItem(
                    content=history_text,
                    metadata={
                        "session_id": request.session_id,
                        "message_count": len(history),
                        "is_navigation": is_navigation,
                        "messages": prior_messages,
                    },
                )
            ]

            elapsed = time.monotonic() - t0
            return build_provider_result(
                provider_id=self.provider_id,
                section_name="conversation",
                items=items,
                confidence=1.0,
                priority_weight=self.priority_weight,
                execution_time_s=elapsed,
            )

        except Exception as exc:
            logger.error("ConversationProvider failed: %s", exc, exc_info=True)
            return FailedProviderResult(
                provider_id=self.provider_id,
                priority_weight=self.priority_weight,
                error_detail=str(exc),
                execution_time_s=time.monotonic() - t0,
            )
