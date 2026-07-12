"""
Strongly typed Pydantic models for the Smart Context Engine.

All internal APIs use these models — no raw dicts.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class CompressionLevel(str, Enum):
    """Supported context compression levels."""
    NONE   = "NONE"
    LOW    = "LOW"
    MEDIUM = "MEDIUM"
    HIGH   = "HIGH"
    AUTO   = "AUTO"


class ProviderStatus(str, Enum):
    """Execution status of a context provider."""
    SUCCESS  = "SUCCESS"
    SKIPPED  = "SKIPPED"
    FAILED   = "FAILED"
    DEGRADED = "DEGRADED"   # partial result available


class ContextSectionName(str, Enum):
    """Standard section names in the assembled context package."""
    SYSTEM       = "system"
    PROFILE      = "profile"
    CONVERSATION = "conversation"
    WORKSPACE    = "workspace"
    NAVIGATION   = "navigation"
    RAG          = "rag"


# ---------------------------------------------------------------------------
# Primitive context units
# ---------------------------------------------------------------------------

class ContextItem(BaseModel):
    """
    A single atomic unit of context.

    Attributes:
        content:    The raw text content of this item.
        citation:   Optional source citation (e.g. "[Source: handbook.pdf, Page: 3]").
        metadata:   Arbitrary key-value pairs from the source provider.
        priority:   Higher values are ordered first after prioritization.
        token_count: Approximate token count for budget management.
    """
    content:     str
    citation:    Optional[str]          = None
    metadata:    Dict[str, Any]         = Field(default_factory=dict)
    priority:    float                  = 0.0
    token_count: int                    = 0


class ContextSection(BaseModel):
    """
    A named group of context items from a single provider.

    Attributes:
        name:        Section identifier (matches ContextSectionName).
        provider_id: Which provider produced this section.
        items:       Ordered list of ContextItem objects.
        total_tokens: Sum of token_count across all items.
        metadata:   Section-level metadata (e.g. validation_status for navigation).
    """
    name:         str
    provider_id:  str
    items:        List[ContextItem]     = Field(default_factory=list)
    total_tokens: int                   = 0
    metadata:     Dict[str, Any]        = Field(default_factory=dict)

    def formatted_text(self) -> str:
        """Returns the concatenated text of all context items in this section."""
        return "\n\n".join(
            f"{item.citation}\n{item.content}" if item.citation else item.content
            for item in self.items
            if item.content.strip()
        )


# ---------------------------------------------------------------------------
# Provider result
# ---------------------------------------------------------------------------

class ProviderMetadata(BaseModel):
    """
    Metadata describing a provider's execution run.

    Attributes:
        provider_id:      Unique identifier for the provider.
        status:           Execution status.
        execution_time_s: Wall-clock execution time in seconds.
        confidence:       Provider's self-assessed confidence in its output (0.0–1.0).
        priority_weight:  Base priority weight of this provider type.
        skip_reason:      Why this provider was skipped (if applicable).
        error_detail:     Error description (if status=FAILED).
    """
    provider_id:       str
    status:            ProviderStatus  = ProviderStatus.SUCCESS
    execution_time_s:  float           = 0.0
    confidence:        float           = 1.0
    priority_weight:   float           = 0.0
    skip_reason:       Optional[str]   = None
    error_detail:      Optional[str]   = None


class ProviderResult(BaseModel):
    """
    Complete output from a single context provider.

    Attributes:
        metadata:   Execution metadata for this provider.
        section:    The context section produced (None if status != SUCCESS).
        nav_early_exit: If set, navigation returned an early-exit signal
                        (e.g. "ambiguous", "invalid_destination").
                        chat.py checks this before proceeding to Gemini.
        nav_ctx_dict: Optional dict of the full navigation context.
    """
    metadata:       ProviderMetadata
    section:        Optional[ContextSection] = None
    nav_early_exit: Optional[str]            = None   # non-None → bypass Gemini
    nav_ctx_dict:   Optional[Dict[str, Any]] = None


# ---------------------------------------------------------------------------
# Assembled context package
# ---------------------------------------------------------------------------

class ContextPackage(BaseModel):
    """
    The fully assembled, prioritized, deduplicated, compressed context package
    returned by the Context Orchestrator.

    Attributes:
        sections:           Ordered list of context sections.
        compression_level:  Which compression was applied.
        total_tokens:       Total token count across all sections.
        navigation_data:    Structured navigation data (for prompt injection).
        nav_early_exit:     If non-None, signals to chat.py to short-circuit.
        provider_results:   Raw provider results (for diagnostics).
    """
    sections:           List[ContextSection]    = Field(default_factory=list)
    compression_level:  CompressionLevel        = CompressionLevel.NONE
    total_tokens:       int                     = 0
    navigation_data:    Optional[Dict[str, Any]] = None
    nav_early_exit:     Optional[str]            = None
    nav_early_exit_msg: Optional[str]            = None
    provider_results:   List[ProviderResult]    = Field(default_factory=list)

    def get_section(self, name: str) -> Optional[ContextSection]:
        """Retrieves a section by name, or None if absent."""
        for section in self.sections:
            if section.name == name:
                return section
        return None

    def get_text(self, name: str) -> str:
        """Returns formatted text for a named section, or empty string."""
        section = self.get_section(name)
        return section.formatted_text() if section else ""


# ---------------------------------------------------------------------------
# Compression result
# ---------------------------------------------------------------------------

class CompressionResult(BaseModel):
    """
    Statistics about a compression operation.

    Attributes:
        original_tokens:   Token count before compression.
        final_tokens:      Token count after compression.
        compression_ratio: final / original (1.0 = no compression).
        level_applied:     Which compression level was used.
        sections_affected: Which section names were compressed.
    """
    original_tokens:   int
    final_tokens:      int
    compression_ratio: float                = 1.0
    level_applied:     CompressionLevel     = CompressionLevel.NONE
    sections_affected: List[str]            = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Token budget allocation
# ---------------------------------------------------------------------------

class BudgetAllocation(BaseModel):
    """
    Token budget allocated per context section.

    Attributes:
        allocations:     Section name → token limit mapping.
        total_budget:    Sum of all allocations.
        overflow:        True if total content exceeded the budget.
        overflow_by:     How many tokens over budget (0 if no overflow).
    """
    allocations:  Dict[str, int] = Field(default_factory=dict)
    total_budget: int             = 0
    overflow:     bool            = False
    overflow_by:  int             = 0


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------

class ProviderDiagnostic(BaseModel):
    """Per-provider diagnostic record."""
    provider_id:      str
    status:           ProviderStatus
    execution_time_s: float
    tokens_produced:  int
    priority_score:   float
    confidence:       float
    skip_reason:      Optional[str] = None
    error_detail:     Optional[str] = None


class PipelineDiagnostics(BaseModel):
    """
    Structured diagnostics for the full context pipeline execution.

    Captured by ContextOrchestrator and passed to chat.py for
    inclusion in the developer diagnostics payload.
    """
    providers_executed:     List[str]                = Field(default_factory=list)
    providers_skipped:      Dict[str, str]           = Field(default_factory=dict)
    provider_diagnostics:   List[ProviderDiagnostic] = Field(default_factory=list)
    priority_scores:        Dict[str, float]         = Field(default_factory=dict)
    token_usage_per_section:Dict[str, int]           = Field(default_factory=dict)
    total_tokens_before:    int                      = 0
    total_tokens_after:     int                      = 0
    compression_result:     Optional[CompressionResult] = None
    duplicates_removed:     int                      = 0
    pipeline_time_s:        float                    = 0.0
    context_size_chars:     int                      = 0
    budget_allocation:      Optional[BudgetAllocation] = None
    timestamp:              datetime                 = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Context request (input to the orchestrator)
# ---------------------------------------------------------------------------

class ContextRequest(BaseModel):
    """
    Input payload passed from chat.py to ContextOrchestrator.

    Providers receive a ContextRequest and extract what they need.
    """
    query:                    str
    intent:                   str
    session_id:               Optional[str]           = None
    current_student:          Optional[Dict[str, Any]] = None
    routing_confidence:       float                   = 1.0
    requires_rag:             bool                    = False
    requires_navigation:      bool                    = False
    requires_workspace:       bool                    = False
    requires_conversation:    bool                    = True
    current_location_node_id: Optional[str]           = None
    current_dest_node_id:     Optional[str]           = None
    accessibility_mode:       bool                    = False
    compression_level:        CompressionLevel        = CompressionLevel.AUTO
    history:                  Optional[list]          = None  # pre-fetched or None
