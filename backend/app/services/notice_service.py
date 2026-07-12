from rapidfuzz import process, fuzz
from app.utils.loader import load_json

notices = load_json(
    "notices/notices.json"
)


def search_notice(query: str):

    notice_titles = [
        notice["title"]
        for notice in notices
    ]

    result = process.extractOne(
        query,
        notice_titles,
        scorer=fuzz.token_set_ratio
    )

    if not result:
        return None

    title = result[0]
    score = result[1]

    if score < 40:
        return None

    for notice in notices:

        if notice["title"] == title:

            return {
                "type": "notice",
                "score": round(score, 2),
                "title": notice["title"],
                "category": notice["category"],
                "date": notice["date"],
                "description": notice["content"],
                "answer": (
                    f"📢 {notice['title']}\n\n"
                    f"{notice['content']}\n\n"
                    f"Category: {notice['category']}\n"
                    f"Date: {notice['date']}"
                )
            }

    return None


def get_all_notices() -> list:
    """Returns all loaded notices."""
    return notices


def get_latest_notices(limit: int = 5) -> list:
    """Returns the latest notices (sorted by date if possible)."""
    try:
        # Sort by date descending if in YYYY-MM-DD or similar sortable format
        sorted_notices = sorted(notices, key=lambda x: x.get("date", ""), reverse=True)
        return sorted_notices[:limit]
    except Exception:
        return notices[:limit]


def get_notices_by_category(category: str) -> list:
    """Filters notices by category name (case-insensitive)."""
    return [
        n for n in notices
        if n.get("category", "").lower() == category.lower()
    ]