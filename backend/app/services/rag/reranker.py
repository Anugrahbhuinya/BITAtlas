import logging
import time
from typing import List, Tuple
from langchain_core.documents import Document

logger = logging.getLogger("rag_reranker")

_reranker_model = None
_reranker_tokenizer = None
_reranker_loaded = False

def load_reranker():
    global _reranker_model, _reranker_tokenizer, _reranker_loaded
    if _reranker_loaded:
        return _reranker_model, _reranker_tokenizer
        
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        import torch
        
        model_name = "cross-encoder/ms-marco-MiniLM-L-2-v2"
        logger.info(f"Loading Cross-Encoder reranker model: {model_name}")
        t0 = time.time()
        
        # Load tokenizer and model with CPU mapping
        _reranker_tokenizer = AutoTokenizer.from_pretrained(model_name)
        _reranker_model = AutoModelForSequenceClassification.from_pretrained(model_name)
        _reranker_loaded = True
        logger.info(f"Cross-Encoder model loaded successfully in {time.time() - t0:.2f}s")
    except Exception as e:
        logger.error(f"Failed to load Cross-Encoder model: {e}. Will fallback to heuristic ranking.")
        _reranker_loaded = True # Prevent repeated attempts
        
    return _reranker_model, _reranker_tokenizer

import threading
from collections import OrderedDict

# Thread-safe LRU cache for cross-encoder scores
_rerank_cache = OrderedDict()
_rerank_cache_lock = threading.Lock()
MAX_CACHE_SIZE = 1000

def get_cached_score(query: str, doc_content: str) -> float | None:
    key = (query, doc_content)
    with _rerank_cache_lock:
        if key in _rerank_cache:
            # Move to end (MRU)
            val = _rerank_cache.pop(key)
            _rerank_cache[key] = val
            return val
    return None

def set_cached_score(query: str, doc_content: str, score: float):
    key = (query, doc_content)
    with _rerank_cache_lock:
        if key in _rerank_cache:
            _rerank_cache.pop(key)
        _rerank_cache[key] = score
        if len(_rerank_cache) > MAX_CACHE_SIZE:
            _rerank_cache.popitem(last=False)


def rerank_documents(query: str, candidates: List[Tuple[Document, float]], k: int = 5) -> List[Tuple[Document, float]]:
    """
    Reranks candidate documents using a Cross-Encoder with LRU caching of scores.
    If the model fails to load or execute, returns candidates sorted by their initial scores.
    """
    if not candidates:
        return []
        
    model, tokenizer = load_reranker()
    if model is None or tokenizer is None:
        logger.info("Reranking: No Cross-Encoder model available, using original scores.")
        return [(doc, score, 0.0) for doc, score in sorted(candidates, key=lambda x: x[1])[:k]]
        
    try:
        import torch
        t0 = time.time()
        
        # 1. Resolve scores using LRU cache
        scores = [0.0] * len(candidates)
        pairs_to_compute = []
        indices_to_compute = []
        
        for idx, (doc, _) in enumerate(candidates):
            cached_val = get_cached_score(query, doc.page_content)
            if cached_val is not None:
                scores[idx] = cached_val
            else:
                pairs_to_compute.append([query, doc.page_content])
                indices_to_compute.append(idx)
                
        # 2. Compute scores for cache misses
        if pairs_to_compute:
            inputs = tokenizer(pairs_to_compute, padding=True, truncation=True, return_tensors="pt", max_length=512)
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits.squeeze(-1)
                if logits.dim() == 0:
                    computed_scores = [logits.item()]
                else:
                    computed_scores = logits.tolist()
                    
            for i, score_val in enumerate(computed_scores):
                idx = indices_to_compute[i]
                scores[idx] = score_val
                # Cache the computed score
                set_cached_score(query, candidates[idx][0].page_content, score_val)
                
        # Combine initial scores with Cross-Encoder scores
        reranked = []
        for idx, (doc, initial_score) in enumerate(candidates):
            raw_score = scores[idx]
            # Sigmoid normalization to bring score to [0, 1] range
            import math
            try:
                sigmoid_score = 1.0 / (1.0 + math.exp(-raw_score))
            except OverflowError:
                sigmoid_score = 0.0 if raw_score < 0 else 1.0
            
            # Blend 60% Cross-Encoder, 40% original score (which includes metadata & keyword boosts)
            # original score is a distance (lower is better), so we use (1.0 - initial_score)
            blended_similarity = (sigmoid_score * 0.60) + ((1.0 - initial_score) * 0.40)
            final_distance = 1.0 - blended_similarity
            
            reranked.append((doc, final_distance, raw_score))
            
        # Sort by final_distance ascending
        reranked.sort(key=lambda x: x[1])
        
        logger.info(f"Cross-Encoder reranked {len(candidates)} candidates ({len(pairs_to_compute)} computed, {len(candidates) - len(pairs_to_compute)} cached) in {time.time() - t0:.4f}s")
        return [(doc, score, raw_score) for doc, score, raw_score in reranked[:k]]
        
    except Exception as e:
        logger.error(f"Error during Cross-Encoder reranking: {e}", exc_info=True)
        return [(doc, score, 0.0) for doc, score in sorted(candidates, key=lambda x: x[1])[:k]]
