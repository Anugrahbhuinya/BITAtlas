"""
Navigation Context Provider.

Resolves navigation nodes and computes routes using the existing
navigation_resolver module.

Handles all navigation validation states:
- valid: Route computed successfully
- ambiguous: Multiple locations matched → early exit signal
- invalid_destination: Destination not on campus map → early exit signal
- invalid_source: Source not found → early exit signal
- no_path: No route exists between nodes → early exit signal

Early exit signals are propagated via ProviderResult.nav_early_exit
so that chat.py can return the appropriate response before calling Gemini.
"""
from __future__ import annotations

import logging
import time

from app.services.context.configs.context_config import PROVIDER_WEIGHTS
from app.services.context.interfaces import BaseContextProvider
from app.services.context.models import ContextItem, ContextRequest, ProviderResult
from app.services.context.providers.base import (
    FailedProviderResult,
    SkippedProviderResult,
    build_provider_result,
)

logger = logging.getLogger("context.navigation_provider")


class NavigationProvider(BaseContextProvider):
    """
    Resolves campus navigation and provides structured route context.

    Skips cleanly when navigation is not required for the routing decision.
    Propagates early-exit signals for ambiguous/invalid navigation requests.

    Never calls Gemini. Never builds prompts. Isolated from other providers.
    """

    @property
    def provider_id(self) -> str:
        return "navigation"

    @property
    def priority_weight(self) -> float:
        return PROVIDER_WEIGHTS.get("navigation", 0.95)

    async def get_context(self, request: ContextRequest) -> ProviderResult:
        """
        Resolves navigation entities, computes route, and returns context.

        Args:
            request: ContextRequest with query, intent, and nav node IDs.

        Returns:
            ProviderResult with navigation section on success, or
            ProviderResult with nav_early_exit set for handled error states.
        """
        t0 = time.monotonic()

        if not request.requires_navigation:
            return SkippedProviderResult(
                provider_id=self.provider_id,
                priority_weight=self.priority_weight,
                reason="Navigation not required for this routing decision",
            )

        try:
            from app.core.database import get_database
            from app.services.ai.prompt.navigation_resolver import resolve_navigation_nodes

            # Retrieve history for navigation context resolution
            history_list = request.history or []
            db = get_database()

            nav_ctx = await resolve_navigation_nodes(
                query=request.query,
                db=db,
                history_list=history_list,
                current_location_id=request.current_location_node_id,
                current_destination_id=request.current_dest_node_id,
                accessibility_mode=request.accessibility_mode,
            )

            elapsed = time.monotonic() - t0

            # ---------------------------------------------------------------
            # Handle early-exit states — propagate to orchestrator / chat.py
            # ---------------------------------------------------------------
            if nav_ctx.validation_status == "ambiguous":
                ambigs = nav_ctx.building_metadata.get("ambiguities", [])
                early_msg = (
                    f"Multiple locations match your query: {', '.join(ambigs)}. "
                    f"Which one did you mean?"
                )
                result = ProviderResult(
                    metadata=_build_meta(self, elapsed, 0.0),
                    section=None,
                    nav_early_exit="ambiguous",
                    nav_ctx_dict=nav_ctx.dict(),
                )
                result.metadata.error_detail = early_msg
                return result

            if nav_ctx.validation_status == "invalid_destination":
                result = ProviderResult(
                    metadata=_build_meta(self, elapsed, 0.0),
                    section=None,
                    nav_early_exit="invalid_destination",
                    nav_ctx_dict=nav_ctx.dict(),
                )
                result.metadata.error_detail = (
                    "The destination you requested does not exist on the BIT Mesra campus. "
                    "If you are looking for academic lectures, check the Lecture Hall Complex (LHC) "
                    "or department buildings."
                )
                return result

            if nav_ctx.validation_status == "invalid_source":
                result = ProviderResult(
                    metadata=_build_meta(self, elapsed, 0.0),
                    section=None,
                    nav_early_exit="invalid_source",
                    nav_ctx_dict=nav_ctx.dict(),
                )
                result.metadata.error_detail = "The source location could not be identified."
                return result

            if nav_ctx.validation_status == "no_path":
                result = ProviderResult(
                    metadata=_build_meta(self, elapsed, 0.0),
                    section=None,
                    nav_early_exit="no_path",
                    nav_ctx_dict=nav_ctx.dict(),
                )
                result.metadata.error_detail = (
                    f"No pathway exists between {nav_ctx.source} and "
                    f"{nav_ctx.destination} on the campus graph."
                )
                return result

            if nav_ctx.validation_status != "valid":
                result = ProviderResult(
                    metadata=_build_meta(self, elapsed, 0.0),
                    section=None,
                    nav_early_exit=nav_ctx.validation_status,
                    nav_ctx_dict=nav_ctx.dict(),
                )
                result.metadata.error_detail = (
                    f"Navigation failed: {nav_ctx.validation_status.replace('_', ' ')}."
                )
                return result

            # ---------------------------------------------------------------
            # Build navigation context string for valid routes
            # ---------------------------------------------------------------
            nav_instructions_str = "\n".join(
                f"- {instr}" for instr in nav_ctx.directions
            )
            landmarks_str = ", ".join(nav_ctx.landmarks) if nav_ctx.landmarks else "None"
            facilities_str = (
                ", ".join(nav_ctx.nearby_facilities) if nav_ctx.nearby_facilities else "None"
            )

            navigation_context_str = (
                f"NAVIGATION CONTEXT:\n"
                f"Destination: {nav_ctx.destination}\n"
                f"Source: {nav_ctx.source or 'None'}\n"
                f"Walking Distance: {nav_ctx.walking_distance} meters\n"
                f"Estimated Time: {nav_ctx.estimated_time} minutes\n"
                f"Directions:\n{nav_instructions_str}\n\n"
                f"Landmarks:\n{landmarks_str}\n\n"
                f"Nearby Facilities:\n{facilities_str}"
            )

            items = [
                ContextItem(
                    content=navigation_context_str,
                    metadata={
                        "source": nav_ctx.source,
                        "destination": nav_ctx.destination,
                        "walking_distance": nav_ctx.walking_distance,
                        "estimated_time": nav_ctx.estimated_time,
                        "directions": nav_ctx.directions,
                        "landmarks": nav_ctx.landmarks,
                        "nearby_facilities": nav_ctx.nearby_facilities,
                        "validation_status": nav_ctx.validation_status,
                        "nav_ctx_dict": nav_ctx.dict(),
                    },
                )
            ]

            result = build_provider_result(
                provider_id=self.provider_id,
                section_name="navigation",
                items=items,
                confidence=nav_ctx.confidence,
                priority_weight=self.priority_weight,
                execution_time_s=elapsed,
                section_metadata={
                    "validation_status": nav_ctx.validation_status,
                    "nav_ctx_dict": nav_ctx.dict(),
                },
            )
            return result

        except Exception as exc:
            logger.error("NavigationProvider failed: %s", exc, exc_info=True)
            return FailedProviderResult(
                provider_id=self.provider_id,
                priority_weight=self.priority_weight,
                error_detail=str(exc),
                execution_time_s=time.monotonic() - t0,
            )


def _build_meta(provider: "NavigationProvider", elapsed: float, confidence: float):
    """Helper to build ProviderMetadata for early-exit results."""
    from app.services.context.models import ProviderMetadata, ProviderStatus
    return ProviderMetadata(
        provider_id=provider.provider_id,
        status=ProviderStatus.DEGRADED,
        execution_time_s=elapsed,
        confidence=confidence,
        priority_weight=provider.priority_weight,
    )
