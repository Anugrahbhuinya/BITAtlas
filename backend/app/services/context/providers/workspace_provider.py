"""
Workspace Context Provider.

Retrieves student academic workspace context:
- Timetable
- Attendance
- Academic calendar
- Planner items

Wraps the existing get_academic_prompt_context() function which
delegates to AcademicContextService and its provider chain.
"""
from __future__ import annotations

import logging
import time
from typing import Optional

from app.services.context.configs.context_config import PROVIDER_WEIGHTS
from app.services.context.interfaces import BaseContextProvider
from app.services.context.models import ContextItem, ContextRequest, ProviderResult
from app.services.context.providers.base import (
    FailedProviderResult,
    SkippedProviderResult,
    build_provider_result,
)

logger = logging.getLogger("context.workspace_provider")


class WorkspaceProvider(BaseContextProvider):
    """
    Retrieves student academic workspace context using the existing
    AcademicContextService pipeline.

    Skips cleanly for guest (unauthenticated) requests.
    Never calls Gemini. Never builds prompts.
    """

    @property
    def provider_id(self) -> str:
        return "workspace"

    @property
    def priority_weight(self) -> float:
        return PROVIDER_WEIGHTS.get("workspace", 0.85)

    async def get_context(self, request: ContextRequest) -> ProviderResult:
        """
        Fetches academic/workspace context for the authenticated student.

        Args:
            request: ContextRequest with student_id, student data, and nav data.

        Returns:
            ProviderResult with workspace section, or SKIPPED for guests.
        """
        t0 = time.monotonic()

        student_id = (
            request.current_student.get("_id", "guest_student")
            if request.current_student
            else "guest_student"
        )

        # Only run if there is a student or navigation node context
        has_student = request.current_student is not None
        has_nav_nodes = bool(
            request.current_location_node_id or request.current_dest_node_id
        )

        if not has_student and not has_nav_nodes:
            return SkippedProviderResult(
                provider_id=self.provider_id,
                priority_weight=self.priority_weight,
                reason="No authenticated student and no navigation nodes",
            )

        try:
            from app.services.llm.academic_context import get_academic_prompt_context

            nav_data = {
                "currentLocationNodeId": request.current_location_node_id,
                "currentDestinationNodeId": request.current_dest_node_id,
                "accessibilityMode": request.accessibility_mode,
            }

            academic_context_str = await get_academic_prompt_context(
                student_id=student_id,
                student_data=request.current_student,
                nav_data=nav_data,
            )

            if not academic_context_str or not academic_context_str.strip():
                return SkippedProviderResult(
                    provider_id=self.provider_id,
                    priority_weight=self.priority_weight,
                    reason="Academic context returned empty",
                )

            items = [
                ContextItem(
                    content=academic_context_str,
                    metadata={
                        "student_id": student_id,
                        "has_nav_nodes": has_nav_nodes,
                    },
                )
            ]

            elapsed = time.monotonic() - t0
            return build_provider_result(
                provider_id=self.provider_id,
                section_name="workspace",
                items=items,
                confidence=1.0,
                priority_weight=self.priority_weight,
                execution_time_s=elapsed,
            )

        except Exception as exc:
            logger.error("WorkspaceProvider failed: %s", exc, exc_info=True)
            return FailedProviderResult(
                provider_id=self.provider_id,
                priority_weight=self.priority_weight,
                error_detail=str(exc),
                execution_time_s=time.monotonic() - t0,
            )
