import logging

logger = logging.getLogger("intent_router")

GEMINI_KEYWORDS = [
    "compare",
    "comparison",
    "difference",
    "different",
    "pros and cons",
    "advantages",
    "disadvantages",
    "recommend",
    "recommendation",
    "which is better",
    "better option",
    "best hostel",
    "best department",
    "best club",
    "best",
    "summarize",
    "summary",
    "overview",
    "explain",
    "guide",
    "advice",
    "suggest",
    "help me choose",
    "first-year",
    "joining",
    "know before"
]

GEMINI_THRESHOLD = 0.45

import re

def should_use_gemini(query: str, rag_result: dict | None) -> bool:
    """
    Decides whether to route the query to Gemini or use the direct RAG response.
    Returns True if Gemini should be used, False if RAG should be used directly.
    """
    if not query:
        print("\n========== INTENT ROUTER ==========")
        print("Query: [Empty Query]")
        print("Matched intent keyword: None")
        print("Final decision: Gemini")
        return True
        
    query_lower = query.lower()
    matched_keyword = None
    
    # Case 1: Intent requires Gemini (query contains specific keywords)
    for kw in GEMINI_KEYWORDS:
        if kw in query_lower:
            matched_keyword = kw
            break
            
    # Conversational follow-up detection:
    if not matched_keyword:
        for pronoun in ["its", "it", "they", "them", "this", "that"]:
            pattern = r"\b" + re.escape(pronoun) + r"\b"
            if re.search(pattern, query_lower):
                matched_keyword = f"conversational pronoun '{pronoun}'"
                break
            
    decision = True
    if matched_keyword:
        decision = True
    elif rag_result is None:
        decision = True
    else:
        confidence = rag_result.get("confidence")
        if confidence is None:
            decision = True
        elif confidence < GEMINI_THRESHOLD:
            decision = False
        else:
            decision = True
            
    print("\n========== INTENT ROUTER ==========")
    print(f"Query: {query}")
    print(f"Matched intent keyword: {matched_keyword}")
    print(f"Final decision: {'Gemini' if decision else 'Direct RAG'}")
    
    if matched_keyword:
        logger.info(f"Routing to Gemini: Query matched intent keyword/pronoun '{matched_keyword}'")
        return True
        
    # Case 4: rag_result is None
    if rag_result is None:
        logger.info("Routing to Gemini: No RAG result found")
        return True
        
    confidence = rag_result.get("confidence")
    if confidence is None:
        logger.info("Routing to Gemini: RAG result exists but confidence is missing")
        return True
        
    # Remember: Lower score = better confidence
    # Case 2: rag_result exists and confidence < GEMINI_THRESHOLD -> Direct RAG
    if confidence < GEMINI_THRESHOLD:
        logger.info(f"Routing to RAG directly: RAG confidence {confidence:.4f} is strong/better than threshold {GEMINI_THRESHOLD}")
        return False
        
    # Case 3: rag_result exists and confidence >= GEMINI_THRESHOLD -> Gemini
    logger.info(f"Routing to Gemini: RAG confidence {confidence:.4f} is weak/worse than or equal to threshold {GEMINI_THRESHOLD}")
    return True
