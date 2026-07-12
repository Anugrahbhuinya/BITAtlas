import contextvars
import logging
import time
from typing import Dict, Any, List, Optional

# ANSI Escape Codes for console coloring
BLUE = "\033[94m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
RESET = "\033[0m"

logger = logging.getLogger("rag.debug")

class RAGDebugStore:
    """
    Telemetry and observability store for RAG pipeline debug metrics.
    Collected on a per-request basis.
    """
    def __init__(self) -> None:
        self.original_query: str = ""
        self.normalized_query: str = ""
        self.detected_intent: str = ""
        self.query_category: str = ""
        self.synonyms_expanded: List[str] = []
        
        # Latencies (in milliseconds)
        self.embedding_time_ms: float = 0.0
        self.vector_search_time_ms: float = 0.0
        self.metadata_filtering_time_ms: float = 0.0
        self.cross_encoder_time_ms: float = 0.0
        self.total_retrieval_latency_ms: float = 0.0
        self.prompt_builder_time_ms: float = 0.0
        self.llm_time_ms: float = 0.0
        self.formatting_time_ms: float = 0.0
        self.total_time_ms: float = 0.0
        
        # Retrieved Candidates & Ranking Decisions
        self.candidates: List[Dict[str, Any]] = []
        self.ranking_decisions: List[Dict[str, Any]] = []
        
        # Context Builder stats
        self.selected_chunks: List[str] = []
        self.rejected_chunks: List[str] = []
        self.duplicate_removal_count: int = 0
        self.metadata_filtering_details: str = ""
        self.token_count: int = 0
        self.context_length: int = 0
        self.final_prompt_size: int = 0
        
        # Prompt Builder structure
        self.system_prompt: str = ""
        self.retrieved_context: str = ""
        self.conversation_memory: str = ""
        self.knowledge_sources: List[str] = []
        self.prompt_length: int = 0
        self.estimated_tokens: int = 0
        
        # LLM Details
        self.llm_model: str = ""
        self.llm_response_time_ms: float = 0.0
        self.completion_tokens: int = 0
        self.prompt_tokens: int = 0
        self.total_tokens: int = 0
        self.generation_latency_ms: float = 0.0
        
        # Response details
        self.final_answer: str = ""
        self.sources_used: List[str] = []
        self.confidence: float = 0.0
        self.fallback_used: bool = False
        self.hallucination_warning: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Returns the collected debug metrics in a serializable dictionary format."""
        return {
            "query_info": {
                "original_query": self.original_query,
                "normalized_query": self.normalized_query,
                "detected_intent": self.detected_intent,
                "query_category": self.query_category,
                "synonyms_expanded": self.synonyms_expanded,
            },
            "latencies_ms": {
                "embedding": round(self.embedding_time_ms, 2),
                "vector_search": round(self.vector_search_time_ms, 2),
                "metadata_filtering": round(self.metadata_filtering_time_ms, 2),
                "cross_encoder": round(self.cross_encoder_time_ms, 2),
                "total_retrieval": round(self.total_retrieval_latency_ms, 2),
                "prompt_builder": round(self.prompt_builder_time_ms, 2),
                "llm": round(self.llm_time_ms, 2),
                "formatting": round(self.formatting_time_ms, 2),
                "total": round(self.total_time_ms, 2),
            },
            "candidates": self.candidates,
            "ranking_decisions": self.ranking_decisions,
            "context_builder": {
                "selected_chunks_count": len(self.selected_chunks),
                "rejected_chunks_count": len(self.rejected_chunks),
                "duplicate_removal_count": self.duplicate_removal_count,
                "metadata_filtering_details": self.metadata_filtering_details,
                "token_count": self.token_count,
                "context_length": self.context_length,
                "final_prompt_size": self.final_prompt_size,
            },
            "prompt_builder": {
                "system_prompt_size": len(self.system_prompt),
                "retrieved_context_size": len(self.retrieved_context),
                "conversation_memory_size": len(self.conversation_memory),
                "knowledge_sources": self.knowledge_sources,
                "prompt_length": self.prompt_length,
                "estimated_tokens": self.estimated_tokens,
            },
            "llm": {
                "model": self.llm_model,
                "response_time_ms": round(self.llm_response_time_ms, 2),
                "completion_tokens": self.completion_tokens,
                "prompt_tokens": self.prompt_tokens,
                "total_tokens": self.total_tokens,
                "generation_latency_ms": round(self.generation_latency_ms, 2),
            },
            "response": {
                "final_answer": self.final_answer,
                "sources_used": self.sources_used,
                "confidence": round(self.confidence, 4),
                "fallback_used": self.fallback_used,
                "hallucination_warning": self.hallucination_warning,
            }
        }

    def log_report(self) -> None:
        """Logs a beautiful colorized diagnostic report to the python root logger."""
        report = (
            f"\n{BOLD}{CYAN}============================================================{RESET}\n"
            f"{BOLD}{CYAN}               RAG PIPELINE DEBUG REPORT{RESET}\n"
            f"{BOLD}{CYAN}============================================================{RESET}\n"
            f"{BOLD}{BLUE}[Query Processing]{RESET}\n"
            f"  {BOLD}Original Query:{RESET}   {self.original_query}\n"
            f"  {BOLD}Normalized Query:{RESET} {self.normalized_query}\n"
            f"  {BOLD}Detected Intent:{RESET}  {self.detected_intent}\n"
            f"  {BOLD}Category:{RESET}         {self.query_category}\n"
            f"  {BOLD}Synonyms Expanded:{RESET} {', '.join(self.synonyms_expanded) if self.synonyms_expanded else 'None'}\n\n"
            
            f"{BOLD}{BLUE}[Retrieval Latencies]{RESET}\n"
            f"  {BOLD}Embedding Generation:{RESET} {CYAN}{self.embedding_time_ms:.2f} ms{RESET}\n"
            f"  {BOLD}Vector Search:{RESET}        {CYAN}{self.vector_search_time_ms:.2f} ms{RESET}\n"
            f"  {BOLD}Metadata Filtering:{RESET}   {CYAN}{self.metadata_filtering_time_ms:.2f} ms{RESET}\n"
            f"  {BOLD}Cross Encoder Rerank:{RESET} {CYAN}{self.cross_encoder_time_ms:.2f} ms{RESET}\n"
            f"  {BOLD}Total Retrieval:{RESET}      {GREEN}{self.total_retrieval_latency_ms:.2f} ms{RESET}\n\n"
        )
        
        if self.candidates:
            report += f"{BOLD}{BLUE}[Retrieved Candidates]{RESET}\n"
            for c in self.candidates:
                report += (
                    f"  {BOLD}Rank {c['rank']}:{RESET} {c['title']} ({c['source_type']})\n"
                    f"    - Category:       {c['category']}\n"
                    f"    - Raw Score:      {c['raw_score']:.4f} (Distance)\n"
                    f"    - Cross-Encoder:  {c['ce_score']:.4f}\n"
                    f"    - Combined Score: {c['combined_score']:.4f}\n"
                    f"    - Chunk ID:       {c['chunk_id']}\n"
                    f"    - Version:        v{c['version']}\n"
                    f"    - Explanation:    {YELLOW}{c['explanation']}{RESET}\n"
                )
            report += "\n"
            
        report += (
            f"{BOLD}{BLUE}[Context & Prompt Builder]{RESET}\n"
            f"  {BOLD}Selected Chunks:{RESET}     {len(self.selected_chunks)}\n"
            f"  {BOLD}Rejected Chunks:{RESET}     {len(self.rejected_chunks)}\n"
            f"  {BOLD}Duplicate Removal:{RESET}   {self.duplicate_removal_count}\n"
            f"  {BOLD}Knowledge Sources:{RESET}   {', '.join(self.knowledge_sources) if self.knowledge_sources else 'None'}\n"
            f"  {BOLD}Final Prompt Size:{RESET}   {self.prompt_length} chars ({self.estimated_tokens} estimated tokens)\n\n"
            
            f"{BOLD}{BLUE}[LLM Details]{RESET}\n"
            f"  {BOLD}Model Called:{RESET}        {self.llm_model if self.llm_model else 'N/A'}\n"
            f"  {BOLD}Response Time:{RESET}       {CYAN}{self.llm_response_time_ms:.2f} ms{RESET}\n"
            f"  {BOLD}Prompt Tokens:{RESET}       {self.prompt_tokens}\n"
            f"  {BOLD}Completion Tokens:{RESET}   {self.completion_tokens}\n"
            f"  {BOLD}Total Tokens:{RESET}        {self.total_tokens}\n\n"
            
            f"{BOLD}{BLUE}[Response Details]{RESET}\n"
            f"  {BOLD}Confidence Score:{RESET}    {self.confidence:.4f}\n"
            f"  {BOLD}Fallback Mode Used:{RESET}  {YELLOW if self.fallback_used else GREEN}{self.fallback_used}{RESET}\n"
            f"  {BOLD}Hallucination Alert:{RESET} {RED if self.hallucination_warning else GREEN}{self.hallucination_warning}{RESET}\n"
            f"  {BOLD}Final Answer Snippet:{RESET} {self.final_answer[:120]}...\n\n"
            
            f"{BOLD}{GREEN}TOTAL END-TO-END PIPELINE LATENCY: {self.total_time_ms:.2f} ms{RESET}\n"
            f"{BOLD}{CYAN}============================================================{RESET}\n"
        )
        # Log colorized output directly via standard root logging formatting
        logger.info(report)

# Global ContextVar to store current request telemetry
_rag_debug_context = contextvars.ContextVar("rag_debug_context", default=None)

def get_debug_store() -> Optional[RAGDebugStore]:
    """Helper to retrieve the current request's debug store."""
    return _rag_debug_context.get()

def init_debug_store() -> RAGDebugStore:
    """Helper to initialize a new debug store for the current request."""
    store = RAGDebugStore()
    _rag_debug_context.set(store)
    return store
