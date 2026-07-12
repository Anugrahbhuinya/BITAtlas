from rapidfuzz import fuzz
from app.utils.loader import load_json

faqs = load_json("faqs/student_faqs.json")


def search_faq(query: str):

    best_match = None
    best_score: float = 0.0

    for faq in faqs:

        score = fuzz.token_set_ratio(
            query.lower(),
            faq["question"].lower()
        )

        if score > best_score:
            best_score = score
            best_match = faq

    if best_score > 60 and best_match is not None:
        return {
            "type": "faq",
            "score": best_score,
            "answer": best_match["answer"]
        }

    return None