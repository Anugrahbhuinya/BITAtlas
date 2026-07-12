import re
import logging
from typing import List
from app.services.rag.retriever import retrieve_with_scores
from app.utils.loader import load_json

logger = logging.getLogger("rag_service")

SIMILARITY_THRESHOLD = 0.70

# Load FAQs data for answer lookups
faqs_data = load_json("faqs/student_faqs.json")

def validate_rag_relevance(query: str, doc_content: str, doc_metadata: dict, intent: str | None) -> bool:
    """
    Validates if the retrieved RAG document content matches the user's intent.
    Returns True if relevant, False if it should be rejected.
    """
    if not intent:
        return True
        
    query_lower = query.lower()
    doc_content_lower = doc_content.lower()
    filename = doc_metadata.get("filename", "").lower()
    source = doc_metadata.get("source", "").lower()
    
    # Rule 1: Reject resume/CV documents if the query is not asking about professional details or student profiles
    if "resume" in filename or "cv" in filename or source == "resume":
        profile_keywords = ["resume", "cv", "experience", "education", "project", "work", "job", "career", "skills", "profile", "gpa", "internship"]
        if not any(k in query_lower for k in profile_keywords):
            logger.info(f"Rejecting document {filename} because it is a resume and query is not profile-related.")
            return False
            
    # Rule 2: If the query is a comparison or concept question, verify that the document is relevant to the comparison terms
    if intent in ["Comparison", "AI / ML Concept", "Programming Help", "Engineering Concept"]:
        if "cnn" in query_lower and "resnet" in query_lower:
            if "resnet" not in doc_content_lower:
                logger.info(f"Rejecting document {filename} because it does not contain 'resnet' for CNN vs ResNet comparison.")
                return False
        if "list" in query_lower and "tuple" in query_lower:
            if "tuple" not in doc_content_lower:
                logger.info(f"Rejecting document {filename} because it does not contain 'tuple' for List vs Tuple comparison.")
                return False
        if "tcp" in query_lower and "udp" in query_lower:
            if "udp" not in doc_content_lower:
                logger.info(f"Rejecting document {filename} because it does not contain 'udp' for TCP vs UDP comparison.")
                return False
                
    return True

def query_rag(question: str, intent: str | None = None, metadata_filters: dict | None = None):

    results = retrieve_with_scores(
        question,
        k=5,
        metadata_filters=metadata_filters
    )

    valid_results = []
    rejected_docs = []
    if results:
        for doc, score in results:
            if validate_rag_relevance(question, doc.page_content, doc.metadata, intent):
                # Ignore expired knowledge items
                if doc.metadata.get("status") == "expired":
                    continue
                valid_results.append((doc, score))
            else:
                rejected_docs.append(doc.metadata.get("filename", "unknown"))
                
    results = valid_results

    retrieved_docs = []
    if results:
        for doc, score in results:
            source_name = (
                doc.metadata.get("filename") or
                doc.metadata.get("name") or
                doc.metadata.get("title") or
                doc.metadata.get("event") or
                doc.metadata.get("question") or
                doc.metadata.get("source", "unknown")
            )
            page_num = doc.metadata.get("page")
            citation = f"[Source: {source_name}"
            if page_num:
                citation += f", Page: {page_num}"
            citation += "]"
            retrieved_docs.append(f"{citation}\n{doc.page_content}")

    print("\n========== RAG SERVICE ==========")
    print(f"Retrieved Documents:\n{len(results)}")
    if results:
        best_doc, best_score = results[0]
        print(f"Best Score:\n{best_score}")
        print(f"Best Source:\n{best_doc.metadata.get('source', 'unknown')}")
    else:
        print("Best Score:\nNone")
        print("Best Source:\nNone")
    print("=================================\n")

    if not results:
        return {
            "answer": "I could not find that information in the BIT Mesra knowledge base.",
            "confidence": 1.0,
            "source": "rag",
            "documents": [],
            "rejected_documents": rejected_docs
        }

    best_doc, best_score = results[0]

    source = best_doc.metadata.get(
        "source",
        "rag"
    )

    # ==================================================
    # CALENDAR RESPONSE
    # ==================================================

    if source == "calendar":
        query_lower = question.lower()
        is_specific = False
        event_name = best_doc.metadata.get("event", "").lower()

        # Check if the query specifically references a calendar event name
        event_words = {
            w for w in event_name.replace("?", "").replace(",", "").split()
            if w not in ["academic", "date", "event", "calendar"]
        }
        if event_words and any(w in query_lower for w in event_words):
            is_specific = True

        # Check if the query contains specific temporal queries
        if any(kw in query_lower for kw in ["when is", "date of", "date for", "exact date"]):
            is_specific = True

        if is_specific:
            event = best_doc.metadata.get("event", "Academic Event")
            start_date = best_doc.metadata.get("start_date", "Not Available")
            end_date = best_doc.metadata.get("end_date", "Not Available")
            return {
                "answer": (
                    f"📅 {event}\n\n"
                    f"Start Date: {start_date}\n"
                    f"End Date: {end_date}"
                ),
                "confidence": float(best_score),
                "source": source,
                "documents": retrieved_docs
            }
        else:
            calendar_answers = []
            for doc, score in results[:5]:
                if doc.metadata.get("source") == "calendar" and score <= SIMILARITY_THRESHOLD:
                    event = doc.metadata.get("event", "Academic Event")
                    start_date = doc.metadata.get("start_date", "Not Available")
                    end_date = doc.metadata.get("end_date", "Not Available")
                    calendar_answers.append(
                        f"📅 {event}\nStart Date: {start_date}\nEnd Date: {end_date}"
                    )

            combined_answer = "\n\n---\n\n".join(calendar_answers) if calendar_answers else (
                f"📅 {best_doc.metadata.get('event', 'Academic Event')}\n"
                f"Start Date: {best_doc.metadata.get('start_date', 'Not Available')}\n"
                f"End Date: {best_doc.metadata.get('end_date', 'Not Available')}"
            )

            return {
                "answer": combined_answer,
                "confidence": float(best_score),
                "source": source,
                "documents": retrieved_docs
            }

    # ==================================================
    # NOTICE RESPONSE
    # ==================================================

    if source == "notice":
        notice_answers = []
        for doc, score in results[:5]:
            if doc.metadata.get("source") == "notice" and score <= SIMILARITY_THRESHOLD:
                title = doc.metadata.get("title", "Campus Notice")
                category = doc.metadata.get("category", "General")
                date = doc.metadata.get("date", "N/A")
                notice_answers.append(
                    f"📢 {title}\nCategory: {category}\nDate: {date}\n\n{doc.page_content}"
                )

        combined_answer = "\n\n---\n\n".join(notice_answers) if notice_answers else (
            f"📢 {best_doc.metadata.get('title', 'Campus Notice')}\n"
            f"Category: {best_doc.metadata.get('category', 'General')}\n"
            f"Date: {best_doc.metadata.get('date', 'N/A')}\n\n"
            f"{best_doc.page_content}"
        )

        return {
            "answer": combined_answer,
            "confidence": float(best_score),
            "source": source,
            "documents": retrieved_docs
        }

    # ==================================================
    # BUILDING RESPONSE
    # ==================================================

    if source == "building":
        return {
            "answer": (
                f"🏢 Building Information\n\n"
                f"{best_doc.page_content}"
            ),
            "confidence": float(best_score),
            "source": source,
            "documents": retrieved_docs
        }

    # ==================================================
    # FACILITY RESPONSE
    # ==================================================

    if source == "facility":
        return {
            "answer": (
                f"🏥 Facility Information\n\n"
                f"{best_doc.page_content}"
            ),
            "confidence": float(best_score),
            "source": source,
            "documents": retrieved_docs
        }

    # ==================================================
    # HOSTEL RESPONSE
    # ==================================================

    if source == "hostel":
        return {
            "answer": (
                f"🏠 Hostel Information\n\n"
                f"{best_doc.page_content}"
            ),
            "confidence": float(best_score),
            "source": source,
            "documents": retrieved_docs
        }

    # ==================================================
    # DEPARTMENT RESPONSE
    # ==================================================

    if source == "department":
        return {
            "answer": (
                f"🎓 Department Information\n\n"
                f"{best_doc.page_content}"
            ),
            "confidence": float(best_score),
            "source": source,
            "documents": retrieved_docs
        }

    # ==================================================
    # CLUB RESPONSE
    # ==================================================

    if source == "club":
        answers = []
        for doc, score in results[:5]:
            if doc.metadata.get("source") == "club" and score <= SIMILARITY_THRESHOLD:
                answers.append(doc.page_content.strip())

        combined_answer = "\n\n---\n\n".join(answers) if answers else best_doc.page_content

        return {
            "answer": (
                f"🎯 Club Information\n\n"
                f"{combined_answer}"
            ),
            "confidence": float(best_score),
            "source": source,
            "documents": retrieved_docs
        }

    # ==================================================
    # FAQ RESPONSE
    # ==================================================

    if source == "faq":
        faq_id = best_doc.metadata.get("id")
        answer = None

        if faq_id is not None:
            # Look up the actual answer by FAQ ID
            for faq in faqs_data:
                if faq.get("id") == faq_id:
                    answer = faq.get("answer")
                    break

        if not answer:
            # Fallback to looking up by question text match
            question_text = best_doc.metadata.get("question")
            for faq in faqs_data:
                if faq.get("question") == question_text:
                    answer = faq.get("answer")
                    break

        if not answer:
            # Ultimate fallback to page content
            answer = best_doc.page_content

        return {
            "answer": answer,
            "confidence": float(best_score),
            "source": source,
            "documents": retrieved_docs
        }

    # ==================================================
    # DEFAULT RESPONSE
    # ==================================================

    return {
        "answer": best_doc.page_content,
        "confidence": float(best_score),
        "source": source,
        "documents": retrieved_docs
    }


def extract_fallback_answer(query: str, retrieved_docs: List[str]) -> str:
    """
    Parses and extracts a clean direct answer from retrieved document chunks.
    Used as a high-quality fallback when the Gemini API is rate-limited or down.
    """
    if not retrieved_docs:
        return "I could not find that information in the BIT Mesra knowledge base."
        
    query_lower = query.lower()
    query_clean = re.sub(r'[^\w\s]', ' ', query_lower)
    query_words = set(query_clean.split())
    stop_words = {
        "what", "is", "the", "are", "of", "in", "to", "for", "a", "an", "this", 
        "that", "it", "they", "them", "where", "how", "who", "when", "which", 
        "on", "at", "by", "from", "with", "listed", "listed in", "on campus", "resume"
    }
    meaningful_words = query_words - stop_words
    if not meaningful_words:
        meaningful_words = query_words
        
    best_sentences = []
    best_source_header = ""
    max_overlap = -1
    
    # Parse retrieved docs (formatted as "[Source: filename, Page: page]\ncontent")
    for doc_text in retrieved_docs:
        header = ""
        content = doc_text
        if doc_text.startswith("[Source:"):
            end_idx = doc_text.find("]")
            if end_idx != -1:
                header = doc_text[:end_idx + 1]
                content = doc_text[end_idx + 1:].strip()
                
        # Split content into sentences or lines
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n', content) if s.strip()]
        
        for sent in sentences:
            sent_lower = sent.lower()
            sent_clean = re.sub(r'[^\w\s]', ' ', sent_lower)
            sent_words = set(sent_clean.split())
            overlap = len(meaningful_words.intersection(sent_words))
            
            # Additional score weight if sentence contains decimals/numbers when querying stats
            if overlap > 0:
                if any(term in query_lower for term in ["cgpa", "gpa", "score", "percentage", "marks", "grade"]):
                    if re.search(r'\b\d\.\d+\b|\b\d/\d\b|\b\d{2,3}\b', sent):
                        overlap += 1
                
                if overlap > max_overlap:
                    max_overlap = overlap
                    best_sentences = [sent]
                    best_source_header = header
                elif overlap == max_overlap:
                    best_sentences.append(sent)
                    
    if max_overlap > 0 and best_sentences:
        unique_sentences = []
        for s in best_sentences:
            if s not in unique_sentences:
                unique_sentences.append(s)
        joined_sentences = " ".join(unique_sentences[:2])
        
        source_citation = ""
        if best_source_header:
            source_citation = f"According to {best_source_header.replace('[Source: ', '').replace(']', '')}:\n"
            
        return f"{source_citation}{joined_sentences}"
        
    # If no specific sentence has overlap, return a clean snippet of the top document
    first_doc = retrieved_docs[0]
    header = ""
    content = first_doc
    if first_doc.startswith("[Source:"):
        end_idx = first_doc.find("]")
        if end_idx != -1:
            header = first_doc[:end_idx + 1]
            content = first_doc[end_idx + 1:].strip()
            
    source_citation = ""
    if header:
        source_citation = f"According to {header.replace('[Source: ', '').replace(']', '')}:\n"
        
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    snippet = " ".join(lines[:3])
    return f"{source_citation}{snippet}"