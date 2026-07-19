# backend/scripts/merge_txt_data.py

import os
import sys
import json
import re

# Setup paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

# File paths
KNOWLEDGE_TXT = r"C:\Users\ASUS\Downloads\knowledge.txt"
LOCATIONS_TXT = r"C:\Users\ASUS\Downloads\locations.txt"

FAQ_JSON = os.path.join(PROJECT_ROOT, "data", "faqs", "student_faqs.json")
BUILDINGS_JSON = os.path.join(PROJECT_ROOT, "data", "maps", "buildings.json")
FACILITIES_JSON = os.path.join(PROJECT_ROOT, "data", "maps", "facilities.json")
HOSTELS_JSON = os.path.join(PROJECT_ROOT, "data", "maps", "hostels.json")
DEPARTMENTS_JSON = os.path.join(PROJECT_ROOT, "data", "academics", "departments.json")

print("[DEV DEBUG] starting TXT Knowledge Conversion & Location Merging...")

# Helper to normalize questions for comparison
def normalize_text(text):
    if not text:
        return ""
    return re.sub(r"[^\w\s]", "", text.lower()).replace(" ", "").strip()

# ==============================================================================
# 1. PARSE & MERGE FAQs (knowledge.txt)
# ==============================================================================
print(f"[DEV DEBUG] Ingesting FAQs from: {KNOWLEDGE_TXT}")

if not os.path.exists(KNOWLEDGE_TXT):
    print(f"[ERROR] knowledge.txt not found at {KNOWLEDGE_TXT}")
    sys.exit(1)

with open(KNOWLEDGE_TXT, "r", encoding="utf-8") as f:
    knowledge_content = f.read()

# Load existing FAQs
with open(FAQ_JSON, "r", encoding="utf-8") as f:
    existing_faqs = json.load(f)

# Keep track of existing questions to avoid duplicates
existing_questions_normalized = {normalize_text(faq["question"]) for faq in existing_faqs}
next_faq_id = max(faq["id"] for faq in existing_faqs) + 1 if existing_faqs else 1

# Split FAQs by the separator line
faq_blocks = knowledge_content.split("==================================================================")
faqs_added = 0

for block in faq_blocks:
    block = block.strip()
    if not block:
        continue
    
    # Parse Q and A
    q_match = re.search(r"^Q:\s*(.*?)\n\s*A:\s*(.*)$", block, re.DOTALL | re.IGNORECASE)
    if q_match:
        question = q_match.group(1).strip()
        answer = q_match.group(2).strip()
        
        print(f"[DEV DEBUG] [TXT Parsing] Parsing FAQ: Question='{question[:40]}...'")
        print(f"[DEV DEBUG] [Category Detection] Category detected: FAQ")
        
        norm_q = normalize_text(question)
        print(f"[DEV DEBUG] [Duplicate Detection] Checking duplication: Question='{question[:40]}...'")
        
        if norm_q in existing_questions_normalized:
            print(f"[DEV DEBUG] [Duplicate Detection] FAQ Duplicate Ignored: Question='{question[:40]}...'")
        else:
            new_faq = {
                "id": next_faq_id,
                "question": question,
                "answer": answer
            }
            existing_faqs.append(new_faq)
            existing_questions_normalized.add(norm_q)
            print(f"[DEV DEBUG] [JSON Merge] FAQ Parsed & Merged: Question='{question[:40]}...' (ID: {next_faq_id})")
            next_faq_id += 1
            faqs_added += 1
    else:
        print(f"[WARNING] Could not parse FAQ block: {block[:50]}...")

# Write back FAQs
print(f"[DEV DEBUG] [Knowledge Ingestion] Ingesting FAQs... Writing to {FAQ_JSON}")
with open(FAQ_JSON, "w", encoding="utf-8") as f:
    json.dump(existing_faqs, f, indent=2, ensure_ascii=False)

print(f"[DEV DEBUG] Knowledge Ingestion Complete: Merged {faqs_added} new FAQs into {FAQ_JSON}")


# ==============================================================================
# 2. PARSE & MERGE LOCATIONS (locations.txt)
# ==============================================================================
print(f"[DEV DEBUG] Ingesting Locations from: {LOCATIONS_TXT}")

if not os.path.exists(LOCATIONS_TXT):
    print(f"[ERROR] locations.txt not found at {LOCATIONS_TXT}")
    sys.exit(1)

# Load existing maps JSONs
with open(BUILDINGS_JSON, "r", encoding="utf-8") as f:
    buildings = json.load(f)
with open(FACILITIES_JSON, "r", encoding="utf-8") as f:
    facilities = json.load(f)
with open(HOSTELS_JSON, "r", encoding="utf-8") as f:
    hostels = json.load(f)
with open(DEPARTMENTS_JSON, "r", encoding="utf-8") as f:
    departments = json.load(f)

# Function to build standardized fields for any location object
def build_required_location_fields(obj, name, category, lat, lon, description="", aliases=None, search_keywords=None, associated_building=None):
    # Enforce exact Title Case properties
    obj["Name"] = name
    obj["Category"] = category
    obj["Latitude"] = lat
    obj["Longitude"] = lon
    obj["Description"] = description or obj.get("description", "")
    
    # Aliases
    if aliases is None:
        aliases = obj.get("aliases", [name])
    if name not in aliases:
        aliases.append(name)
    obj["Aliases"] = aliases
    
    # Search Keywords
    if search_keywords is None:
        search_keywords = obj.get("search_keywords", [w.strip(",.()\"'") for w in name.lower().split() if len(w) > 2])
    obj["Search Keywords"] = search_keywords
    
    # Associated Building
    obj["Associated Building"] = associated_building or obj.get("associated_building", None)
    
    # Keep snake_case equivalents for backend compatibility
    obj["name"] = name
    obj["category"] = category
    obj["latitude"] = lat
    obj["longitude"] = lon
    obj["description"] = obj["Description"]
    obj["aliases"] = obj["Aliases"]
    obj["search_keywords"] = obj["Search Keywords"]
    obj["associated_building"] = obj["Associated Building"]
    return obj

hostels_by_id = {h["id"]: h for h in hostels}
buildings_by_name = {b["name"].lower(): b for b in buildings}
facilities_by_name = {f["name"].lower(): f for f in facilities}
departments_by_name = {d["name"].lower(): d for d in departments}

# Parse lines from locations.txt
locations_parsed = 0
locations_merged = 0
locations_new = 0

with open(LOCATIONS_TXT, "r", encoding="utf-8") as f:
    for line_num, line in enumerate(f, 1):
        line = line.strip()
        if not line:
            continue
        
        # Parse Name, Latitude, Longitude
        match = re.match(r'^(.+?)(?:\s*-\s*|\s*:\s*)(\d+\.\d+)\s*,\s*(\d+\.\d+)$', line)
        if not match:
            print(f"[WARNING] Skipping unparseable location line {line_num}: {line}")
            continue
            
        raw_name, lat_str, lon_str = match.groups()
        name = raw_name.strip()
        lat = float(lat_str)
        lon = float(lon_str)
        locations_parsed += 1
        
        print(f"[DEV DEBUG] [TXT Parsing] Line {line_num}: name='{name}' -> ({lat}, {lon})")
        
        # Clean suffixes for matching
        clean_name = re.sub(
            r"\s*(?:,\s*BIT\s*Mesra|,\s*BIT,\s*Mesra|-?\s*BIT,\s*Mesra|,\s*Birla\s*Institute\s*of\s*Technology,\s*Mesra|,\s*Birla\s*Institute\s*of\s*Technology\s*-\s*Mesra)\s*$", 
            "", 
            name, 
            flags=re.IGNORECASE
        ).strip()
        name_lower = clean_name.lower()
        
        # --- Category Detection & Matching ---
        # 1. HOSTELS
        if "hostel" in name_lower:
            print(f"[DEV DEBUG] [Category Detection] Detected category: Hostel")
            num_match = re.search(r"hostel\s*(\d+)", name_lower)
            hid = int(num_match.group(1)) if num_match else None
            
            print(f"[DEV DEBUG] [Duplicate Detection] Checking if hostel ID {hid} exists...")
            if hid and hid in hostels_by_id:
                # Merge into existing hostel
                h = hostels_by_id[hid]
                build_required_location_fields(h, h["name"], "Residential", lat, lon, h.get("description"), h.get("aliases", [h["name"], f"Hostel {hid}"]), None, None)
                print(f"[DEV DEBUG] [Coordinate Merge] Coordinate Merge: Name='{name}' merged into Hostel ID {hid} ({h['name']})")
                print(f"[DEV DEBUG] [Map Registration] Hostel '{h['name']}' coordinate updated")
                locations_merged += 1
            elif hid:
                # Register new Hostel
                new_h = {
                    "id": hid,
                    "name": f"Hostel {hid}",
                    "gender": "Male" if hid in [9, 10, 11, 12, 13] else "Co-ed",
                    "capacity": 350
                }
                desc = f"Student residential hostel {hid} located at the hostel zone of the BIT Mesra campus."
                build_required_location_fields(new_h, new_h["name"], "Residential", lat, lon, desc, [new_h["name"], f"H{hid}"], None, None)
                hostels.append(new_h)
                hostels_by_id[hid] = new_h
                print(f"[DEV DEBUG] [JSON Merge] Location Registered: Name='{name}' (Hostel ID: {hid})")
                print(f"[DEV DEBUG] [Map Registration] Hostel '{new_h['name']}' registered on campus map")
                locations_new += 1
        
        # 2. BUILDINGS (Academic/Administrative Blocks)
        elif any(k in name_lower for k in ["department", "dept", "faculty chambers", "lecture hall", "main building", "academic", "administrative", "research", "library"]):
            print(f"[DEV DEBUG] [Category Detection] Detected category: Building")
            # Normalize names to check matches
            matched_b = None
            for b_name, b_obj in buildings_by_name.items():
                b_code = b_obj.get("building_code", "").lower()
                # Exact or substring match of the name
                if b_name == name_lower or (len(b_name) > 10 and b_name in name_lower) or (len(name_lower) > 10 and name_lower in b_name):
                    matched_b = b_obj
                    break
                # Code match as a whole word
                if b_code and len(b_code) >= 2 and re.search(r"\b" + re.escape(b_code) + r"\b", name_lower):
                    matched_b = b_obj
                    break
            
            print(f"[DEV DEBUG] [Duplicate Detection] Checking if building '{clean_name}' exists...")
            if matched_b:
                # Merge coordinates
                build_required_location_fields(matched_b, matched_b["name"], matched_b["category"], lat, lon, matched_b.get("description"), matched_b.get("aliases"), None, None)
                print(f"[DEV DEBUG] [Coordinate Merge] Coordinate Merge: Name='{name}' merged into Building ID {matched_b['id']} ({matched_b['name']})")
                print(f"[DEV DEBUG] [Map Registration] Building '{matched_b['name']}' coordinate updated")
                locations_merged += 1
            else:
                # Register new Building
                next_id = max(b["id"] for b in buildings) + 1 if buildings else 1
                words = clean_name.replace("Department of", "").replace("Department", "").split()
                code = "".join(w[0] for w in words if w[0].isupper())[:6]
                if not code or len(code) < 2:
                    code = clean_name.replace(" ", "")[:4].upper()
                
                new_b = {
                    "id": next_id,
                    "name": clean_name,
                    "location": f"Academic Zone, BIT Mesra",
                    "category": "Academic"
                }
                desc = f"The {clean_name} building at BIT Mesra campus houses academic classrooms, laboratories, faculty chambers, and research facilities."
                build_required_location_fields(new_b, clean_name, "Academic", lat, lon, desc, [clean_name, code], None, None)
                new_b["building_code"] = code
                
                buildings.append(new_b)
                buildings_by_name[clean_name.lower()] = new_b
                print(f"[DEV DEBUG] [JSON Merge] Location Registered: Name='{clean_name}' (Building ID: {next_id})")
                print(f"[DEV DEBUG] [Map Registration] Building '{clean_name}' registered on campus map")
                locations_new += 1
                
            # Also merge into departments.json if there is a matching department
            for dept_name, d_obj in departments_by_name.items():
                if dept_name in name_lower or name_lower in dept_name:
                    d_obj["latitude"] = lat
                    d_obj["longitude"] = lon
                    d_obj["Latitude"] = lat
                    d_obj["Longitude"] = lon
                    print(f"[DEV DEBUG] [JSON Merge] Department Coordinate Synced: Department '{d_obj['name']}' -> ({lat}, {lon})")

        # 3. FACILITIES (Shops, Canteens, ATMs, stands, Viewpoints, Landmarks)
        else:
            print(f"[DEV DEBUG] [Category Detection] Detected category: Facility")
            # Check existing facility matches
            matched_f = None
            for f_name, f_obj in facilities_by_name.items():
                if f_name == name_lower or (len(f_name) > 8 and f_name in name_lower) or (len(name_lower) > 8 and name_lower in f_name):
                    matched_f = f_obj
                    break
            
            print(f"[DEV DEBUG] [Duplicate Detection] Checking if facility '{clean_name}' exists...")
            if matched_f:
                build_required_location_fields(matched_f, matched_f["name"], matched_f.get("category", "Other"), lat, lon, matched_f.get("description"), matched_f.get("aliases"), None, None)
                print(f"[DEV DEBUG] [Coordinate Merge] Coordinate Merge: Name='{name}' merged into Facility ID {matched_f['id']} ({matched_f['name']})")
                print(f"[DEV DEBUG] [Map Registration] Facility '{matched_f['name']}' coordinate updated")
                locations_merged += 1
            else:
                # Register new Facility
                next_id = max(f["id"] for f in facilities) + 1 if facilities else 1
                cat = "Cafeteria" if any(k in name_lower for k in ["cafe", "canteen", "dhaba", "food", "pizza", "nescafe"]) else \
                      "ATM" if "atm" in name_lower else \
                      "Bank" if "bank" in name_lower else \
                      "Medical Centre" if "pharmacy" in name_lower or "medical" in name_lower else \
                      "Sports Complex" if any(k in name_lower for k in ["sports", "gym", "ground"]) else \
                      "Parking" if any(k in name_lower for k in ["parking", "stand"]) else \
                      "Other"
                      
                new_f = {
                    "id": next_id,
                    "name": clean_name,
                    "location": "BIT Mesra Campus",
                    "timings": "09:00 AM - 08:00 PM" if cat != "ATM" else "24 Hours"
                }
                desc = f"Campus facility {clean_name} serving students, faculty, and visitors at BIT Mesra."
                build_required_location_fields(new_f, clean_name, cat, lat, lon, desc, [clean_name], None, None)
                
                facilities.append(new_f)
                facilities_by_name[clean_name.lower()] = new_f
                print(f"[DEV DEBUG] [JSON Merge] Location Registered: Name='{clean_name}' (Facility ID: {next_id}, Category: {cat})")
                print(f"[DEV DEBUG] [Map Registration] Facility '{clean_name}' registered on campus map")
                locations_new += 1


# Ensure all existing buildings, hostels, and facilities also have the required fields filled in
for b in buildings:
    if "latitude" not in b: b["latitude"] = 0.0
    if "longitude" not in b: b["longitude"] = 0.0
    build_required_location_fields(b, b["name"], b.get("category", "Academic"), b["latitude"], b["longitude"], b.get("description"), b.get("aliases"), None, None)

for h in hostels:
    if "latitude" not in h: h["latitude"] = 0.0
    if "longitude" not in h: h["longitude"] = 0.0
    build_required_location_fields(h, h["name"], "Residential", h["latitude"], h["longitude"], h.get("description"), h.get("aliases"), None, None)

for fac in facilities:
    if "latitude" not in fac: fac["latitude"] = 0.0
    if "longitude" not in fac: fac["longitude"] = 0.0
    build_required_location_fields(fac, fac["name"], fac.get("category", "Other"), fac["latitude"], fac["longitude"], fac.get("description"), fac.get("aliases"), None, None)


# Write back maps files
with open(BUILDINGS_JSON, "w", encoding="utf-8") as f:
    json.dump(buildings, f, indent=2, ensure_ascii=False)
with open(HOSTELS_JSON, "w", encoding="utf-8") as f:
    json.dump(hostels, f, indent=2, ensure_ascii=False)
with open(FACILITIES_JSON, "w", encoding="utf-8") as f:
    json.dump(facilities, f, indent=2, ensure_ascii=False)
with open(DEPARTMENTS_JSON, "w", encoding="utf-8") as f:
    json.dump(departments, f, indent=2, ensure_ascii=False)

print("\n=======================================================")
print("MIGRATION STATISTICS:")
print(f"Total Locations Parsed: {locations_parsed}")
print(f"Total Coordinate Merges (Existing): {locations_merged}")
print(f"Total New Locations Registered: {locations_new}")
print("=======================================================")
print("[DEV DEBUG] Location Merging & Map Integration Completed Successfully.")
