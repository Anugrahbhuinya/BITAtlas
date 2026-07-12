"""
RAG Context Provider.

Wraps the existing Hybrid RAG service (query_rag) to retrieve
relevant documents from the vector store.

Applies intent-specific filtering and chunk limiting consistent
with the original chat.py implementation.
"""
from __future__ import annotations

import asyncio
import logging
import time
from typing import List, Optional

from app.services.context.configs.context_config import (
    MAX_RAG_CHUNKS_DEFAULT,
    MAX_RAG_CHUNKS_NAVIGATION,
    MAX_RAG_CHUNKS_REASONING,
    PROVIDER_WEIGHTS,
)
from app.services.context.interfaces import BaseContextProvider
from app.services.context.models import ContextItem, ContextRequest, ProviderResult
from app.services.context.providers.base import (
    FailedProviderResult,
    SkippedProviderResult,
    build_provider_result,
)

logger = logging.getLogger("context.rag_provider")

# Keywords that make a navigation RAG chunk irrelevant
_NAV_UNRELATED_KEYWORDS = [
    "membership", "internet access", "wi-fi", "rules", "regulations",
    "admission", "fee structure", "library card", "fine", "refund",
    "bunking", "attendance policy", "syllabus details", "course syllabus",
    "marks distribution",
]

# Intent names that require reasoning-level chunk counts
_REASONING_INTENTS = {
    "Reasoning", "Comparison", "AI / ML Concept", "AI / ML Concepts",
    "Engineering Concept", "Programming Help", "Explanation",
    "Summarization", "General Academic Concept",
}


class RAGProvider(BaseContextProvider):
    """
    Retrieves relevant knowledge from the Hybrid RAG vector store.

    Wraps the existing synchronous query_rag() via asyncio.to_thread().
    Applies navigation-specific keyword filtering and intent-aware chunk limits.

    Never calls Gemini. Never builds prompts. Isolated from all other providers.
    """

    @property
    def provider_id(self) -> str:
        return "rag"

    @property
    def priority_weight(self) -> float:
        return PROVIDER_WEIGHTS.get("rag", 0.75)

    async def get_context(self, request: ContextRequest) -> ProviderResult:
        """
        Retrieves context chunks from the RAG knowledge base.

        Args:
            request: ContextRequest with query and intent.

        Returns:
            ProviderResult with retrieved knowledge section and citations,
            or SKIPPED if RAG is not required for this intent.
        """
        t0 = time.monotonic()

        if not request.requires_rag:
            return SkippedProviderResult(
                provider_id=self.provider_id,
                priority_weight=self.priority_weight,
                reason="RAG not required for this routing decision",
            )

        try:
            from app.services.rag.rag_service import query_rag
            from app.services.rag.retriever import is_reasoning_query

            # Run the synchronous RAG query in a thread pool
            rag_result = await asyncio.to_thread(
                query_rag, request.query, request.intent
            )

            if not rag_result or not rag_result.get("documents"):
                return SkippedProviderResult(
                    provider_id=self.provider_id,
                    priority_weight=self.priority_weight,
                    reason="RAG returned no documents",
                )

            documents: List[str] = rag_result.get("documents", [])
            confidence: float = float(rag_result.get("confidence", 1.0))

            # Navigation: filter unrelated chunks
            is_navigation = (request.intent == "navigation")
            if is_navigation:
                documents = [
                    doc for doc in documents
                    if not any(kw in doc.lower() for kw in _NAV_UNRELATED_KEYWORDS)
                ]

            # Determine chunk limit based on intent and reasoning flag
            is_reasoning = is_reasoning_query(request.query)
            if is_navigation:
                limit = MAX_RAG_CHUNKS_NAVIGATION
            elif is_reasoning or request.intent in _REASONING_INTENTS:
                limit = MAX_RAG_CHUNKS_REASONING
            else:
                limit = MAX_RAG_CHUNKS_DEFAULT

            selected_docs = documents[:limit]

            if not selected_docs:
                return SkippedProviderResult(
                    provider_id=self.provider_id,
                    priority_weight=self.priority_weight,
                    reason="No relevant chunks remaining after filtering",
                )

            # Build ContextItems preserving inline citations already in document text
            items = [
                ContextItem(
                    content=doc,
                    metadata={
                        "chunk_index": i,
                        "source": rag_result.get("source", "rag"),
                        "rejected_count": len(rag_result.get("rejected_documents", [])),
                    },
                )
                for i, doc in enumerate(selected_docs)
            ]

            elapsed = time.monotonic() - t0
            return build_provider_result(
                provider_id=self.provider_id,
                section_name="rag",
                items=items,
                confidence=confidence,
                priority_weight=self.priority_weight,
                execution_time_s=elapsed,
                section_metadata={
                    "total_retrieved": len(documents),
                    "chunks_used": len(selected_docs),
                    "rejected_documents": rag_result.get("rejected_documents", []),
                    "rag_source": rag_result.get("source", "rag"),
                    "rag_result_dict": rag_result,
                },
            )

        except Exception as exc:
            logger.error("RAGProvider failed: %s", exc, exc_info=True)
            return FailedProviderResult(
                provider_id=self.provider_id,
                priority_weight=self.priority_weight,
                error_detail=str(exc),
                execution_time_s=time.monotonic() - t0,
            )
