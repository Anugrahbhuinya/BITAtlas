from app.utils.loader import load_json

buildings = load_json("maps/buildings.json")
hostels = load_json("maps/hostels.json")
facilities = load_json("maps/facilities.json")
departments = load_json("academics/departments.json")


def get_all_locations():
    locations = []
    
    # 1. Parse buildings
    for b in buildings:
        name = b.get("name", "")
        locations.append({
            "name": name,
            "description": b.get("description") or f"{name} ({b.get('category', 'building')})"
        })
        
    # 2. Parse hostels
    for h in hostels:
        name = h.get("name", "")
        locations.append({
            "name": name,
            "description": h.get("description") or f"{name} ({h.get('gender', 'hostel')})"
        })
        
    # 3. Parse facilities
    for f in facilities:
        name = f.get("name", "")
        desc = f.get("description") or name
        timings = f.get("timings")
        if timings:
            desc += f" [Timings: {timings}]"
        locations.append({
            "name": name,
            "description": desc
        })
        
    # 4. Parse departments
    for d in departments:
        name = d.get("name", "")
        desc = d.get("description", "")
        building = d.get("building", "")
        full_desc = f"Department of {name}: {desc} (Located in {building})"
        
        # Simple acronym code generation (e.g. Computer Science and Engineering -> CSE)
        words = name.split()
        code = "".join(w[0] for w in words if w[0].isupper())
        
        locations.append({
            "name": name,
            "code": code,
            "description": full_desc
        })
        
    return locations


def search_location(query):

    query = query.lower()
    all_locations = get_all_locations()

    for place in all_locations:

        name_match = place["name"].lower() in query
        code_match = "code" in place and place["code"].lower() in query.split()

        if name_match or code_match:

            return {
                "type": "location",
                "answer": place["description"]
            }

    return None