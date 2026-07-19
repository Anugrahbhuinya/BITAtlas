# backend/scripts/seed_navigation.py

import os
import sys
import json
import asyncio
from datetime import datetime, timezone
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# Setup path so it can import app.core
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.core import config

# OSM IDs mapping for realistic BIT Mesra layout
OSM_MAP = {
    # Buildings: name -> (osm_type, osm_id, code)
    "Central Library": ("node", 100002, "LIB"),
    "Main Administrative Building": ("node", 100001, "MAIN"),
    "University Auditorium": ("node", 100003, "AUDI"),
    "Lecture Hall Complex": ("node", 100004, "LHC"),
    "Department of Computer Science and Engineering": ("node", 100005, "CSE"),
    "Department of Artificial Intelligence and Machine Learning": ("node", 100006, "AIML"),
    "Department of Electronics and Communication Engineering": ("node", 100007, "ECE"),
    "Department of Mechanical Engineering": ("node", 100008, "MECH"),
    "Department of Electrical Engineering": ("node", 100009, "EE"),
    "Department of Civil Engineering": ("node", 100046, "CIVIL"),
    "Department of Biotechnology": ("node", 100010, "BIOTECH"),
    "Research and Innovation Center": ("node", 100011, "RIC"),
    "Student Activity Center": ("node", 100012, "SAC"),
    "Sports Complex": ("node", 100013, "SPORTS"),
    "Guest House": ("node", 100014, "GUEST"),
    
    # Hostels
    "Aryabhatta Hostel": ("node", 100015, "H1"),
    "Raman Hostel": ("node", 100016, "H2"),
    "CV Raman Hostel": ("node", 100017, "H3"),
    "Vivekananda Hostel": ("node", 100018, "H4"),
    "Gargi Hostel": ("node", 100019, "H5"),
    "Sarojini Hostel": ("node", 100020, "H6"),
    "New Girls Hostel": ("node", 100021, "H7"),
    "International Students Hostel": ("node", 100022, "H8"),
}

FACILITY_MAP = {
    # Facility -> (osm_type, osm_id, category)
    "Medical Unit": ("node", 100031, "Medical Centre"),
    "Central Cafeteria": ("node", 100032, "Cafeteria"),
    "Nescafe Outlet": ("node", 100033, "Cafeteria"),
    "SBI Bank Branch": ("node", 100034, "Bank"),
    "SBI ATM": ("node", 100035, "ATM"),
    "Placement and Training Cell": ("node", 100036, "Administrative"),
    "Campus Gymnasium": ("node", 100037, "Sports Complex"),
    "Indoor Sports Hall": ("node", 100038, "Sports Complex"),
    "Student Store": ("node", 100039, "Other"),
    "Stationery and Xerox Center": ("node", 100040, "Xerox"),
}

LANDMARK_OSM_MAP = {
    # Landmark -> (osm_type, osm_id)
    "Main Gate": ("node", 100041),
    "Clock Tower": ("node", 100042),
    "Central Lawn": ("node", 100043),
    "Saraswati Temple (Statue)": ("node", 100044),
    "Main Fountain": ("node", 100045),
}

def get_aliases_for_building(name: str, code: str) -> List[str]:
    aliases = [name, code]
    if "Hostel" in name:
        num = code.replace("H", "")
        aliases.extend([f"Hostel {num}", f"H{num}", name.replace(" Hostel", "")])
    if "Main Administrative Building" in name:
        aliases.extend(["Admin Building", "Administration", "Main Building"])
    if "Computer Science" in name:
        aliases.extend(["CSE Department", "CSE", "Computer Science"])
    if "Artificial Intelligence" in name:
        aliases.extend(["AI Department", "AIML Department", "AI", "AIML"])
    if "Lecture Hall Complex" in name:
        aliases.extend(["LHC", "Lecture Hall"])
    if "Library" in name:
        aliases.extend(["Library", "Central Library"])
    if "Medical" in name:
        aliases.extend(["Medical Centre", "Hospital", "Health Centre"])
    return list(set(aliases))

async def seed_data():
    client = AsyncIOMotorClient(config.MONGO_URI)
    db = client[config.MONGO_DB]
    
    print("Clearing existing navigation collections...")
    await db.buildings.delete_many({})
    await db.rooms.delete_many({})
    await db.landmarks.delete_many({})
    await db.facilities.delete_many({})
    await db.pathways.delete_many({})
    
    print("Loading data from JSON files...")
    project_root = os.path.dirname(BACKEND_DIR)
    
    # 1. Buildings
    buildings_path = os.path.join(project_root, "data", "maps", "buildings.json")
    with open(buildings_path, "r", encoding="utf-8") as f:
        buildings_json = json.load(f)
        
    building_map_id = {} # maps JSON ID to MongoDB string ID
    
    for bj in buildings_json:
        name = bj["name"]
        osm_type, osm_id, code = OSM_MAP.get(name, ("way", 0, bj.get("building_code", "BLDG")))
        
        building_doc = {
            "building_code": bj.get("building_code", code),
            "building_name": name,
            "description": bj["description"],
            "category": bj["category"] if bj["category"] != "Student Services" else "Student Services",
            "latitude": bj.get("latitude", 0.0),
            "longitude": bj.get("longitude", 0.0),
            "osm_type": osm_type,
            "osm_id": osm_id,
            "aliases": bj.get("aliases", get_aliases_for_building(name, code)),
            "address": bj.get("location") or bj.get("address") or "BIT Mesra Campus",
            "image": None,
            "opening_hours": "09:00 - 17:30" if bj["category"] != "Administrative" else "09:30 - 17:00",
            "contact": "0651-2275444",
            "departments": [name.replace("Department of ", "")] if "Department" in name else [],
            "entrances": [
                {"name": "Main Entrance", "latitude": bj.get("latitude", 0.0), "longitude": bj.get("longitude", 0.0)}
            ],
            "floors": [0, 1, 2],
            "accessibility": {
                "wheelchair_accessible": True,
                "has_elevator": True if code in ["MAIN", "LIB", "CSE", "RIC"] else False,
                "has_ramp": True
            },
            "metadata": {
                "search_keywords": bj.get("search_keywords", []),
                "associated_building": bj.get("associated_building", None)
            },
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        res = await db.buildings.insert_one(building_doc)
        building_map_id[bj["id"]] = str(res.inserted_id)
        
    print(f"Seeded {len(building_map_id)} Academic and Admin Buildings.")

    # 2. Hostels (Add as residential buildings)
    hostels_path = os.path.join(project_root, "data", "maps", "hostels.json")
    with open(hostels_path, "r", encoding="utf-8") as f:
        hostels_json = json.load(f)
        
    for hj in hostels_json:
        name = hj["name"]
        osm_type, osm_id, code = OSM_MAP.get(name, ("way", 0, hj.get("building_code", "H" + str(hj["id"]))))
        
        building_doc = {
            "building_code": hj.get("building_code", code),
            "building_name": name,
            "description": hj["description"],
            "category": "Residential",
            "latitude": hj.get("latitude", 0.0),
            "longitude": hj.get("longitude", 0.0),
            "osm_type": osm_type,
            "osm_id": osm_id,
            "aliases": hj.get("aliases", get_aliases_for_building(name, code)),
            "address": "Hostel Zone, BIT Mesra Campus",
            "image": None,
            "opening_hours": "24 Hours (Gate closes at 22:00 for students)",
            "contact": "0651-2275000",
            "departments": [],
            "entrances": [{"name": "Main Gate", "latitude": hj.get("latitude", 0.0), "longitude": hj.get("longitude", 0.0)}],
            "floors": [0, 1, 2, 3],
            "accessibility": {
                "wheelchair_accessible": True,
                "has_elevator": True if code == "H7" else False,
                "has_ramp": True
            },
            "metadata": {
                "capacity": hj["capacity"],
                "gender": hj["gender"],
                "search_keywords": hj.get("search_keywords", []),
                "associated_building": hj.get("associated_building", None)
            },
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        res = await db.buildings.insert_one(building_doc)
        building_map_id[f"hostel_{hj['id']}"] = str(res.inserted_id)
        
    print(f"Seeded {len(hostels_json)} Residential Hostels.")

    # 3. Rooms
    lhc_db_id = None
    cse_db_id = None
    lib_db_id = None
    
    async for b in db.buildings.find():
        if b["building_code"] == "LHC":
            lhc_db_id = str(b["_id"])
        elif b["building_code"] == "CSE":
            cse_db_id = str(b["_id"])
        elif b["building_code"] == "LIB":
            lib_db_id = str(b["_id"])
            
    rooms = []
    
    if lhc_db_id:
        rooms.extend([
            {"room_number": "LH-1", "room_name": "Lecture Hall 1", "building_id": lhc_db_id, "floor": 0, "room_type": "Classroom", "capacity": 150, "description": "Large smart classroom on the ground floor.", "facilities": ["AC", "Projector", "Sound System"], "department": "First Year UG"},
            {"room_number": "LH-2", "room_name": "Lecture Hall 2", "building_id": lhc_db_id, "floor": 0, "room_type": "Classroom", "capacity": 150, "description": "Large smart classroom on the ground floor.", "facilities": ["AC", "Projector", "Sound System"], "department": "First Year UG"},
            {"room_number": "LH-3", "room_name": "Lecture Hall 3", "building_id": lhc_db_id, "floor": 1, "room_type": "Classroom", "capacity": 120, "description": "Smart classroom on the first floor.", "facilities": ["Projector", "Sound System"], "department": "First Year UG"},
            {"room_number": "LH-4", "room_name": "Lecture Hall 4", "building_id": lhc_db_id, "floor": 1, "room_type": "Classroom", "capacity": 120, "description": "Smart classroom on the first floor.", "facilities": ["Projector", "Sound System"], "department": "First Year UG"}
        ])
        
    if cse_db_id:
        rooms.extend([
            {"room_number": "CS-102", "room_name": "Algorithm Lab", "building_id": cse_db_id, "floor": 0, "room_type": "Laboratory", "capacity": 60, "description": "High performance programming lab.", "facilities": ["Computers", "AC", "Projector"], "department": "Computer Science"},
            {"room_number": "CS-201", "room_name": "Seminar Room", "building_id": cse_db_id, "floor": 1, "room_type": "Seminar Hall", "capacity": 80, "description": "Air-conditioned seminar room.", "facilities": ["AC", "Projector", "Sound System"], "department": "Computer Science"},
            {"room_number": "CS-305", "room_name": "HOD Cabin", "building_id": cse_db_id, "floor": 2, "room_type": "Office", "capacity": 5, "description": "Department Head office chamber.", "facilities": ["AC", "Intercom"], "department": "Computer Science"}
        ])
        
    if lib_db_id:
        rooms.extend([
            {"room_number": "LIB-RD", "room_name": "Reading Room", "building_id": lib_db_id, "floor": 0, "room_type": "Reading Space", "capacity": 200, "description": "Silent reading section.", "facilities": ["AC", "Wi-Fi"], "department": "Library Services"},
            {"room_number": "LIB-EL", "room_name": "E-Library Section", "building_id": lib_db_id, "floor": 1, "room_type": "Computer Lab", "capacity": 50, "description": "Digital reference database section.", "facilities": ["Computers", "Wi-Fi"], "department": "Library Services"}
        ])
        
    for r in rooms:
        r["latitude"] = 0.0
        r["longitude"] = 0.0
        r["created_at"] = datetime.now(timezone.utc)
        r["updated_at"] = datetime.now(timezone.utc)
        await db.rooms.insert_one(r)
        
    print(f"Seeded {len(rooms)} Academic and Department rooms.")

    # 4. Facilities
    facilities_path = os.path.join(project_root, "data", "maps", "facilities.json")
    with open(facilities_path, "r", encoding="utf-8") as f:
        facilities_json = json.load(f)
        
    for fj in facilities_json:
        name = fj["name"]
        osm_type, osm_id, cat = FACILITY_MAP.get(name, ("way", 0, fj.get("category", "Other")))
        
        facility_doc = {
            "name": name,
            "latitude": fj.get("latitude", 0.0),
            "longitude": fj.get("longitude", 0.0),
            "osm_type": osm_type,
            "osm_id": osm_id,
            "coordinates": {"latitude": fj.get("latitude", 0.0), "longitude": fj.get("longitude", 0.0)},
            "category": cat,
            "timing": fj.get("timings") or fj.get("timing") or "",
            "services": [name] + (["OPD", "Pharmacy"] if "Medical" in name or "Pharmacy" in name else []) + (["Food", "Coffee"] if "Nescafe" in name or "Cafeteria" in name or "Cafe" in name or "Dhaba" in name or "Factory" in name else []) + (["Withdrawal", "Deposit"] if "SBI" in name else []),
            "accessibility": {
                "wheelchair_accessible": True
            },
            "metadata": {
                "description": fj.get("description", ""),
                "location_details": fj.get("location", ""),
                "search_keywords": fj.get("search_keywords", []),
                "associated_building": fj.get("associated_building", None)
            }
        }
        await db.facilities.insert_one(facility_doc)
        
    print(f"Seeded {len(facilities_json)} Facilities.")

    # 5. Landmarks
    landmarks = [
        {"name": "Main Gate", "category": "Gate", "description": "Security-controlled entrance gate of Birla Institute of Technology, Mesra."},
        {"name": "Clock Tower", "category": "Tower", "description": "Famous architectural heritage tower standing in front of the Admin block."},
        {"name": "Central Lawn", "category": "Lawn", "description": "Lush green lawn hosting evening debates, gatherings, and flower shows."},
        {"name": "Saraswati Temple (Statue)", "category": "Statue", "description": "Peaceful worship point surrounded by gardens."},
        {"name": "Main Fountain", "category": "Fountain", "description": "Operational fountain in the main rotunda courtyard."}
    ]
    
    for l in landmarks:
        osm_type, osm_id = LANDMARK_OSM_MAP.get(l["name"], ("way", 0))
        l["latitude"] = 0.0
        l["longitude"] = 0.0
        l["osm_type"] = osm_type
        l["osm_id"] = osm_id
        l["coordinates"] = {"latitude": 0.0, "longitude": 0.0}
        l["image"] = None
        l["metadata"] = {}
        await db.landmarks.insert_one(l)
        
    print(f"Seeded {len(landmarks)} Landmarks.")

    # 6. Pathways
    # Create realistic walkway paths containing coordinate bends (geometry)
    # Kept for unit testing and backward compatibility in mock environments
    pathways = [
        {
            "start_node": {"id": "main_gate", "type": "landmark", "name": "Main Gate"},
            "end_node": {"id": "guest_house", "type": "building", "name": "Guest House"},
            "path_type": "road", "distance": 180.0, "surface": "asphalt", "accessible": True, "lighting": "excellent", "notes": "Main boulevard entry road.",
            "geometry": [[23.4082, 85.4452], [23.4090, 85.4445], [23.4095, 85.4435]]
        },
        {
            "start_node": {"id": "guest_house", "type": "building", "name": "Guest House"},
            "end_node": {"id": "admin_building", "type": "building", "name": "Main Administrative Building"},
            "path_type": "road", "distance": 550.0, "surface": "asphalt", "accessible": True, "lighting": "excellent", "notes": "Main entrance boulevard.",
            "geometry": [[23.4095, 85.4435], [23.4110, 85.4420], [23.4125, 85.4405], [23.4142, 85.4388]]
        },
        {
            "start_node": {"id": "admin_building", "type": "building", "name": "Main Administrative Building"},
            "end_node": {"id": "clock_tower", "type": "landmark", "name": "Clock Tower"},
            "path_type": "walkway", "distance": 25.0, "surface": "tile", "accessible": True, "lighting": "excellent", "notes": "Paved tiles.",
            "geometry": [[23.4142, 85.4388], [23.41415, 85.4389], [23.4141, 85.4390]]
        },
        {
            "start_node": {"id": "clock_tower", "type": "landmark", "name": "Clock Tower"},
            "end_node": {"id": "central_library", "type": "building", "name": "Central Library"},
            "path_type": "walkway", "distance": 120.0, "surface": "concrete", "accessible": True, "lighting": "excellent", "notes": "Walkway bypassing Central Lawn.",
            "geometry": [[23.4141, 85.4390], [23.4144, 85.4397], [23.4150, 85.4400]]
        },
        {
            "start_node": {"id": "central_library", "type": "building", "name": "Central Library"},
            "end_node": {"id": "lecture_hall_complex", "type": "building", "name": "Lecture Hall Complex"},
            "path_type": "walkway", "distance": 50.0, "surface": "concrete", "accessible": True, "lighting": "excellent", "notes": "Direct connector crossing.",
            "geometry": [[23.4150, 85.4400], [23.41525, 85.43975], [23.4155, 85.4395]]
        },
        {
            "start_node": {"id": "lecture_hall_complex", "type": "building", "name": "Lecture Hall Complex"},
            "end_node": {"id": "cse_department", "type": "building", "name": "Department of Computer Science and Engineering"},
            "path_type": "walkway", "distance": 80.0, "surface": "concrete", "accessible": True, "lighting": "moderate", "notes": "Paved pathway alongside Nescafe.",
            "geometry": [[23.4155, 85.4395], [23.4158, 85.4390], [23.4162, 85.4385]]
        },
        {
            "start_node": {"id": "admin_building", "type": "building", "name": "Main Administrative Building"},
            "end_node": {"id": "ece_department", "type": "building", "name": "Department of Electronics and Communication Engineering"},
            "path_type": "walkway", "distance": 180.0, "surface": "concrete", "accessible": True, "lighting": "excellent", "notes": "West wing path.",
            "geometry": [[23.4142, 85.4388], [23.4145, 85.4380], [23.4148, 85.4372]]
        },
        {
            "start_node": {"id": "ece_department", "type": "building", "name": "Department of Electronics and Communication Engineering"},
            "end_node": {"id": "ee_department", "type": "building", "name": "Department of Electrical Engineering"},
            "path_type": "walkway", "distance": 90.0, "surface": "concrete", "accessible": True, "lighting": "moderate", "notes": "Electrical wing connector.",
            "geometry": [[23.4148, 85.4372], [23.4144, 85.4370], [23.4140, 85.4368]]
        },
        {
            "start_node": {"id": "ee_department", "type": "building", "name": "Department of Electrical Engineering"},
            "end_node": {"id": "mech_department", "type": "building", "name": "Department of Mechanical Engineering"},
            "path_type": "walkway", "distance": 340.0, "surface": "concrete", "accessible": True, "lighting": "moderate", "notes": "Mechanical hangar road.",
            "geometry": [[23.4140, 85.4368], [23.4125, 85.4364], [23.4110, 85.4360]]
        },
        {
            "start_node": {"id": "mech_department", "type": "building", "name": "Department of Mechanical Engineering"},
            "end_node": {"id": "civil_department", "type": "building", "name": "Department of Civil Engineering"},
            "path_type": "walkway", "distance": 70.0, "surface": "concrete", "accessible": True, "lighting": "moderate", "notes": "Civil wing road.",
            "geometry": [[23.4110, 85.4360], [23.4108, 85.4358], [23.4105, 85.4355]]
        },
        {
            "start_node": {"id": "admin_building", "type": "building", "name": "Main Administrative Building"},
            "end_node": {"id": "aiml_department", "type": "building", "name": "Department of Artificial Intelligence and Machine Learning"},
            "path_type": "walkway", "distance": 80.0, "surface": "concrete", "accessible": True, "lighting": "excellent", "notes": "AI center path.",
            "geometry": [[23.4142, 85.4388], [23.4138, 85.4390], [23.4135, 85.4392]]
        },
        {
            "start_node": {"id": "aiml_department", "type": "building", "name": "Department of Artificial Intelligence and Machine Learning"},
            "end_node": {"id": "ric_building", "type": "building", "name": "Research and Innovation Center"},
            "path_type": "walkway", "distance": 90.0, "surface": "concrete", "accessible": True, "lighting": "excellent", "notes": "Research zone link.",
            "geometry": [[23.4135, 85.4392], [23.4133, 85.4397], [23.4132, 85.4402]]
        },
        {
            "start_node": {"id": "ric_building", "type": "building", "name": "Research and Innovation Center"},
            "end_node": {"id": "sac_building", "type": "building", "name": "Student Activity Center"},
            "path_type": "walkway", "distance": 210.0, "surface": "concrete", "accessible": True, "lighting": "excellent", "notes": "RIC-SAC walkway.",
            "geometry": [[23.4132, 85.4402], [23.4122, 85.4410], [23.4115, 85.4418]]
        },
        {
            "start_node": {"id": "sac_building", "type": "building", "name": "Student Activity Center"},
            "end_node": {"id": "biotech_department", "type": "building", "name": "Department of Biotechnology"},
            "path_type": "walkway", "distance": 140.0, "surface": "concrete", "accessible": True, "lighting": "moderate", "notes": "Biotech crossing.",
            "geometry": [[23.4115, 85.4418], [23.4120, 85.4424], [23.4125, 85.4430]]
        },
        {
            "start_node": {"id": "central_library", "type": "building", "name": "Central Library"},
            "end_node": {"id": "sports_complex", "type": "building", "name": "Sports Complex"},
            "path_type": "walkway", "distance": 350.0, "surface": "concrete", "accessible": True, "lighting": "moderate", "notes": "Gymnasium lane.",
            "geometry": [[23.4150, 85.4400], [23.4165, 85.4410], [23.4180, 85.4420]]
        },
        {
            "start_node": {"id": "sports_complex", "type": "building", "name": "Sports Complex"},
            "end_node": {"id": "h1_hostel", "type": "building", "name": "Aryabhatta Hostel"},
            "path_type": "walkway", "distance": 150.0, "surface": "concrete", "accessible": True, "notes": "Hostel Zone 1 entry.",
            "geometry": [[23.4180, 85.4420], [23.4185, 85.4412], [23.4190, 85.4405]]
        },
        {
            "start_node": {"id": "h1_hostel", "type": "building", "name": "Aryabhatta Hostel"},
            "end_node": {"id": "h2_hostel", "type": "building", "name": "Raman Hostel"},
            "path_type": "walkway", "distance": 100.0, "surface": "concrete", "accessible": True, "notes": "Hostel 1 to 2 connector.",
            "geometry": [[23.4190, 85.4405], [23.4192, 85.4410], [23.4195, 85.4415]]
        },
        {
            "start_node": {"id": "h2_hostel", "type": "building", "name": "Raman Hostel"},
            "end_node": {"id": "h3_hostel", "type": "building", "name": "CV Raman Hostel"},
            "path_type": "walkway", "distance": 110.0, "surface": "concrete", "accessible": True, "notes": "Hostel 2 to 3 connector.",
            "geometry": [[23.4195, 85.4415], [23.4198, 85.4420], [23.4200, 85.4425]]
        },
        {
            "start_node": {"id": "h3_hostel", "type": "building", "name": "CV Raman Hostel"},
            "end_node": {"id": "h4_hostel", "type": "building", "name": "Vivekananda Hostel"},
            "path_type": "walkway", "distance": 110.0, "surface": "concrete", "accessible": True, "notes": "Hostel 3 to 4 connector.",
            "geometry": [[23.4200, 85.4425], [23.4202, 85.4430], [23.4205, 85.4435]]
        },
        {
            "start_node": {"id": "main_gate", "type": "landmark", "name": "Main Gate"},
            "end_node": {"id": "h8_hostel", "type": "building", "name": "International Students Hostel"},
            "path_type": "walkway", "distance": 380.0, "surface": "concrete", "accessible": True, "notes": "East girls hostel loop.",
            "geometry": [[23.4082, 85.4452], [23.4076, 85.4426], [23.4070, 85.4400]]
        },
        {
            "start_node": {"id": "h8_hostel", "type": "building", "name": "International Students Hostel"},
            "end_node": {"id": "h5_hostel", "type": "building", "name": "Gargi Hostel"},
            "path_type": "walkway", "distance": 140.0, "surface": "concrete", "accessible": True, "notes": "Text book girls hostel 5 link.",
            "geometry": [[23.4070, 85.4400], [23.4065, 85.4395], [23.4060, 85.4390]]
        },
        {
            "start_node": {"id": "h5_hostel", "type": "building", "name": "Gargi Hostel"},
            "end_node": {"id": "h6_hostel", "type": "building", "name": "Sarojini Hostel"},
            "path_type": "walkway", "distance": 110.0, "surface": "concrete", "accessible": True, "notes": "Girls Hostel 5 to 6.",
            "geometry": [[23.4060, 85.4390], [23.4057, 85.4385], [23.4055, 85.4380]]
        },
        {
            "start_node": {"id": "h6_hostel", "type": "building", "name": "Sarojini Hostel"},
            "end_node": {"id": "h7_hostel", "type": "building", "name": "New Girls Hostel"},
            "path_type": "walkway", "distance": 110.0, "surface": "concrete", "accessible": True, "notes": "Girls Hostel 6 to 7.",
            "geometry": [[23.4055, 85.4380], [23.4052, 85.4375], [23.4050, 85.4370]]
        }
    ]
    
    # Resolve actual DB IDs if possible
    async def resolve_node_id(node):
        code_mapping = {
            "guest_house": "GUEST",
            "admin_building": "MAIN",
            "central_library": "LIB",
            "lecture_hall_complex": "LHC",
            "cse_department": "CSE",
            "ece_department": "ECE",
            "ee_department": "EE",
            "mech_department": "MECH",
            "civil_department": "CIVIL",
            "aiml_department": "AIML",
            "ric_building": "RIC",
            "sac_building": "SAC",
            "biotech_department": "BIOTECH",
            "sports_complex": "SPORTS",
            "h1_hostel": "H1",
            "h2_hostel": "H2",
            "h3_hostel": "H3",
            "h4_hostel": "H4",
            "h5_hostel": "H5",
            "h6_hostel": "H6",
            "h7_hostel": "H7",
            "h8_hostel": "H8"
        }
        
        if node["id"] in code_mapping:
            b_code = code_mapping[node["id"]]
            doc = await db.buildings.find_one({"building_code": b_code})
            if doc: 
                node["id"] = str(doc["_id"])
        elif node["id"] == "main_gate":
            doc = await db.landmarks.find_one({"name": "Main Gate"})
            if doc: 
                node["id"] = str(doc["_id"])
        elif node["id"] == "clock_tower":
            doc = await db.landmarks.find_one({"name": "Clock Tower"})
            if doc: 
                node["id"] = str(doc["_id"])
            
    for p in pathways:
        await resolve_node_id(p["start_node"])
        await resolve_node_id(p["end_node"])
        p["metadata"] = {}
        await db.pathways.insert_one(p)
        
    print(f"Seeded {len(pathways)} walkable pathways.")
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    asyncio.run(seed_data())
