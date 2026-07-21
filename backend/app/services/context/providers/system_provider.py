"""
System Context Provider.

Provides static system-level context:
- Current date and time (IST)
- AI operating identity
- Semester/academic cycle metadata

This provider never queries the database or calls external services.
It always succeeds and provides foundational context for every query.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone, timedelta

from app.services.context.configs.context_config import PROVIDER_WEIGHTS
from app.services.context.interfaces import BaseContextProvider
from app.services.context.models import ContextItem, ContextRequest, ProviderResult
from app.services.context.providers.base import FailedProviderResult, build_provider_result

logger = logging.getLogger("context.system_provider")

# India Standard Time offset
_IST = timezone(timedelta(hours=5, minutes=30))


class SystemProvider(BaseContextProvider):
    """
    Provides system-level context for every request.

    Outputs:
    - Current date and time in IST
    - AI assistant identity statement
    - Academic system metadata

    Never calls Gemini. Never builds prompts. Always succeeds.
    """

    @property
    def provider_id(self) -> str:
        return "system"

    @property
    def priority_weight(self) -> float:
        return PROVIDER_WEIGHTS.get("system", 1.0)

    async def get_context(self, request: ContextRequest) -> ProviderResult:
        """
        Returns system-level context items.

        Args:
            request: ContextRequest (query, intent, student data, etc.)

        Returns:
            ProviderResult with system section populated.
        """
        t0 = time.monotonic()
        try:
            now_ist = datetime.now(_IST)
            date_str = now_ist.strftime("%A, %B %d, %Y")
            time_str = now_ist.strftime("%I:%M %p IST")

            system_text = (
                f"You are BITATLAS — an enterprise-grade, production AI system "
                f"serving students of Birla Institute of Technology, Mesra.\n"
                f"Current Date: {date_str}\n"
                f"Current Time: {time_str}\n"
                f"Your role is to assist students accurately using only verified context provided below."
            )

            items = [
                ContextItem(
                    content=system_text,
                    metadata={"date": date_str, "time": time_str},
                )
            ]

            elapsed = time.monotonic() - t0
            return build_provider_result(
                provider_id=self.provider_id,
                section_name="system",
                items=items,
                confidence=1.0,
                priority_weight=self.priority_weight,
                execution_time_s=elapsed,
            )

        except Exception as exc:
            logger.error("SystemProvider failed: %s", exc, exc_info=True)
            return FailedProviderResult(
                provider_id=self.provider_id,
                priority_weight=self.priority_weight,
                error_detail=str(exc),
                execution_time_s=time.monotonic() - t0,
            )
