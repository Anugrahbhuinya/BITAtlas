"""
Dynamic Context Provider Selector.

Maps a RoutingDecision's intent to the set of required context providers.
Only providers that are relevant to the current routing decision are executed.
This avoids unnecessary database calls and latency.
"""
from __future__ import annotations

import logging
from typing import Dict, List, Set

from app.services.context.configs.context_config import PROVIDER_ENABLED

logger = logging.getLogger("context.selector")

# ---------------------------------------------------------------------------
# Provider selection rules per intent
# Each intent maps to the set of provider IDs that should be executed.
# Providers NOT in the set are skipped entirely.
# ---------------------------------------------------------------------------
_INTENT_PROVIDER_MAP: Dict[str, Set[str]] = {
    # Navigation: route + profile + conversation + system
    "navigation": {"navigation", "profile", "conversation", "system"},

    # Student workspace: workspace + conversation + profile + system
    "student_workspace": {"workspace", "conversation", "profile", "system"},

    # Academic calendar: rag + workspace + conversation + system
    "academic": {"rag", "workspace", "conversation", "system"},

    # General campus information: rag + conversation + system
    "general": {"rag", "conversation", "system"},

    # Educational / conceptual (Gemini handles majority): rag optional + system
    "educational": {"rag", "conversation", "system"},

    # Document QA: rag + conversation + profile + system
    "rag": {"rag", "conversation", "profile", "system"},
}

# Default provider set when intent doesn't match any specific rule
_DEFAULT_PROVIDERS: Set[str] = {"rag", "conversation", "system"}

# Intents where RAG should always be skipped
_RAG_SKIP_INTENTS = {"navigation"}

# Intents where workspace should always be skipped
_WORKSPACE_SKIP_INTENTS = {
    "educational", "general", "navigation",
}


def select_providers(
    intent: str,
    requires_rag: bool,
    requires_navigation: bool,
    requires_workspace: bool,
    has_student: bool,
) -> List[str]:
    """
    Returns an ordered list of provider IDs to execute for this request.

    Selection is driven by:
    1. The legacy intent string (mapped from RoutingDecision.intent)
    2. Routing flags (requires_rag, requires_navigation, requires_workspace)
    3. Whether a student is authenticated (profile provider)
    4. Global provider enable flags (from context_config)

    Args:
        intent:              Legacy intent string (e.g. "navigation", "general").
        requires_rag:        True if the routing decision requires RAG retrieval.
        requires_navigation: True if the routing decision requires navigation.
        requires_workspace:  True if the routing decision requires workspace context.
        has_student:         True if an authenticated student is present.

    Returns:
        Ordered list of provider IDs to execute. System is always last.
    """
    # Get the base set from intent map
    base_set: Set[str] = _INTENT_PROVIDER_MAP.get(intent, _DEFAULT_PROVIDERS).copy()

    # Override with routing flags
    if not requires_rag:
        base_set.discard("rag")
    if not requires_navigation:
        base_set.discard("navigation")
    if not requires_workspace:
        base_set.discard("workspace")

    # Force add providers when routing explicitly requires them
    if requires_navigation:
        base_set.add("navigation")
        base_set.add("conversation")  # navigation uses history
    if requires_workspace:
        base_set.add("workspace")
    if requires_rag:
        base_set.add("rag")

    # Profile only makes sense for authenticated students
    if not has_student:
        base_set.discard("profile")

    # Conversation is always useful when session exists (selector doesn't know session_id,
    # provider itself will skip if no session)
    base_set.add("conversation")

    # System is always included
    base_set.add("system")

    # Filter by global enable flags
    enabled = {p for p in base_set if PROVIDER_ENABLED.get(p, True)}

    # Log selections
    skipped = base_set - enabled
    if skipped:
        logger.info("Providers disabled by config: %s", skipped)

    logger.info(
        "Selector: intent=%s → providers=%s",
        intent,
        sorted(enabled),
    )

    # Return in execution-friendly order (system last to avoid ordering issues)
    ordered = [p for p in ["navigation", "workspace", "rag", "conversation", "profile", "system"]
               if p in enabled]
    return ordered
