import json

from langchain_core.documents import Document

from app.services.rag.chunking_service import create_chunks


# ==================================================
# FAQ INGESTION
# ==================================================

def load_faqs(path: str):

    documents = []

    with open(path, "r", encoding="utf-8") as file:
        faqs = json.load(file)

    for faq in faqs:

        content = f"""
Question: {faq['question']}
"""

        chunks = create_chunks(content)

        for chunk in chunks:

            documents.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "source": "faq",
                        "id": faq["id"],
                        "question": faq["question"]
                    }
                )
            )

    return documents


# ==================================================
# CALENDAR INGESTION
# ==================================================

def load_calendar(path: str):

    documents = []

    with open(path, "r", encoding="utf-8") as file:
        calendar = json.load(file)

    for entry in calendar:

        content = f"""
Event: {entry['event']}
Start Date: {entry['start_date']}
End Date: {entry['end_date']}
"""

        chunks = create_chunks(content)

        for chunk in chunks:

            documents.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "source": "calendar",
                        "event": entry["event"],
                        "start_date": entry["start_date"],
                        "end_date": entry["end_date"]
                    }
                )
            )

    return documents


# ==================================================
# NOTICE INGESTION
# ==================================================

def load_notices(path: str):

    documents = []

    with open(path, "r", encoding="utf-8") as file:
        notices = json.load(file)

    for notice in notices:

        content = f"""
Title: {notice['title']}

Category: {notice['category']}

Date: {notice['date']}

Content:
{notice['content']}
"""

        chunks = create_chunks(content)

        for chunk in chunks:

            documents.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "source": "notice",
                        "id": notice["id"],
                        "title": notice["title"],
                        "category": notice["category"],
                        "date": notice["date"]
                    }
                )
            )

    return documents


# ==================================================
# BUILDINGS INGESTION
# ==================================================

def load_buildings(path: str):

    documents = []

    with open(path, "r", encoding="utf-8") as file:
        buildings = json.load(file)

    for b in buildings:
        name = b.get("name", "")
        content = f"""
Building Name: {name}
Category: {b.get('category', '')}
Location: {b.get('location', '')}
Description: {b.get('description', '')}
"""

        chunks = create_chunks(content)

        for chunk in chunks:

            documents.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "source": "building",
                        "name": name
                    }
                )
            )

    return documents


# ==================================================
# FACILITIES INGESTION
# ==================================================

def load_facilities(path: str):

    documents = []

    with open(path, "r", encoding="utf-8") as file:
        facilities = json.load(file)

    for f in facilities:
        name = f.get("name", "")
        content = f"""
Facility Name: {name}
Location: {f.get('location', '')}
Timings: {f.get('timings', '')}
Description: {f.get('description', '')}
"""

        chunks = create_chunks(content)

        for chunk in chunks:

            documents.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "source": "facility",
                        "name": name
                    }
                )
            )

    return documents


# ==================================================
# HOSTELS INGESTION
# ==================================================

def load_hostels(path: str):

    documents = []

    with open(path, "r", encoding="utf-8") as file:
        hostels = json.load(file)

    for h in hostels:
        name = h.get("name", "")
        content = f"""
Hostel Name: {name}
Gender: {h.get('gender', '')}
Capacity: {h.get('capacity', 0)}
Description: {h.get('description', '')}
"""

        chunks = create_chunks(content)

        for chunk in chunks:

            documents.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "source": "hostel",
                        "name": name
                    }
                )
            )

    return documents


# ==================================================
# DEPARTMENTS INGESTION
# ==================================================

def load_departments(path: str):

    documents = []

    with open(path, "r", encoding="utf-8") as file:
        departments = json.load(file)

    for d in departments:
        name = d.get("name", "")
        programs_str = ", ".join(d.get("programs", []))
        content = f"""
Department Name: {name}
Building Location: {d.get('building', '')}
Programs Offered: {programs_str}
Description: {d.get('description', '')}
"""

        chunks = create_chunks(content)

        for chunk in chunks:

            documents.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "source": "department",
                        "name": name
                    }
                )
            )

    return documents


# ==================================================
# CLUBS INGESTION
# ==================================================

def load_clubs(path: str):

    documents = []

    with open(path, "r", encoding="utf-8") as file:
        clubs = json.load(file)

    for c in clubs:
        name = c.get("name", "")
        activities_str = ", ".join(c.get("activities", []))
        content = f"""
Club Name: {name}
Category: {c.get('category', '')}
Activities: {activities_str}
Description: {c.get('description', '')}
"""

        chunks = create_chunks(content)

        for chunk in chunks:

            documents.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "source": "club",
                        "name": name
                    }
                )
            )

    return documents