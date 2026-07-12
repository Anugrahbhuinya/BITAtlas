import logging
import re
from typing import Optional, List
from pydantic import BaseModel

logger = logging.getLogger("intent_router")

from app.core.config import ROUTING_CONFIDENCE_THRESHOLD
GEMINI_THRESHOLD = ROUTING_CONFIDENCE_THRESHOLD

# Centralized Routing Table (one source of truth)
ROUTING_TABLE = {
    "Greeting": "Local Response",
    "Campus Information": "Hybrid RAG",
    "Notice Retrieval": "Hybrid RAG",
    "Academic Calendar": "Calendar Service",
    "Navigation": "Navigation Engine",
    "Student Workspace": "Workspace Service",
    "Uploaded Document QA": "Hybrid RAG",
    "Website QA": "Website Knowledge",
    "Programming Help": "Gemini",
    "General Academic Concept": "Gemini",
    "AI / ML Concept": "Gemini",
    "Engineering Concept": "Gemini",
    "Reasoning": "Gemini",
    "Comparison": "Gemini",
    "Summarization": "Gemini",
    "Explanation": "Gemini",
    "Conversation Follow-up": "Conversation Memory",
    "Unknown": "Hybrid Strategy"
}

class RoutingDecision(BaseModel):
    intent: str
    primary_service: str
    fallback_service: str
    confidence: float
    reason: str
    requires_rag: bool
    requires_gemini: bool
    requires_navigation: bool
    requires_workspace: bool
    requires_conversation_memory: bool

def is_greeting(query: str) -> bool:
    query_lower = query.lower().strip().replace("?", "").replace(".", "").replace("!", "")
    greetings = {
        "hello", "hi", "hey", "good morning", "good afternoon", "good evening", 
        "who are you", "what is your name", "greet", "greetings", "yo"
    }
    words = query_lower.split()
    if not words:
        return False
    if words[0] in greetings and len(words) <= 3:
        return True
    return query_lower in greetings

def classify_intent(query: str, history: list | None = None) -> str:
    query_clean = query.strip()
    query_lower = query_clean.lower()
    
    # 1. Greeting
    if is_greeting(query_lower):
        return "Greeting"
        
    # 2. Conversation Follow-up
    if history:
        for pronoun in ["its", "it", "they", "them", "this", "that"]:
            pattern = r"\b" + re.escape(pronoun) + r"\b"
            if re.search(pattern, query_lower):
                if len(query_lower.split()) < 8:
                    return "Conversation Follow-up"

    # 3. Summarization
    if any(k in query_lower for k in ["summarize", "summary", "overview", "tl;dr", "short version", "synopsis"]):
        if any(k in query_lower for k in ["pdf", "document", "file", "uploaded"]):
            return "Uploaded Document QA"
        return "Summarization"

    # 4. Comparison
    if any(k in query_lower for k in ["compare", "comparison", "vs", "versus", "difference between", "different between", "pros and cons", "advantages", "disadvantages"]):
        return "Comparison"

    # 5. Explanation
    if any(k in query_lower for k in ["explain", "explanation", "what is the meaning of", "clarify", "define", "what is a", "what is an"]):
        if any(k in query_lower for k in ["cnn", "resnet", "neural network", "deep learning", "machine learning", "gradient descent", "transformer", "backpropagation", "tcp", "udp", "list", "tuple", "vector", "matrix", "dsa", "dbms", "normalization", "sql", "java", "python", "c++", "data structures", "algorithms"]):
            pass
        else:
            return "Explanation"

    # 6. Navigation
    if any(k in query_lower for k in ["route", "where is", "how to get", "walking", "distance", "location", "landmark", "leave for", "departure", "take me to", "take me back", "reach", "how far", "on the way", "map", "directions", "hostel 5", "library"]):
        return "Navigation"

    # 7. Academic Calendar
    if any(k in query_lower for k in ["calendar", "holiday", "when is end sem", "end sem", "start semester", "mid sem", "session start", "exam dates", "vacation"]):
        return "Academic Calendar"

    # 8. Notice Retrieval
    if any(k in query_lower for k in ["notice", "circular", "announcement", "latest notice", "examination notice"]):
        return "Notice Retrieval"

    # 9. Student Workspace (Assignments, notes, timetable, reminders, etc.)
    if any(k in query_lower for k in ["assignment", "assignments", "task", "todo", "planner", "deadline", "schedule today", "my workspace", "my assignments", "my courses", "my timetable", "my notes", "my reminders", "my uploaded"]):
        if any(k in query_lower for k in ["pdf", "pdfs", "document", "uploaded"]):
            return "Uploaded Document QA"
        return "Student Workspace"

    # 10. Uploaded Document QA
    if any(k in query_lower for k in ["pdf", "pdfs", "document", "uploaded file", "paper", "handbook"]):
        return "Uploaded Document QA"

    # 11. Website QA
    if any(k in query_lower for k in ["website", "site info", "page content", "webpage"]):
        return "Website QA"

    # 12. AI / ML Concept
    ai_keywords = [
        "cnn", "resnet", "neural network", "deep learning", "machine learning", 
        "gradient descent", "transformer", "backpropagation", "supervised learning", 
        "unsupervised learning", "overfitting", "underfitting", "nlp", "llm", 
        "loss function", "activation function", "weights", "biases", "epochs"
    ]
    if any(k in query_lower for k in ai_keywords):
        return "AI / ML Concept"

    # 13. Programming Help
    prog_keywords = [
        "python", "java", "c++", "list vs tuple", "list", "tuple", "loop", 
        "function", "variable", "syntax", "compile", "debug", "array", 
        "pointer", "recursion", "object oriented", "inheritance", "polymorphism"
    ]
    if any(k in query_lower for k in prog_keywords):
        return "Programming Help"

    # 14. Engineering Concept
    eng_keywords = [
        "tcp", "udp", "dbms", "normalization", "dsa", "data structures", 
        "algorithms", "operating system", "computer networks", "sql", 
        "binary search", "sorting", "hash table"
    ]
    if any(k in query_lower for k in eng_keywords):
        return "Engineering Concept"

    # 15. Reasoning
    if any(k in query_lower for k in ["why", "how does", "logic", "prove", "math", "derive", "solve"]):
        return "Reasoning"

    # 16. General Academic Concept
    academic_keywords = [
        "semester", "credits", "cgpa", "gpa", "course registration", 
        "degree", "department", "probation"
    ]
    if any(k in query_lower for k in academic_keywords):
        return "General Academic Concept"

    # 17. Campus Information
    campus_keywords = [
        "hostel", "mess", "canteen", "library", "timings", "placement", 
        "fees", "hostel fee", "admission", "bit mesra", "deans", "clubs", 
        "sports", "gym", "dispensary", "placement office", "dean office",
        "scholarship", "scholarships", "buildings", "campus map", "campus facilities"
    ]
    if any(k in query_lower for k in campus_keywords):
        return "Campus Information"

    return "Unknown"

def make_routing_decision(query: str, rag_result: dict | None = None, history: list | None = None) -> RoutingDecision:
    intent = classify_intent(query, history)
    primary_service = ROUTING_TABLE.get(intent, "Gemini")
    
    # Defaults
    fallback_service = "Gemini" if primary_service != "Gemini" else "Direct RAG Fallback"
    confidence = 1.0
    reason = f"Intent '{intent}' mapped to service '{primary_service}'"
    
    # Check RAG confidence override if primary is RAG
    if primary_service in ["Hybrid RAG", "Website Knowledge", "Hybrid Strategy", "Calendar Service", "Workspace Service"]:
        if rag_result:
            # Check if there are valid documents retrieved
            docs = rag_result.get("documents", [])
            if not docs:
                primary_service = "Gemini"
                reason = "No relevant documents found in knowledge base, falling back to Gemini"
            else:
                confidence = rag_result.get("confidence", 1.0)
                # Lower score = better confidence (Chroma distance)
                if confidence >= GEMINI_THRESHOLD:
                    primary_service = "Gemini"
                    reason = f"RAG confidence {confidence:.4f} is weak, falling back to Gemini"
        else:
            primary_service = "Gemini"
            reason = "No RAG result available, falling back to Gemini"
            
    # Gating and flag resolution
    requires_rag = (primary_service in ["Hybrid RAG", "Website Knowledge", "Hybrid Strategy", "Calendar Service", "Workspace Service"])
    requires_gemini = (primary_service == "Gemini")
    requires_navigation = (intent == "Navigation")
    requires_workspace = (intent in ["Student Workspace", "Student Dashboard"])
    requires_conversation_memory = (intent == "Conversation Follow-up")
    
    return RoutingDecision(
        intent=intent,
        primary_service=primary_service,
        fallback_service=fallback_service,
        confidence=confidence,
        reason=reason,
        requires_rag=requires_rag,
        requires_gemini=requires_gemini,
        requires_navigation=requires_navigation,
        requires_workspace=requires_workspace,
        requires_conversation_memory=requires_conversation_memory
    )

def should_use_gemini(query: str, rag_result: dict | None) -> bool:
    """
    Decides whether to route the query to Gemini or use the direct RAG response.
    Returns True if Gemini should be used, False if RAG should be used directly.
    """
    decision = make_routing_decision(query, rag_result)
    return decision.requires_gemini
