def format_response(
    response: str,
    source: str
):

    icons = {
        "building": "📍",
        "hostel": "🏠",
        "facility": "🏥",
        "calendar": "📅",
        "notice": "📢",
        "department": "🎓",
        "club": "🎭",
        "faq": "❓"
    }

    icon = icons.get(source, "ℹ️")

    return f"{icon} {response}"

import re

def clean_gemini_response(text: str) -> str:
    """
    Cleans the Gemini response output by removing extra whitespace,
    standardizing newlines, and making sure the response is user-friendly.
    """
    if not text:
        return ""
    
    # Trim leading and trailing whitespace
    text = text.strip()
    
    # Normalize multiple newlines (max 2 consecutive newlines)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text

def append_citations_to_response(answer: str, documents: list) -> str:
    """
    Appends a structured Sources section to the response based on retrieved document metadata.
    If the response already states that the answer was not found, no citations are appended.
    """
    if not answer or not documents:
        return answer
        
    answer_lower = answer.lower()
    not_found_phrases = [
        "could not find that information",
        "having trouble reaching the ai service",
        "please try again in a few moments",
        "not found in the bit mesra knowledge base",
        "unsupported",
        "technical difficulties"
    ]
    if any(phrase in answer_lower for phrase in not_found_phrases):
        return answer
        
    unique_sources = []
    seen_sources = set()
    
    for doc in documents:
        meta = doc.metadata
        source_name = (
            meta.get("filename") or
            meta.get("name") or
            meta.get("title") or
            meta.get("event") or
            meta.get("question") or
            meta.get("source", "unknown")
        )
        
        # Avoid duplicate citations
        source_key = f"{source_name}_{meta.get('version', '')}"
        if source_key in seen_sources:
            continue
        seen_sources.add(source_key)
        
        category = meta.get("category") or meta.get("type") or "General"
        version = meta.get("version", 1)
        last_updated = meta.get("indexed_at") or meta.get("updated_at")
        if last_updated and isinstance(last_updated, str) and "t" in last_updated.lower():
            last_updated = last_updated.split("T")[0]
            
        source_type = meta.get("source_type") or meta.get("source", "manual")
        
        source_desc = f"• {source_name} ({source_type.title()} Knowledge)"
        details = []
        if version:
            details.append(f"Version V{version}")
        if category:
            details.append(f"Category: {category.title()}")
        if last_updated:
            details.append(f"Last Updated: {last_updated}")
            
        if details:
            source_desc += "\n  - " + " • ".join(details)
            
        unique_sources.append(source_desc)
        
    if not unique_sources:
        return answer
        
    # Split on ### Sources and keep only the part before it to avoid duplicated source blocks
    if "### Sources" in answer:
        answer = answer.split("### Sources")[0].strip()
        
    sources_block = "\n\n### Sources\n" + "\n".join(unique_sources)
    return answer + sources_block