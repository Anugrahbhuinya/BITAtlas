"""
BaseContextProvider interface for the Smart Context Engine.

Every context provider must implement this interface.
Providers are isolated: they cannot call Gemini, build prompts,
or depend on other providers.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.services.context.models import ContextRequest, ProviderResult


class BaseContextProvider(ABC):
    """
    Abstract base class for all context providers.

    Contract:
    - get_context() must never raise an unhandled exception.
    - get_context() must never call Gemini.
    - get_context() must never build prompts.
    - get_context() must never depend on other providers.
    - Failures must be caught internally and returned as
      ProviderResult with status=FAILED.
    """

    @abstractmethod
    async def get_context(self, request: ContextRequest) -> ProviderResult:
        """
        Fetches and returns context for the given request.

        Args:
            request: Structured input containing query, intent, student data,
                     session ID, and routing flags.

        Returns:
            ProviderResult with populated section and metadata, or
            ProviderResult with status=FAILED if an error occurred.
        """
        ...

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """
        Unique string identifier for this provider.
        Used in diagnostics, logging, and section naming.
        """
        ...

    @property
    @abstractmethod
    def priority_weight(self) -> float:
        """
        Base priority weight for this provider type.
        Used by the Prioritizer when computing priority scores.
        Higher = more important.
        """
        ...
