import os
import sys

SCRIPT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

BACKEND_DIR = os.path.dirname(
    SCRIPT_DIR
)

PROJECT_ROOT = os.path.dirname(
    BACKEND_DIR
)

if BACKEND_DIR not in sys.path:
    sys.path.insert(
        0,
        BACKEND_DIR
    )

from app.services.rag.ingestion_service import (
    load_faqs,
    load_calendar,
    load_notices,
    load_buildings,
    load_facilities,
    load_hostels,
    load_departments,
    load_clubs
)

from app.services.rag.embeddings import (
    save_documents
)

all_docs = []

# ==================================================
# FAQS
# ==================================================

faq_path = os.path.join(
    PROJECT_ROOT,
    "data",
    "faqs",
    "student_faqs.json"
)

faq_docs = load_faqs(
    faq_path
)

print(
    f"Loaded FAQs: {len(faq_docs)}"
)

all_docs.extend(
    faq_docs
)

# ==================================================
# CALENDAR
# ==================================================

calendar_path = os.path.join(
    PROJECT_ROOT,
    "data",
    "academics",
    "academic_calendar",
    "calendar.json"
)
print(calendar_path)
print(os.path.exists(calendar_path))

calendar_docs = load_calendar(
    calendar_path
)

print(
    f"Loaded Calendar Events: {len(calendar_docs)}"
)

all_docs.extend(
    calendar_docs
)

# ==================================================
# NOTICES
# ==================================================

notices_path = os.path.join(
    PROJECT_ROOT,
    "data",
    "notices",
    "notices.json"
)

notice_docs = load_notices(
    notices_path
)

print(
    f"Loaded Notices: {len(notice_docs)}"
)

all_docs.extend(
    notice_docs
)

#facilities
facilities_path = os.path.join(
    PROJECT_ROOT,
    "data",
    "maps",
    "facilities.json"
)

facility_docs = load_facilities(
    facilities_path
)

print(
    f"Loaded Facilities: {len(facility_docs)}"
)

all_docs.extend(
    facility_docs
)

#hostels
hostels_path = os.path.join(
    PROJECT_ROOT,
    "data",
    "maps",
    "hostels.json"
)

hostel_docs = load_hostels(
    hostels_path
)

print(
    f"Loaded Hostels: {len(hostel_docs)}"
)

all_docs.extend(
    hostel_docs
)

#buildings
buildings_path = os.path.join(
    PROJECT_ROOT,
    "data",
    "maps",
    "buildings.json"
)

building_docs = load_buildings(
    buildings_path
)

print(
    f"Loaded Buildings: {len(building_docs)}"
)

all_docs.extend(
    building_docs
)

#departments
departments_path = os.path.join(
    PROJECT_ROOT,
    "data",
    "academics",
    "departments.json"
)

department_docs = load_departments(
    departments_path
)

print(
    f"Loaded Departments: {len(department_docs)}"
)

all_docs.extend(
    department_docs
)

#clubs
clubs_path = os.path.join(
    PROJECT_ROOT,
    "data",
    "clubs",
    "clubs.json"
)

club_docs = load_clubs(
    clubs_path
)

print(
    f"Loaded Clubs: {len(club_docs)}"
)

all_docs.extend(
    club_docs
)

# ==================================================
# SAVE TO CHROMA
# ==================================================

save_documents(
    all_docs,
    source_types=["faq", "calendar", "notice", "building", "facility", "hostel", "department", "club"]
)

print(
    f"\nIndexed Total Documents: {len(all_docs)}"
)

print(
    "RAG Knowledge Base Created Successfully"
)