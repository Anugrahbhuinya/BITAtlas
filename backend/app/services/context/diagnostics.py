"""
Context Diagnostics.

Helpers to gather and compile structured performance, token usage, and execution
diagnostics across the pipeline execution.
"""
from __future__ import annotations

import logging
import time
from typing import Dict, List, Optional

from app.services.context.models import (
    BudgetAllocation,
    CompressionResult,
    PipelineDiagnostics,
    ProviderDiagnostic,
    ProviderResult,
)

logger = logging.getLogger("context.diagnostics")


class DiagnosticsCollector:
    """
    Collects diagnostics during a Context Pipeline execution.
    """

    def __init__(self) -> None:
        self.t0 = time.monotonic()
        self.provider_diagnostics: List[ProviderDiagnostic] = []
        self.providers_executed: List[str] = []
        self.providers_skipped: Dict[str, str] = {}
        self.priority_scores: Dict[str, float] = {}

    def record_provider_result(self, result: ProviderResult, score: float = 0.0) -> None:
        """Records diagnostic info for an executed provider."""
        meta = result.metadata
        provider_id = meta.provider_id
        
        # Calculate tokens produced
        tokens_produced = 0
        if result.section:
            tokens_produced = result.section.total_tokens

        diag = ProviderDiagnostic(
            provider_id=provider_id,
            status=meta.status,
            execution_time_s=meta.execution_time_s,
            tokens_produced=tokens_produced,
            priority_score=score,
            confidence=meta.confidence,
            skip_reason=meta.skip_reason,
            error_detail=meta.error_detail,
        )
        self.provider_diagnostics.append(diag)
        
        from app.services.context.models import ProviderStatus
        if meta.status == ProviderStatus.SKIPPED:
            self.providers_skipped[provider_id] = meta.skip_reason or "Unknown reason"
        else:
            self.providers_executed.append(provider_id)
            if score > 0.0:
                self.priority_scores[provider_id] = score

    def compile(
        self,
        total_tokens_before: int,
        total_tokens_after: int,
        duplicates_removed: int,
        compression_result: Optional[CompressionResult],
        budget_allocation: Optional[BudgetAllocation],
        final_context_text: str,
    ) -> PipelineDiagnostics:
        """Compiles the collected information into the final PipelineDiagnostics model."""
        elapsed = time.monotonic() - self.t0

        # Build token usage per section mapping
        token_usage_per_section: Dict[str, int] = {}
        if budget_allocation:
            token_usage_per_section = {
                k: v for k, v in budget_allocation.allocations.items() if k != "prompt_reserve"
            }

        diag_payload = PipelineDiagnostics(
            providers_executed=self.providers_executed,
            providers_skipped=self.providers_skipped,
            provider_diagnostics=self.provider_diagnostics,
            priority_scores=self.priority_scores,
            token_usage_per_section=token_usage_per_section,
            total_tokens_before=total_tokens_before,
            total_tokens_after=total_tokens_after,
            compression_result=compression_result,
            duplicates_removed=duplicates_removed,
            pipeline_time_s=elapsed,
            context_size_chars=len(final_context_text),
            budget_allocation=budget_allocation,
        )

        logger.info(
            "Compiled pipeline diagnostics: time=%.4fs, tokens_before=%d, tokens_after=%d, "
            "duplicates_removed=%d, chars=%d",
            elapsed,
            total_tokens_before,
            total_tokens_after,
            duplicates_removed,
            len(final_context_text),
        )
        return diag_payload
