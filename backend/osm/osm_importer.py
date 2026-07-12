# backend/osm/osm_importer.py

import os
import requests
import xml.etree.ElementTree as ET

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

def get_fallback_osm_xml() -> str:
    """
    Returns a high-quality fallback OpenStreetMap XML representing the main walkways
    and buildings of BIT Mesra, ensuring offline reliability.
    """
    # Coordinates of major locations
    locs = {
        "admin": (23.4142, 85.4388),
        "library": (23.4150, 85.4400),
        "audi": (23.4120, 85.4410),
        "lhc": (23.4155, 85.4395),
        "cse": (23.4162, 85.4385),
        "aiml": (23.4135, 85.4392),
        "ece": (23.4148, 85.4372),
        "mech": (23.4110, 85.4360),
        "ee": (23.4140, 85.4368),
        "biotech": (23.4125, 85.4430),
        "ric": (23.4132, 85.4402),
        "sac": (23.4115, 85.4418),
        "sports": (23.4180, 85.4420),
        "guest": (23.4095, 85.4435),
        "h1": (23.4190, 85.4405),
        "h2": (23.4195, 85.4415),
        "h3": (23.4200, 85.4425),
        "h4": (23.4205, 85.4435),
        "h5": (23.4060, 85.4390),
        "h6": (23.4055, 85.4380),
        "h7": (23.4050, 85.4370),
        "h8": (23.4070, 85.4400),
        "medical": (23.4172, 85.4408),
        "cafeteria": (23.4148, 85.4392),
        "nescafe": (23.4158, 85.4389),
        "bank": (23.4138, 85.4394),
        "atm": (23.4138, 85.4395),
        "placement": (23.4142, 85.4388),
        "gym": (23.4180, 85.4420),
        "indoor": (23.4181, 85.4422),
        "store": (23.4118, 85.4442),
        "xerox": (23.4151, 85.4401),
        # Intersections
        "int_main_library": (23.4145, 85.4395),
        "int_lhc_cse": (23.4158, 85.4390),
        "int_admin_ece": (23.4145, 85.4380),
        "int_ee_mech": (23.4125, 85.4364),
        "int_audi_ric": (23.4126, 85.4406),
        "int_sac_biotech": (23.4120, 85.4424),
        "int_hostels_north": (23.4185, 85.4410),
        "int_hostels_south": (23.4065, 85.4385),
    }

    # Generate nodes
    nodes_xml = ""
    node_id_counter = 100001
    loc_to_id = {}
    for name, coords in locs.items():
        loc_to_id[name] = node_id_counter
        nodes_xml += f'  <node id="{node_id_counter}" lat="{coords[0]}" lon="{coords[1]}">\n    <tag k="name" v="{name}"/>\n  </node>\n'
        node_id_counter += 1

    # Connect ways representing walkways/roads
    ways_data = [
        ("Main Avenue North", ["h4", "h3", "h2", "h1", "int_hostels_north", "int_lhc_cse", "int_main_library", "int_audi_ric", "int_sac_biotech", "biotech"]),
        ("Main Avenue South", ["int_hostels_south", "h8", "h5", "h6", "h7"]),
        ("North-South Connector", ["int_hostels_north", "cse", "int_lhc_cse", "lhc", "library", "int_main_library", "admin", "int_admin_ece", "ee", "int_ee_mech", "mech"]),
        ("East Loop", ["library", "int_audi_ric", "audi", "ric", "sac", "int_sac_biotech", "guest", "sports"]),
        ("West Link", ["int_admin_ece", "ece"]),
        ("South Loop Connector", ["int_audi_ric", "int_hostels_south"]),
    ]

    ways_xml = ""
    way_id_counter = 500001
    for way_name, node_keys in ways_data:
        ways_xml += f'  <way id="{way_id_counter}">\n    <tag k="name" v="{way_name}"/>\n    <tag k="highway" v="footway"/>\n'
        for key in node_keys:
            ways_xml += f'    <nd ref="{loc_to_id[key]}"/>\n'
        ways_xml += '  </way>\n'
        way_id_counter += 1

    # Define building ways enclosing the respective node coordinates to represent buildings in OSM
    buildings_data = [
        ("Central Library", "library"),
        ("Main Administrative Building", "admin"),
        ("University Auditorium", "audi"),
        ("Lecture Hall Complex", "lhc"),
        ("Department of Computer Science and Engineering", "cse"),
        ("Department of Artificial Intelligence and Machine Learning", "aiml"),
        ("Department of Electronics and Communication Engineering", "ece"),
        ("Department of Mechanical Engineering", "mech"),
        ("Department of Electrical Engineering", "ee"),
        ("Department of Civil Engineering", "mech"),
        ("Department of Biotechnology", "biotech"),
        ("Research and Innovation Center", "ric"),
        ("Student Activity Center", "sac"),
        ("Sports Complex", "sports"),
        ("Guest House", "guest"),
        ("Aryabhatta Hostel", "h1"),
        ("Raman Hostel", "h2"),
        ("CV Raman Hostel", "h3"),
        ("Vivekananda Hostel", "h4"),
        ("Gargi Hostel", "h5"),
        ("Sarojini Hostel", "h6"),
        ("New Girls Hostel", "h7"),
        ("International Students Hostel", "h8"),
        ("Medical Unit", "medical"),
        ("Central Cafeteria", "cafeteria"),
        ("Nescafe Outlet", "nescafe"),
        ("SBI Bank Branch", "bank"),
        ("SBI ATM", "atm"),
        ("Placement and Training Cell", "placement"),
        ("Campus Gymnasium", "gym"),
        ("Indoor Sports Hall", "indoor"),
        ("Student Store", "store"),
        ("Stationery and Xerox Center", "xerox"),
    ]

    for b_name, node_key in buildings_data:
        ways_xml += f'  <way id="{way_id_counter}">\n    <tag k="name" v="{b_name}"/>\n    <tag k="building" v="yes"/>\n'
        ways_xml += f'    <nd ref="{loc_to_id[node_key]}"/>\n'
        ways_xml += '  </way>\n'
        way_id_counter += 1

    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<osm version="0.6" generator="AntigravityOSMImporter">
{nodes_xml}
{ways_xml}
</osm>"""
    return xml_content

def download_osm_data(filepath: str, force_download: bool = False) -> bool:
    """
    Downloads OSM XML from Overpass API or writes a fallback XML if network fails.
    """
    if os.path.exists(filepath) and not force_download:
        print(f"OSM file already exists at {filepath}, skipping download.")
        return True

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Overpass bounding box covering BIT Mesra campus
    bbox = "23.400,85.420,23.425,85.460"
    query = f"""[out:xml][timeout:25];
(
  way["highway"="footway"]({bbox});
  way["highway"="path"]({bbox});
  way["highway"="pedestrian"]({bbox});
  way["highway"="service"]({bbox});
  way["highway"="residential"]({bbox});
  way["highway"="steps"]({bbox});
  way["highway"="track"]({bbox});
  way["building"]({bbox});
  relation["building"]({bbox});
);
(._;>;);
out body;"""

    try:
        print(f"Downloading OpenStreetMap data for BIT Mesra from Overpass URL...")
        response = requests.post(OVERPASS_URL, data={"data": query}, timeout=15)
        if response.status_code == 200 and "<osm" in response.text:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"Successfully downloaded and saved OSM data to {filepath}")
            return True
        else:
            print(f"Overpass API failed with status code {response.status_code}. Using fallback XML.")
    except Exception as e:
        print(f"Network error querying Overpass API: {e}. Using fallback XML.")

    # Write fallback XML
    try:
        fallback_xml = get_fallback_osm_xml()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(fallback_xml)
        print(f"Fallback OSM XML successfully written to {filepath}")
        return True
    except Exception as ex:
        print(f"Failed to write fallback OSM XML: {ex}")
        return False
