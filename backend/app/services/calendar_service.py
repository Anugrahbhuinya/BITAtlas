from rapidfuzz import process, fuzz
from datetime import datetime
from app.utils.loader import load_json

# Load calendar data once at startup
calendar_data = load_json(
    "academics/academic_calendar/calendar.json"
)


def format_date(date_str):
    """
    Convert:
    2026-11-17
    to
    17 Nov 2026
    """
    return datetime.strptime(
        date_str,
        "%Y-%m-%d"
    ).strftime("%d %b %Y")


def search_calendar(query: str):

    event_names = [
        item["event"]
        for item in calendar_data
    ]

    result = process.extractOne(
        query,
        event_names,
        scorer=fuzz.token_set_ratio
    )

    if not result:
        return None

    event_name = result[0]
    score = result[1]

    # Confidence threshold
    if score < 40:
        return None

    for item in calendar_data:

        if item["event"] == event_name:

            start_date = format_date(
                item["start_date"]
            )

            end_date = format_date(
                item["end_date"]
            )

            # Single-day event
            if start_date == end_date:

                answer = (
                    f"📅 {item['event']} is scheduled on "
                    f"{start_date}."
                )

            # Multi-day event
            else:

                answer = (
                    f"📅 {item['event']} is scheduled from "
                    f"{start_date} to {end_date}."
                )

            return {
                "type": "calendar",
                "score": round(score, 2),
                "event": item["event"],
                "start_date": item["start_date"],
                "end_date": item["end_date"],
                "answer": answer
            }

    return None