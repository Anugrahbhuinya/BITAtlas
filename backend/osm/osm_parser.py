# backend/osm/osm_parser.py

import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple, Any, Optional

def parse_osm_file(filepath: str) -> Tuple[Dict[str, Dict[str, Any]], List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    """
    Parses the OpenStreetMap XML file.
    Returns:
      - nodes: Dict[node_id, node_data]
      - ways: List of walkable ways
      - elements: Dict of all elements (nodes, ways, relations) indexed by "type_id"
    """
    tree = ET.parse(filepath)
    root = tree.getroot()

    nodes: Dict[str, Dict[str, Any]] = {}
    ways: List[Dict[str, Any]] = []
    elements: Dict[str, Dict[str, Any]] = {}

    # 1. Parse nodes
    for child in root.findall("node"):
        n_id = child.attrib["id"]
        lat = float(child.attrib["lat"])
        lon = float(child.attrib["lon"])
        tags = {}
        for tag in child.findall("tag"):
            tags[tag.attrib["k"]] = tag.attrib["v"]
        
        node_data = {
            "type": "node",
            "id": n_id,
            "latitude": lat,
            "longitude": lon,
            "tags": tags,
            "name": tags.get("name")
        }
        nodes[n_id] = node_data
        elements[f"node_{n_id}"] = node_data

    # 2. Parse ways
    for child in root.findall("way"):
        w_id = child.attrib["id"]
        tags = {}
        for tag in child.findall("tag"):
            tags[tag.attrib["k"]] = tag.attrib["v"]

        way_nodes = [nd.attrib["ref"] for nd in child.findall("nd")]
        way_nodes = [ref for ref in way_nodes if ref in nodes]
        
        way_data = {
            "type": "way",
            "id": w_id,
            "nodes": way_nodes,
            "tags": tags,
            "name": tags.get("name")
        }
        elements[f"way_{w_id}"] = way_data

        highway = tags.get("highway")
        if highway:
            # Walkability check based on highway tags
            is_walkable = highway in ["footway", "path", "pedestrian", "service", "residential", "steps", "track", "unclassified", "living_street"]
            if tags.get("foot") == "no":
                is_walkable = False
            if tags.get("foot") == "yes" or tags.get("pedestrian") == "yes":
                is_walkable = True

            if is_walkable and len(way_nodes) >= 2:
                ways.append(way_data)

    # 3. Parse relations
    for child in root.findall("relation"):
        r_id = child.attrib["id"]
        tags = {}
        for tag in child.findall("tag"):
            tags[tag.attrib["k"]] = tag.attrib["v"]

        members = []
        for member in child.findall("member"):
            members.append({
                "type": member.attrib["type"],
                "ref": member.attrib["ref"],
                "role": member.attrib.get("role")
            })

        rel_data = {
            "type": "relation",
            "id": r_id,
            "members": members,
            "tags": tags,
            "name": tags.get("name")
        }
        elements[f"relation_{r_id}"] = rel_data

    return nodes, ways, elements

def get_element_geometry_and_centroid(
    element_type: str, 
    element_id: str, 
    nodes: Dict[str, Any], 
    elements: Dict[str, Any],
    referenced_osm_ids: set
) -> Tuple[List[List[float]], Tuple[float, float], Optional[Tuple[float, float]]]:
    """
    Returns:
      - geometry: list of [lat, lon] coordinates representing the boundary or path points
      - centroid: (lat, lon) coordinates
      - entrance: (lat, lon) coordinates if an entrance node is found, otherwise None
    """
    key = f"{element_type}_{element_id}"
    geom: List[List[float]] = []
    centroid: Tuple[float, float] = (0.0, 0.0)
    entrance: Optional[Tuple[float, float]] = None

    if key not in elements:
        return geom, centroid, entrance

    elem = elements[key]
    if element_type == "node":
        lat, lon = elem["latitude"], elem["longitude"]
        geom = [[lat, lon]]
        centroid = (lat, lon)
        if elem["tags"].get("entrance") == "yes":
            entrance = (lat, lon)
    elif element_type == "way":
        lat_sum = 0.0
        lon_sum = 0.0
        valid_nodes_count = 0
        
        # Check first for entrance tagged nodes or nodes intersecting road/paths network
        intersection_node = None
        tagged_entrance = None

        for nd_ref in elem["nodes"]:
            if nd_ref in nodes:
                nd = nodes[nd_ref]
                lat, lon = nd["latitude"], nd["longitude"]
                geom.append([lat, lon])
                lat_sum += lat
                lon_sum += lon
                valid_nodes_count += 1
                
                # Check for explicit entrance tag
                if nd["tags"].get("entrance") == "yes" or "entrance" in nd["tags"]:
                    tagged_entrance = (lat, lon)
                
                # Check for intersection with path network
                if nd_ref in referenced_osm_ids:
                    intersection_node = (lat, lon)
        
        if valid_nodes_count > 0:
            centroid = (lat_sum / valid_nodes_count, lon_sum / valid_nodes_count)
            # Entrance priority: 1. Tagged entrance, 2. Walkway intersection, 3. Centroid fallback
            if tagged_entrance:
                entrance = tagged_entrance
            elif intersection_node:
                entrance = intersection_node
            elif len(geom) > 0:
                entrance = (geom[0][0], geom[0][1])
        else:
            centroid = (0.0, 0.0)
            
    elif element_type == "relation":
        lat_sum = 0.0
        lon_sum = 0.0
        valid_nodes_count = 0
        
        for member in elem["members"]:
            m_type = member["type"]
            m_ref = member["ref"]
            if m_type == "node" and m_ref in nodes:
                nd = nodes[m_ref]
                lat, lon = nd["latitude"], nd["longitude"]
                geom.append([lat, lon])
                lat_sum += lat
                lon_sum += lon
                valid_nodes_count += 1
                if nd["tags"].get("entrance") == "yes":
                    entrance = (lat, lon)
            elif m_type == "way":
                way_key = f"way_{m_ref}"
                if way_key in elements:
                    w = elements[way_key]
                    for nd_ref in w["nodes"]:
                        if nd_ref in nodes:
                            nd = nodes[nd_ref]
                            lat, lon = nd["latitude"], nd["longitude"]
                            geom.append([lat, lon])
                            lat_sum += lat
                            lon_sum += lon
                            valid_nodes_count += 1
                            if nd["tags"].get("entrance") == "yes":
                                entrance = (lat, lon)
                                
        if valid_nodes_count > 0:
            centroid = (lat_sum / valid_nodes_count, lon_sum / valid_nodes_count)
            if not entrance and len(geom) > 0:
                entrance = (geom[0][0], geom[0][1])
        else:
            centroid = (0.0, 0.0)

    return geom, centroid, entrance
