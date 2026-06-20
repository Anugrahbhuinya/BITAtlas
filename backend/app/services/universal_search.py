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
    for b in buildings:
        name = b.get("name", "")
        score = fuzz.token_set_ratio(
            query, name.lower(), processor=utils.default_process
        )

        candidates.append({
            "type": "location",
            "score": score,
            "answer": b.get("description") or f"{name} ({b.get('category', 'building')})"
        })

    # Facilities
    for f in facilities:
        name = f.get("name", "")
        score = fuzz.token_set_ratio(
            query, name.lower(), processor=utils.default_process
        )

        desc = f.get("description") or name
        timings = f.get("timings")
        if timings:
            desc += f" [Timings: {timings}]"

        candidates.append({
            "type": "facility",
            "score": score,
            "answer": desc
        })

    # Hostels
    for h in hostels:
        name = h.get("name", "")
        score = fuzz.token_set_ratio(
            query, name.lower(), processor=utils.default_process
        )

        candidates.append({
            "type": "hostel",
            "score": score,
            "answer": h.get("description") or f"{name} ({h.get('gender', 'hostel')})"
        })

    # Departments
    for d in departments:
        name = d.get("name", "")
        desc = d.get("description", "")
        building = d.get("building", "")
        programs = d.get("programs", [])
        
        # We also extract acronym (e.g. CSE) to match acronym searches
        words = name.split()
        acronym = "".join(w[0] for w in words if w[0].isupper())

        score = max(
            fuzz.token_set_ratio(
                query, name.lower(), processor=utils.default_process
            ),
            fuzz.token_set_ratio(
                query, acronym.lower(), processor=utils.default_process
            ),
        )

        full_desc = f"Department of {name}: {desc} (Located in {building}). Programs: {', '.join(programs)}"

        candidates.append({
            "type": "department",
            "score": score,
            "answer": full_desc
        })

    # Clubs
    for c in clubs:
        name = c.get("name", "")
        category = c.get("category", "")
        desc = c.get("description", "")
        activities = c.get("activities", [])
        
        score = fuzz.token_set_ratio(
            query, name.lower(), processor=utils.default_process
        )

        full_desc = f"{name} ({category}): {desc} Activities: {', '.join(activities)}"

        candidates.append({
            "type": "club",
            "score": score,
            "answer": full_desc
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