from app.services.rag.retriever import retrieve_with_scores
from app.utils.loader import load_json

SIMILARITY_THRESHOLD = 0.70

# Load FAQs data for answer lookups
faqs_data = load_json("faqs/student_faqs.json")


def query_rag(question: str):

    results = retrieve_with_scores(
        question,
        k=5
    )

    if not results:
        return None

    best_doc, best_score = results[0]

    # Lower score = better match
    if best_score > SIMILARITY_THRESHOLD:
        return None

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
                "source": source
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
                "source": source
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
            "source": source
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
            "source": source
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
            "source": source
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
            "source": source
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
            "source": source
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
            "source": source
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
            "source": source
        }

    # ==================================================
    # DEFAULT RESPONSE
    # ==================================================

    return {
        "answer": best_doc.page_content,
        "confidence": float(best_score),
        "source": source
    }