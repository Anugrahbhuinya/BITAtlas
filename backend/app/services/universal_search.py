from rapidfuzz import fuzz, utils
from app.utils.loader import load_json

# Load all datasets
faqs = load_json("faqs/student_faqs.json")
calendar = load_json("academics/academic_calendar/calendar.json")
buildings = load_json("maps/buildings.json")
facilities = load_json("maps/facilities.json")
hostels = load_json("maps/hostels.json")
departments = load_json("academics/departments.json")
clubs = load_json("clubs/clubs.json")


def universal_search(query: str):

    query = query.lower()

    candidates = []

    # FAQs
    for faq in faqs:
        score = fuzz.token_set_ratio(
            query, faq["question"].lower(), processor=utils.default_process
        )

        candidates.append({
            "type": "faq",
            "score": score,
            "answer": faq["answer"]
        })

    # Buildings
    for name, info in buildings.items():
        score = fuzz.token_set_ratio(
            query, name.lower(), processor=utils.default_process
        )

        candidates.append({
            "type": "location",
            "score": score,
            "answer": info.get("description") or f"{name} ({info.get('type', 'building')})"
        })

    # Facilities
    for name, info in facilities.items():
        score = fuzz.token_set_ratio(
            query, name.lower(), processor=utils.default_process
        )

        desc = f"{name}"
        category = info.get("category")
        if category:
            desc += f" ({category})"
        if "opening_time" in info and "closing_time" in info:
            desc += f" [Open: {info['opening_time']} - {info['closing_time']}]"

        candidates.append({
            "type": "facility",
            "score": score,
            "answer": desc
        })

    # Hostels
    for name, info in hostels.items():
        score = fuzz.token_set_ratio(
            query, name.lower(), processor=utils.default_process
        )

        candidates.append({
            "type": "hostel",
            "score": score,
            "answer": info.get("description") or f"{name} ({info.get('type', 'hostel').replace('_', ' ')})"
        })

    # Departments
    for code, info in departments.items():
        name = info.get("name", code)
        score = max(
            fuzz.token_set_ratio(
                query, name.lower(), processor=utils.default_process
            ),
            fuzz.token_set_ratio(
                query, code.lower(), processor=utils.default_process
            ),
        )

        desc = f"Department of {name}"
        head = info.get("head")
        office = info.get("office")
        extra = []
        if head:
            extra.append(f"Head: {head}")
        if office:
            extra.append(f"Office: {office}")
        if extra:
            desc += f" ({', '.join(extra)})"

        candidates.append({
            "type": "department",
            "score": score,
            "answer": desc
        })

    # Clubs
    for name, info in clubs.items():
        score = fuzz.token_set_ratio(
            query, name.lower(), processor=utils.default_process
        )

        desc = info.get("description") or name
        contact = info.get("contact")
        place = info.get("meeting_place")
        extra = []
        if contact:
            extra.append(f"Contact: {contact}")
        if place:
            extra.append(f"Meeting Place: {place}")
        if extra:
            desc += f" ({', '.join(extra)})"

        candidates.append({
            "type": "club",
            "score": score,
            "answer": desc
        })

    # Calendar
    for event in calendar:
        score = fuzz.token_set_ratio(
            query, event["event"].lower(), processor=utils.default_process
        )

        start = event.get("start_date")
        end = event.get("end_date")
        if start and end:
            date_info = f"{start} to {end}" if start != end else start
        else:
            date_info = event.get("date", "N/A")

        candidates.append({
            "type": "calendar",
            "score": score,
            "answer": (
                f"{event['event']} ({date_info})"
            )
        })

    best_match = max(
        candidates,
        key=lambda x: x["score"]
    )

    if best_match["score"] < 40:
        return None

    return best_match