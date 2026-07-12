import re
from typing import Dict, List, Any

# Configurable Synonym Dictionary
SYNONYMS: Dict[str, str] = {
    "end sem": "end semester",
    "endsem": "end semester",
    "mid sem": "mid semester",
    "midsem": "mid semester",
    "reg": "registration",
    "dept": "department",
    "placement": "placement season",
    "hostel fee": "hostel fees",
}

# Stop, Question, and Filler Words to remove for semantic focus
STOP_WORDS = {
    "when", "what", "how", "who", "where", "which", "why", "is", "are", "the", 
    "a", "an", "do", "does", "did", "can", "could", "would", "should", "of", 
    "in", "to", "for", "on", "at", "by", "from", "with", "about", "please", 
    "tell", "me", "show", "get", "give", "find", "search", "query", "info", 
    "information", "details", "rules", "policy", "policies"
}

def classify_retrieval_intent(query: str) -> str:
    """
    Classifies queries into one of the designated production intents:
    Academic Calendar, Notice, Department, Hostel, Facility, Building, FAQ, Placement, Club, Navigation, General.
    """
    query_lower = query.lower().strip()
    
    # Helper to check if any term is present as a full word
    def has_word(term: str) -> bool:
        if " " in term:
            return term in query_lower
        return bool(re.search(r"\b" + re.escape(term) + r"\b", query_lower))

    def has_any_words(terms: List[str]) -> bool:
        return any(has_word(t) for t in terms)
        
    # 1. Navigation
    if has_any_words(["route", "where is", "how to get", "walking", "distance", "location", "landmark", "directions", "map"]):
        return "Navigation"
        
    # 2. FAQ (informational query starting with question words)
    if any(query_lower.startswith(w) for w in ["how", "what", "why", "who", "which"]) or has_any_words(["rule", "rules", "policy", "policies", "procedure", "eligibility"]):
        return "FAQ"
        
    # 3. Academic Calendar
    if has_any_words(["calendar", "holiday", "when is end sem", "end sem", "start semester", "mid sem", "session start", "exam dates", "vacation"]):
        return "Academic Calendar"
        
    # 4. Notice
    if has_any_words(["notice", "circular", "announcement", "latest notice", "examination notice"]):
        return "Notice"
        
    # 5. Department
    if has_any_words(["department", "cse", "ece", "aiml", "mechanical", "civil", "biotechnology"]):
        return "Department"
        
    # 6. Placement
    if has_any_words(["placement", "recruitment", "hiring", "ppo", "job", "career", "salary", "package", "companies"]):
        return "Placement"
        
    # 7. Hostel
    if has_any_words(["hostel", "mess", "dorm", "room", "accommodation"]):
        return "Hostel"
        
    # 8. Club
    if has_any_words(["club", "coding club", "robotics club", "society", "societies", "sports club", "dance club"]):
        return "Club"
        
    # 9. Facility
    if has_any_words(["medical", "doctor", "dispensary", "bank", "atm", "gym", "canteen", "cafeteria", "store"]):
        return "Facility"
        
    # 10. Building
    if has_any_words(["building", "library", "auditorium", "lecture hall", "complex", "gate"]):
        return "Building"
        
    return "General"

class QueryNormalizer:
    @staticmethod
    def normalize(query: str) -> Dict[str, Any]:
        """
        Normalizes a natural language query:
        1. Strips punctuation and lowercases.
        2. Replaces configured synonyms/abbreviations.
        3. Extracts core keywords.
        4. Removes stop words and filler words.
        5. Detects the intent.
        """
        original = query
        
        # 1. Clean and lowercase
        clean_text = query.lower().strip()
        clean_text = re.sub(r"[^\w\s]", " ", clean_text)
        
        # 2. Normalize abbreviations and synonyms (match whole phrases/words)
        for abbr, full in SYNONYMS.items():
            pattern = r"\b" + re.escape(abbr) + r"\b"
            clean_text = re.sub(pattern, full, clean_text)
            
        words = clean_text.split()
        
        # 3. Filter stop words
        meaningful_words = [w for w in words if w not in STOP_WORDS]
        if not meaningful_words:
            # Fallback to avoid empty normalized query
            meaningful_words = words
            
        normalized = " ".join(meaningful_words)
        
        # 4. Extract unique keywords (retaining ordering)
        keywords = []
        for w in meaningful_words:
            if w not in keywords:
                keywords.append(w)
                
        # 5. Detect Intent
        intent = classify_retrieval_intent(original)
        
        return {
            "original_query": original,
            "normalized_query": normalized,
            "extracted_keywords": keywords,
            "detected_intent": intent
        }
