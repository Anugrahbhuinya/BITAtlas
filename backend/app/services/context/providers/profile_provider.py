"""
Profile Context Provider.

Provides authenticated student profile information:
- Name, department, semester, CGPA
- Attendance summary

Sources data from the authenticated student dict passed through
from the JWT authentication layer. No database calls are made here.
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

logger = logging.getLogger("context.profile_provider")


class ProfileProvider(BaseContextProvider):
    """
    Provides student profile context from the authenticated user dict.

    Only active when a student is authenticated (current_student is not None).
    Returns a skipped result for unauthenticated/guest requests.

    Never calls Gemini. Never builds prompts.
    """

    @property
    def provider_id(self) -> str:
        return "profile"

    @property
    def priority_weight(self) -> float:
        return PROVIDER_WEIGHTS.get("profile", 0.9)

    async def get_context(self, request: ContextRequest) -> ProviderResult:
        """
        Extracts student profile from the authenticated student dictionary.

        Args:
            request: ContextRequest with current_student dict.

        Returns:
            ProviderResult with student profile section, or SKIPPED if unauthenticated.
        """
        t0 = time.monotonic()

        if not request.current_student:
            return SkippedProviderResult(
                provider_id=self.provider_id,
                priority_weight=self.priority_weight,
                reason="No authenticated student (guest request)",
            )

        try:
            student = request.current_student
            profile_lines = []

            name = student.get("name", "Student")
            department = student.get("department", "")
            semester = student.get("semester", "")
            cgpa = student.get("cgpa", "")
            attendance = student.get("attendance", "")

            profile_lines.append(f"Student Name: {name}")
            if department:
                profile_lines.append(f"Department: {department}")
            if semester:
                profile_lines.append(f"Semester: {semester}")
            if cgpa:
                profile_lines.append(f"CGPA: {cgpa}")
            if attendance:
                profile_lines.append(f"Attendance Summary:\n{attendance}")

            profile_text = "\n".join(profile_lines)

            items = [
                ContextItem(
                    content=profile_text,
                    metadata={
                        "student_id": str(student.get("_id", "")),
                        "name": name,
                        "department": department,
                        "semester": str(semester),
                        "cgpa": str(cgpa),
                        "attendance": str(attendance),
                    },
                )
            ]

            elapsed = time.monotonic() - t0
            return build_provider_result(
                provider_id=self.provider_id,
                section_name="profile",
                items=items,
                confidence=1.0,
                priority_weight=self.priority_weight,
                execution_time_s=elapsed,
            )

        except Exception as exc:
            logger.error("ProfileProvider failed: %s", exc, exc_info=True)
            return FailedProviderResult(
                provider_id=self.provider_id,
                priority_weight=self.priority_weight,
                error_detail=str(exc),
                execution_time_s=time.monotonic() - t0,
            )
