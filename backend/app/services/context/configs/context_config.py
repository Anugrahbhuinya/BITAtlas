"""
Context Engine Central Configuration

All configurable values are defined here.
No magic numbers anywhere in the context engine.
All values are overridable via environment variables.
"""
import os
from typing import Dict


# ---------------------------------------------------------------------------
# Provider Weights (used by Prioritizer)
# Higher weight = higher base priority before confidence adjustment
# ---------------------------------------------------------------------------
PROVIDER_WEIGHTS: Dict[str, float] = {
    "system":       float(os.getenv("CTX_WEIGHT_SYSTEM",       "1.0")),
    "profile":      float(os.getenv("CTX_WEIGHT_PROFILE",      "0.9")),
    "navigation":   float(os.getenv("CTX_WEIGHT_NAVIGATION",   "0.95")),
    "workspace":    float(os.getenv("CTX_WEIGHT_WORKSPACE",     "0.85")),
    "conversation": float(os.getenv("CTX_WEIGHT_CONVERSATION",  "0.80")),
    "rag":          float(os.getenv("CTX_WEIGHT_RAG",           "0.75")),
}

# Priority scoring formula weights (must sum to 1.0)
PRIORITY_W_ROUTING:     float = float(os.getenv("CTX_PRI_W_ROUTING",    "0.35"))
PRIORITY_W_PROVIDER:    float = float(os.getenv("CTX_PRI_W_PROVIDER",   "0.30"))
PRIORITY_W_FRESHNESS:   float = float(os.getenv("CTX_PRI_W_FRESHNESS",  "0.20"))
PRIORITY_W_RELIABILITY: float = float(os.getenv("CTX_PRI_W_RELIABILITY","0.15"))

# Source reliability scores
SOURCE_RELIABILITY: Dict[str, float] = {
    "system":       1.0,
    "profile":      1.0,
    "navigation":   0.98,
    "workspace":    0.90,
    "conversation": 0.85,
    "rag":          0.80,
}

# ---------------------------------------------------------------------------
# Token Budget (approximate token allocation per context section)
# Adjust via environment variables without code changes.
# ---------------------------------------------------------------------------
TOKEN_BUDGET: Dict[str, int] = {
    "system":         int(os.getenv("CTX_BUDGET_SYSTEM",       "500")),
    "profile":        int(os.getenv("CTX_BUDGET_PROFILE",      "200")),
    "conversation":   int(os.getenv("CTX_BUDGET_CONVERSATION", "800")),
    "workspace":      int(os.getenv("CTX_BUDGET_WORKSPACE",    "600")),
    "navigation":     int(os.getenv("CTX_BUDGET_NAVIGATION",   "400")),
    "rag":            int(os.getenv("CTX_BUDGET_RAG",         "1200")),
    "prompt_reserve": int(os.getenv("CTX_BUDGET_PROMPT_RESERVE","300")),
}

# Total token limit for all context combined (before the prompt itself)
TOTAL_CONTEXT_TOKEN_LIMIT: int = int(os.getenv("CTX_TOTAL_TOKEN_LIMIT", "3500"))

# Overflow resolution priority: which sections to compress/trim first
OVERFLOW_RESOLUTION_ORDER = [
    "conversation",
    "workspace",
    "navigation",
    "rag",
    "profile",
    # "system" is never compressed
]

# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------
DEDUP_SIMILARITY_THRESHOLD: float = float(os.getenv("CTX_DEDUP_THRESHOLD", "0.85"))
DEDUP_EXACT_ENABLED:        bool   = os.getenv("CTX_DEDUP_EXACT", "True").lower() == "true"
DEDUP_NEAR_ENABLED:         bool   = os.getenv("CTX_DEDUP_NEAR",  "True").lower() == "true"

# ---------------------------------------------------------------------------
# Compression
# ---------------------------------------------------------------------------
COMPRESSION_AUTO_THRESHOLD_LOW:    float = float(os.getenv("CTX_COMPRESS_LOW",    "0.60"))  # below: no compression
COMPRESSION_AUTO_THRESHOLD_MEDIUM: float = float(os.getenv("CTX_COMPRESS_MEDIUM", "0.85"))  # below: MEDIUM
COMPRESSION_AUTO_THRESHOLD_HIGH:   float = float(os.getenv("CTX_COMPRESS_HIGH",   "1.00"))  # at or above: HIGH

# Max conversation turns to keep at each compression level
COMPRESSION_CONVERSATION_TURNS_LOW:    int = int(os.getenv("CTX_COMPRESS_CONV_LOW",    "6"))
COMPRESSION_CONVERSATION_TURNS_MEDIUM: int = int(os.getenv("CTX_COMPRESS_CONV_MEDIUM", "4"))
COMPRESSION_CONVERSATION_TURNS_HIGH:   int = int(os.getenv("CTX_COMPRESS_CONV_HIGH",   "2"))

# Max RAG chunks to keep at each compression level
COMPRESSION_RAG_CHUNKS_LOW:    int = int(os.getenv("CTX_COMPRESS_RAG_LOW",    "5"))
COMPRESSION_RAG_CHUNKS_MEDIUM: int = int(os.getenv("CTX_COMPRESS_RAG_MEDIUM", "3"))
COMPRESSION_RAG_CHUNKS_HIGH:   int = int(os.getenv("CTX_COMPRESS_RAG_HIGH",   "1"))

# ---------------------------------------------------------------------------
# Provider Feature Flags
# ---------------------------------------------------------------------------
PROVIDER_ENABLED: Dict[str, bool] = {
    "system":       os.getenv("CTX_PROVIDER_SYSTEM",       "True").lower() == "true",
    "profile":      os.getenv("CTX_PROVIDER_PROFILE",      "True").lower() == "true",
    "conversation": os.getenv("CTX_PROVIDER_CONVERSATION", "True").lower() == "true",
    "rag":          os.getenv("CTX_PROVIDER_RAG",          "True").lower() == "true",
    "workspace":    os.getenv("CTX_PROVIDER_WORKSPACE",    "True").lower() == "true",
    "navigation":   os.getenv("CTX_PROVIDER_NAVIGATION",   "True").lower() == "true",
}

# ---------------------------------------------------------------------------
# Conversation Memory
# ---------------------------------------------------------------------------
MAX_CONVERSATION_TURNS: int = int(os.getenv("CTX_MAX_CONV_TURNS", "6"))

# ---------------------------------------------------------------------------
# RAG
# ---------------------------------------------------------------------------
MAX_RAG_CHUNKS_NAVIGATION: int = int(os.getenv("CTX_MAX_RAG_NAV_CHUNKS", "1"))
MAX_RAG_CHUNKS_REASONING:  int = int(os.getenv("CTX_MAX_RAG_REASON_CHUNKS", "7"))
MAX_RAG_CHUNKS_DEFAULT:    int = int(os.getenv("CTX_MAX_RAG_DEFAULT_CHUNKS", "3"))

# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------
DIAGNOSTICS_ENABLED: bool = os.getenv("CTX_DIAGNOSTICS_ENABLED", "True").lower() == "true"
