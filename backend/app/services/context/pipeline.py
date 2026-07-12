"""
Context Pipeline.

Implements the sequential context collection and optimization pipeline, including
selection, concurrent execution, prioritization, deduplication, merging,
compression, and token budgeting.
"""
from __future__ import annotations

import asyncio
import logging
import time
from typing import Dict, List, Tuple

from app.services.context.configs.context_config import PROVIDER_ENABLED
from app.services.context.deduplicator import ContextDeduplicator
from app.services.context.diagnostics import DiagnosticsCollector
from app.services.context.merger import ContextMerger
from app.services.context.models import (
    ContextPackage,
    ContextRequest,
    PipelineDiagnostics,
    ProviderResult,
)
from app.services.context.prioritizer import ContextPrioritizer
from app.services.context.providers.base import SkippedProviderResult
from app.services.context.providers.conversation_provider import ConversationProvider
from app.services.context.providers.navigation_provider import NavigationProvider
from app.services.context.providers.profile_provider import ProfileProvider
from app.services.context.providers.rag_provider import RAGProvider
from app.services.context.providers.system_provider import SystemProvider
from app.services.context.providers.workspace_provider import WorkspaceProvider
from app.services.context.selector import select_providers

logger = logging.getLogger("context.pipeline")


class ContextPipeline:
    """
    Executes the Context Engine pipeline.
    
    Flow:
    1. Select providers
    2. Execute in parallel (gather)
    3. Prioritize results
    4. Deduplicate items
    5. Merge sections
    6. Compress context
    7. Enforce token budget
    8. Compile diagnostics
    """

    def __init__(self) -> None:
        self.providers = {
            "navigation": NavigationProvider(),
            "workspace": WorkspaceProvider(),
            "rag": RAGProvider(),
            "conversation": ConversationProvider(),
            "profile": ProfileProvider(),
            "system": SystemProvider(),
        }
        self.prioritizer = ContextPrioritizer()
        self.deduplicator = ContextDeduplicator()
        self.merger = ContextMerger()
        
        # We import them lazily to prevent circular dependencies
        from app.services.context.compression import ContextCompressor
        from app.services.context.token_budget import TokenBudgetManager
        self.compressor = ContextCompressor()
        self.budget_manager = TokenBudgetManager()

    async def execute(
        self, request: ContextRequest
    ) -> Tuple[ContextPackage, PipelineDiagnostics]:
        """
        Executes the context pipeline sequentially.

        Args:
            request: Structured ContextRequest input.

        Returns:
            Tuple of (ContextPackage, PipelineDiagnostics).
        """
        collector = DiagnosticsCollector()
        t_start = time.time()

        # 1. Select providers
        selected_ids = select_providers(
            intent=request.intent,
            requires_rag=request.requires_rag,
            requires_navigation=request.requires_navigation,
            requires_workspace=request.requires_workspace,
            has_student=request.current_student is not None,
        )

        # 2. Execute selected providers concurrently
        tasks = []
        executed_ids: List[str] = []
        
        for pid in selected_ids:
            if pid in self.providers:
                executed_ids.append(pid)
                tasks.append(self.providers[pid].get_context(request))

        logger.info("Executing context providers concurrently: %s", executed_ids)
        executed_results = await asyncio.gather(*tasks) if tasks else []
        
        # Build map of executed results
        results_map: Dict[str, ProviderResult] = {
            res.metadata.provider_id: res for res in executed_results
        }

        # Handle skipped/unselected providers for diagnostics
        all_results: List[ProviderResult] = []
        for pid, provider in self.providers.items():
            if pid in results_map:
                all_results.append(results_map[pid])
            else:
                reason = "Not selected for this intent"
                if not PROVIDER_ENABLED.get(pid, True):
                    reason = "Disabled via global configuration"
                elif pid == "profile" and not request.current_student:
                    reason = "No authenticated student (guest request)"
                elif pid == "conversation" and not request.session_id:
                    reason = "No session ID provided"
                    
                skipped_res = SkippedProviderResult(
                    provider_id=pid,
                    priority_weight=provider.priority_weight,
                    reason=reason,
                )
                all_results.append(skipped_res)

        # 3. Prioritize results (only scores successfully executed results)
        scored_results = self.prioritizer.prioritize(
            results=executed_results,
            routing_confidence=request.routing_confidence,
            request_timestamp=t_start,
        )
        scores_dict = self.prioritizer.get_scores_dict(scored_results)

        # Record diagnostics for each provider
        for res in all_results:
            score = scores_dict.get(res.metadata.provider_id, 0.0)
            collector.record_provider_result(res, score)

        # 4. Deduplicate (operates in-place on ProviderResult sections)
        just_successful_results = [res for _, res in scored_results]
        _, duplicates_removed = self.deduplicator.deduplicate(just_successful_results)

        # 5. Merge sections into ContextPackage
        package = self.merger.merge(scored_results, all_results)
        tokens_before = package.total_tokens

        # 6. Apply compression (recalcs total tokens in-place)
        compression_result = self.compressor.compress(package, request.compression_level)

        # 7. Apply token budget (trims in-place and enforces TOTAL_CONTEXT_TOKEN_LIMIT)
        budget_allocation = self.budget_manager.enforce_budget(package)
        tokens_after = package.total_tokens

        # 8. Compile diagnostics
        final_text = "\n\n".join(section.formatted_text() for section in package.sections)
        diagnostics = collector.compile(
            total_tokens_before=tokens_before,
            total_tokens_after=tokens_after,
            duplicates_removed=duplicates_removed,
            compression_result=compression_result,
            budget_allocation=budget_allocation,
            final_context_text=final_text,
        )

        return package, diagnostics
