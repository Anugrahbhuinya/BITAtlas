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