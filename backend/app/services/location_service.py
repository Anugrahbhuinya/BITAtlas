from app.utils.loader import load_json

buildings = load_json("maps/buildings.json")
hostels = load_json("maps/hostels.json")
facilities = load_json("maps/facilities.json")
departments = load_json("academics/departments.json")


def get_all_locations():
    locations = []
    
    # 1. Parse buildings
    for name, info in buildings.items():
        locations.append({
            "name": name,
            "description": info.get("description") or f"{name} ({info.get('type', 'building')})"
        })
        
    # 2. Parse hostels
    for name, info in hostels.items():
        locations.append({
            "name": name,
            "description": info.get("description") or f"{name} ({info.get('type', 'hostel').replace('_', ' ')})"
        })
        
    # 3. Parse facilities
    for name, info in facilities.items():
        desc = f"{name}"
        category = info.get("category")
        if category:
            desc += f" ({category})"
        if "opening_time" in info and "closing_time" in info:
            desc += f" [Open: {info['opening_time']} - {info['closing_time']}]"
        locations.append({
            "name": name,
            "description": desc
        })
        
    # 4. Parse departments
    for code, info in departments.items():
        name = info.get("name", code)
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
        locations.append({
            "name": name,
            "code": code,
            "description": desc
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