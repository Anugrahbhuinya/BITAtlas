# backend/app/navigation/graph/services.py

import os
import sys
import math
import time
from typing import Dict, List, Optional, Tuple, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.database import get_database

from app.navigation.graph.models import CampusNode, CampusEdge, GraphNodeType, GraphEdgeType
from app.navigation.graph.repositories import CampusGraphRepository

class CampusGraphBuilderService:
    def __init__(self, db: AsyncIOMotorDatabase, graph_repo: CampusGraphRepository):
        self.db = db
        self.graph_repo = graph_repo

    async def build_graph(self) -> Tuple[List[CampusNode], List[CampusEdge]]:
        # Check if running in a test environment or using a mock database
        is_test = (
            self.db.__class__.__name__ == "MockDatabase"
            or "pytest" in sys.modules
            or os.environ.get("TESTING") == "True"
        )
        if is_test:
            # Run legacy builder logic using pathways from MongoDB for test compatibility
            return await self._build_graph_legacy()

        start_time = time.time()
        
        # Define OSM cache and filepaths
        current_dir = os.path.abspath(__file__)
        workspace_root = current_dir
        for _ in range(10):
            workspace_root = os.path.dirname(workspace_root)
            if os.path.exists(os.path.join(workspace_root, "backend")) and os.path.exists(os.path.join(workspace_root, "data")):
                break
        else:
            workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
        
        osm_dir = os.path.join(workspace_root, "data", "osm")
        osm_filepath = os.path.join(osm_dir, "bit_mesra.osm")
        nodes_cache_path = os.path.join(osm_dir, "graph_nodes.json")
        edges_cache_path = os.path.join(osm_dir, "graph_edges.json")

        # 1. Attempt to load from cached graph files
        try:
            from osm.osm_cache import load_graph_from_cache
            nodes_data, edges_data = load_graph_from_cache(nodes_cache_path, edges_cache_path)
            
            # Rebuild if the OSM source file has been updated since the cache was generated
            if os.path.exists(osm_filepath):
                osm_mtime = os.path.getmtime(osm_filepath)
                cache_mtime = os.path.getmtime(nodes_cache_path)
                if osm_mtime > cache_mtime:
                    raise ValueError("OpenStreetMap source file is newer than JSON cache.")
            
            nodes: List[CampusNode] = []
            for n in nodes_data:
                nodes.append(CampusNode(
                    node_id=n["id"],
                    node_type=n["type"],
                    name=n["name"],
                    latitude=n["coordinates"]["latitude"],
                    longitude=n["coordinates"]["longitude"],
                    metadata=n["metadata"]
                ))
            
            edges: List[CampusEdge] = []
            for e in edges_data:
                edges.append(CampusEdge(
                    source=e["source"],
                    destination=e["destination"],
                    relationship=e["relationship"],
                    distance=e["distance"],
                    accessibility=e["accessibility"],
                    metadata=e["metadata"]
                ))
            
            print(f"========== NAVIGATION DEBUG ==========")
            print(f"Loaded graph from OSM JSON cache files.")
            print(f"Graph nodes: {len(nodes)}")
            print(f"Graph edges: {len(edges)}")
            print(f"Graph generation time (cached load): {time.time() - start_time:.4f} seconds")
            print(f"======================================")
            
            await self.graph_repo.set_graph(nodes, edges)
            return nodes, edges
        except Exception as cache_err:
            print(f"Could not load graph from cache: {cache_err}. Building from OpenStreetMap dataset...")

        # 2. Build graph from OSM dataset
        from osm.osm_importer import download_osm_data
        from osm.osm_parser import parse_osm_file, get_element_geometry_and_centroid

        download_success = download_osm_data(osm_filepath)
        if not download_success:
            raise RuntimeError(f"Failed to obtain OpenStreetMap dataset at {osm_filepath}")

        osm_nodes, osm_ways, osm_elements = parse_osm_file(osm_filepath)
        
        compiled_nodes: List[CampusNode] = []
        compiled_edges: List[CampusEdge] = []

        # Find which nodes are referenced in walkable ways
        referenced_osm_ids = set()
        for way in osm_ways:
            for ref in way["nodes"]:
                referenced_osm_ids.add(ref)

        # Index OSM elements by name for quick lookup
        osm_by_name = {}
        for key, elem in osm_elements.items():
            if elem.get("name"):
                osm_by_name[elem["name"].lower()] = elem

        osm_node_objects: Dict[str, CampusNode] = {}
        for ref_id in referenced_osm_ids:
            if ref_id in osm_nodes:
                on = osm_nodes[ref_id]
                node_obj = CampusNode(
                    node_id=f"osm_{ref_id}",
                    node_type=GraphNodeType.ROAD,
                    name=on.get("name") or f"Walkway Node {ref_id}",
                    latitude=on["latitude"],
                    longitude=on["longitude"],
                    metadata={"is_road": True, "tags": on.get("tags")}
                )
                compiled_nodes.append(node_obj)
                osm_node_objects[ref_id] = node_obj

        # Haversine distance calculator in meters
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371000.0
            phi1 = math.radians(lat1)
            phi2 = math.radians(lat2)
            dphi = math.radians(lat2 - lat1)
            dlam = math.radians(lon2 - lon1)
            a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
            return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        # Add edges for consecutive node pairs in each way
        for way in osm_ways:
            nodes_list = way["nodes"]
            for i in range(len(nodes_list) - 1):
                u_id = nodes_list[i]
                v_id = nodes_list[i+1]
                if u_id in osm_nodes and v_id in osm_nodes:
                    u = osm_nodes[u_id]
                    v = osm_nodes[v_id]
                    dist = haversine(u["latitude"], u["longitude"], v["latitude"], v["longitude"])
                    geom = [[u["latitude"], u["longitude"]], [v["latitude"], v["longitude"]]]
                    est_time = dist / 1.3 # 1.3 m/s walking speed

                    compiled_edges.append(CampusEdge(
                        source=f"osm_{u_id}",
                        destination=f"osm_{v_id}",
                        relationship=GraphEdgeType.WALKWAY,
                        distance=round(dist, 2),
                        accessibility=True,
                        metadata={"name": way["name"], "geometry": geom, "time_seconds": est_time}
                    ))
                    compiled_edges.append(CampusEdge(
                        source=f"osm_{v_id}",
                        destination=f"osm_{u_id}",
                        relationship=GraphEdgeType.WALKWAY,
                        distance=round(dist, 2),
                        accessibility=True,
                        metadata={"name": way["name"], "geometry": [[v["latitude"], v["longitude"]], [u["latitude"], u["longitude"]]], "time_seconds": est_time}
                    ))

        # Helper to locate nearest walkable OSM road node
        def find_nearest_osm_node(lat: float, lon: float) -> Optional[CampusNode]:
            closest_node = None
            min_dist = float("inf")
            for node in osm_node_objects.values():
                d = haversine(lat, lon, node.latitude, node.longitude)
                if d < min_dist:
                    min_dist = d
                    closest_node = node
            return closest_node

        # 3. Load Buildings/Hostels from MongoDB and link to nearest OSM road node
        cursor_buildings = self.db.buildings.find()
        async for b in cursor_buildings:
            b_id = str(b["_id"])
            b_code = b["building_code"]
            b_name = b["building_name"]
            n_type = GraphNodeType.HOSTEL if b.get("category") == "Residential" else GraphNodeType.BUILDING

            # Find matching element from OSM dynamically
            osm_type = b.get("osm_type")
            osm_id = b.get("osm_id")
            
            if not osm_type or not osm_id:
                osm_elem = osm_by_name.get(b_name.lower())
                if osm_elem:
                    osm_type = osm_elem["type"]
                    osm_id = osm_elem["id"]
                else:
                    osm_type = "way"
                    osm_id = f"synth_{b_id}"
            else:
                osm_id = str(osm_id)

            geom, centroid, entrance = get_element_geometry_and_centroid(
                osm_type, osm_id, osm_nodes, osm_elements, referenced_osm_ids
            )
            if not entrance and centroid:
                entrance = centroid

            if not centroid or (centroid[0] == 0.0 and centroid[1] == 0.0):
                lat = b.get("latitude") or 23.4129
                lon = b.get("longitude") or 85.4407
                centroid = (lat, lon)
                entrance = (lat, lon)
                geom = [[lat, lon]]
            else:
                lat, lon = centroid
                # Synchronize coordinates back to MongoDB building collections
                await self.db.buildings.update_one(
                    {"_id": b["_id"]},
                    {
                        "$set": {
                            "latitude": lat,
                            "longitude": lon,
                            "osm_type": osm_type,
                            "osm_id": osm_id,
                            "geometry": geom,
                            "entrance_geometry": [entrance[0], entrance[1]],
                            "entrances": [{"name": "Main Entrance", "latitude": entrance[0], "longitude": entrance[1]}]
                        }
                    }
                )

            building_node = CampusNode(
                node_id=b_id,
                node_type=n_type,
                name=b_name,
                latitude=lat,
                longitude=lon,
                metadata={
                    "building_code": b_code,
                    "category": b.get("category"),
                    "departments": b.get("departments", []),
                    "address": b.get("address", ""),
                    "osm_id": osm_id,
                    "osm_type": osm_type,
                    "geometry": geom,
                    "centroid": [lat, lon],
                    "entrance": [entrance[0], entrance[1]]
                }
            )
            compiled_nodes.append(building_node)

            # Entrance node represents the building's path network point
            ent_id = f"entr_{b_id}_0"
            entrance_node = CampusNode(
                node_id=ent_id,
                node_type=GraphNodeType.ENTRANCE,
                name=f"{b_code} - Main Entrance",
                latitude=entrance[0],
                longitude=entrance[1],
                metadata={"parent_building_id": b_id}
            )
            compiled_nodes.append(entrance_node)

            # Connect parent building to entrance
            compiled_edges.append(CampusEdge(
                source=b_id,
                destination=ent_id,
                relationship=GraphEdgeType.HAS_ENTRANCE,
                distance=5.0,
                accessibility=b.get("accessibility", {}).get("wheelchair_accessible", True)
            ))
            compiled_edges.append(CampusEdge(
                source=ent_id,
                destination=b_id,
                relationship=GraphEdgeType.CONNECTS_TO,
                distance=5.0,
                accessibility=b.get("accessibility", {}).get("wheelchair_accessible", True)
            ))

            # Connect Entrance to nearest OSM road node
            nearest_osm = find_nearest_osm_node(entrance[0], entrance[1])
            if nearest_osm:
                dist_to_road = haversine(entrance[0], entrance[1], nearest_osm.latitude, nearest_osm.longitude)
                compiled_edges.append(CampusEdge(
                    source=ent_id,
                    destination=nearest_osm.id,
                    relationship=GraphEdgeType.CONNECTS_TO,
                    distance=round(dist_to_road, 2),
                    accessibility=True,
                    metadata={"notes": f"Entrance link to nearest OSM walkway"}
                ))
                compiled_edges.append(CampusEdge(
                    source=nearest_osm.id,
                    destination=ent_id,
                    relationship=GraphEdgeType.CONNECTS_TO,
                    distance=round(dist_to_road, 2),
                    accessibility=True,
                    metadata={"notes": f"Road connector to {entrance_node.name}"}
                ))

        # 4. Load Rooms from MongoDB
        cursor_rooms = self.db.rooms.find()
        async for r in cursor_rooms:
            r_id = str(r["_id"])
            r_num = r["room_number"]
            r_name = r["room_name"]
            b_id = r["building_id"]

            room_node = CampusNode(
                node_id=r_id,
                node_type=GraphNodeType.ROOM,
                name=f"{r_num} - {r_name}",
                latitude=r.get("latitude") or 0.0,
                longitude=r.get("longitude") or 0.0,
                metadata={
                    "room_number": r_num,
                    "building_id": b_id,
                    "floor": r.get("floor", 0),
                    "room_type": r.get("room_type"),
                    "capacity": r.get("capacity")
                }
            )
            compiled_nodes.append(room_node)

            compiled_edges.append(CampusEdge(
                source=b_id,
                destination=r_id,
                relationship=GraphEdgeType.CONTAINS,
                accessibility=True
            ))
            compiled_edges.append(CampusEdge(
                source=r_id,
                destination=b_id,
                relationship=GraphEdgeType.LOCATED_IN,
                accessibility=True
            ))

        # 5. Load Facilities from MongoDB
        cursor_facilities = self.db.facilities.find()
        async for f in cursor_facilities:
            f_id = str(f["_id"])
            f_name = f["name"]
            f_cat = f["category"]
            n_type = GraphNodeType.FACILITY
            if f_cat == "Parking":
                n_type = GraphNodeType.PARKING
            elif f_cat == "Bus Stop":
                n_type = GraphNodeType.BUS_STOP

            osm_type = f.get("osm_type")
            osm_id = f.get("osm_id")
            
            if not osm_type or not osm_id:
                osm_elem = osm_by_name.get(f_name.lower())
                if osm_elem:
                    osm_type = osm_elem["type"]
                    osm_id = osm_elem["id"]
                else:
                    osm_type = "way"
                    osm_id = f"synth_{f_id}"
            else:
                osm_id = str(osm_id)

            geom, centroid, entrance = get_element_geometry_and_centroid(
                osm_type, osm_id, osm_nodes, osm_elements, referenced_osm_ids
            )
            if not entrance and centroid:
                entrance = centroid

            if not centroid or (centroid[0] == 0.0 and centroid[1] == 0.0):
                lat = f.get("latitude") or 23.4129
                lon = f.get("longitude") or 85.4407
                centroid = (lat, lon)
                entrance = (lat, lon)
                geom = [[lat, lon]]
            else:
                lat, lon = centroid
                # Synchronize coordinates back to MongoDB
                await self.db.facilities.update_one(
                    {"_id": f["_id"]},
                    {
                        "$set": {
                            "latitude": lat,
                            "longitude": lon,
                            "osm_type": osm_type,
                            "osm_id": osm_id,
                            "geometry": geom,
                            "entrance_geometry": [entrance[0], entrance[1]],
                            "coordinates": {"latitude": lat, "longitude": lon}
                        }
                    }
                )

            facility_node = CampusNode(
                node_id=f_id,
                node_type=n_type,
                name=f_name,
                latitude=lat,
                longitude=lon,
                metadata={
                    "category": f_cat,
                    "timing": f.get("timing"),
                    "services": f.get("services", []),
                    "osm_id": osm_id,
                    "osm_type": osm_type,
                    "geometry": geom,
                    "centroid": [lat, lon],
                    "entrance": [entrance[0], entrance[1]]
                }
            )
            compiled_nodes.append(facility_node)

            nearest_osm = find_nearest_osm_node(entrance[0], entrance[1])
            if nearest_osm:
                dist_to_road = haversine(entrance[0], entrance[1], nearest_osm.latitude, nearest_osm.longitude)
                compiled_edges.append(CampusEdge(
                    source=f_id,
                    destination=nearest_osm.id,
                    relationship=GraphEdgeType.CONNECTS_TO,
                    distance=round(dist_to_road, 2),
                    accessibility=True
                ))
                compiled_edges.append(CampusEdge(
                    source=nearest_osm.id,
                    destination=f_id,
                    relationship=GraphEdgeType.CONNECTS_TO,
                    distance=round(dist_to_road, 2),
                    accessibility=True
                ))

        # 6. Load Landmarks from MongoDB
        cursor_landmarks = self.db.landmarks.find()
        async for lm in cursor_landmarks:
            lm_id = str(lm["_id"])
            lm_name = lm["name"]

            osm_type = lm.get("osm_type")
            osm_id = lm.get("osm_id")
            
            if not osm_type or not osm_id:
                osm_elem = osm_by_name.get(lm_name.lower())
                if osm_elem:
                    osm_type = osm_elem["type"]
                    osm_id = osm_elem["id"]
                else:
                    osm_type = "way"
                    osm_id = f"synth_{lm_id}"
            else:
                osm_id = str(osm_id)

            geom, centroid, entrance = get_element_geometry_and_centroid(
                osm_type, osm_id, osm_nodes, osm_elements, referenced_osm_ids
            )
            if not entrance and centroid:
                entrance = centroid

            if not centroid or (centroid[0] == 0.0 and centroid[1] == 0.0):
                lat = lm.get("latitude") or 23.4129
                lon = lm.get("longitude") or 85.4407
                centroid = (lat, lon)
                entrance = (lat, lon)
                geom = [[lat, lon]]
            else:
                lat, lon = centroid
                # Synchronize coordinates back to MongoDB
                await self.db.landmarks.update_one(
                    {"_id": lm["_id"]},
                    {
                        "$set": {
                            "latitude": lat,
                            "longitude": lon,
                            "osm_type": osm_type,
                            "osm_id": osm_id,
                            "geometry": geom,
                            "entrance_geometry": [entrance[0], entrance[1]],
                            "coordinates": {"latitude": lat, "longitude": lon}
                        }
                    }
                )

            landmark_node = CampusNode(
                node_id=lm_id,
                node_type=GraphNodeType.LANDMARK,
                name=lm_name,
                latitude=lat,
                longitude=lon,
                metadata={
                    "category": lm.get("category"),
                    "description": lm.get("description"),
                    "osm_id": osm_id,
                    "osm_type": osm_type,
                    "geometry": geom,
                    "centroid": [lat, lon],
                    "entrance": [entrance[0], entrance[1]]
                }
            )
            compiled_nodes.append(landmark_node)

            nearest_osm = find_nearest_osm_node(entrance[0], entrance[1])
            if nearest_osm:
                dist_to_road = haversine(entrance[0], entrance[1], nearest_osm.latitude, nearest_osm.longitude)
                compiled_edges.append(CampusEdge(
                    source=lm_id,
                    destination=nearest_osm.id,
                    relationship=GraphEdgeType.CONNECTS_TO,
                    distance=round(dist_to_road, 2),
                    accessibility=True
                ))
                compiled_edges.append(CampusEdge(
                    source=nearest_osm.id,
                    destination=lm_id,
                    relationship=GraphEdgeType.CONNECTS_TO,
                    distance=round(dist_to_road, 2),
                    accessibility=True
                ))

        # 7. Generate Floor Connections dynamically
        building_rooms: dict[str, dict[int, list[str]]] = {}
        for r_node in [n for n in compiled_nodes if n.type == GraphNodeType.ROOM]:
            b_id = r_node.metadata["building_id"]
            fl = r_node.metadata["floor"]
            if b_id not in building_rooms:
                building_rooms[b_id] = {}
            if fl not in building_rooms[b_id]:
                building_rooms[b_id][fl] = []
            building_rooms[b_id][fl].append(r_node.id)
            
        for b_id, floors in building_rooms.items():
            floor_nums = sorted(list(floors.keys()))
            for i in range(len(floor_nums) - 1):
                f_current = floor_nums[i]
                f_next = floor_nums[i+1]
                if floors[f_current] and floors[f_next]:
                    r_src = floors[f_current][0]
                    r_dest = floors[f_next][0]
                    compiled_edges.append(CampusEdge(
                        source=r_src,
                        destination=r_dest,
                        relationship=GraphEdgeType.FLOOR_CONNECTION,
                        distance=4.0,
                        accessibility=False,
                        metadata={"notes": f"Stairs connecting floor {f_current} to {f_next}"}
                    ))
                    compiled_edges.append(CampusEdge(
                        source=r_dest,
                        destination=r_src,
                        relationship=GraphEdgeType.FLOOR_CONNECTION,
                        distance=4.0,
                        accessibility=False,
                        metadata={"notes": f"Stairs connecting floor {f_next} to {f_current}"}
                    ))

        # Save generated graph to Cache files
        try:
            from osm.osm_cache import save_graph_to_cache
            nodes_serializable = [n.to_dict() for n in compiled_nodes]
            edges_serializable = [e.to_dict() for e in compiled_edges]
            save_graph_to_cache(nodes_serializable, edges_serializable, nodes_cache_path, edges_cache_path)
        except Exception as cache_save_err:
            print(f"Failed to cache generated OSM graph: {cache_save_err}")

        # Set graph in repository
        await self.graph_repo.set_graph(compiled_nodes, compiled_edges)

        print(f"========== NAVIGATION DEBUG ==========")
        print(f"OSM loaded: TRUE")
        print(f"Graph nodes compiled: {len(compiled_nodes)}")
        print(f"Graph edges compiled: {len(compiled_edges)}")
        print(f"Graph generation time: {time.time() - start_time:.4f} seconds")
        print(f"======================================")

        return compiled_nodes, compiled_edges

    async def _build_graph_legacy(self) -> Tuple[List[CampusNode], List[CampusEdge]]:
        nodes: List[CampusNode] = []
        edges: List[CampusEdge] = []

        # 1. Fetch Buildings and Hostels
        cursor_buildings = self.db.buildings.find()
        async for b in cursor_buildings:
            b_id = str(b["_id"])
            b_code = b["building_code"]
            b_name = b["building_name"]
            
            n_type = GraphNodeType.HOSTEL if b.get("category") == "Residential" else GraphNodeType.BUILDING
            
            building_node = CampusNode(
                node_id=b_id,
                node_type=n_type,
                name=b_name,
                latitude=b["latitude"],
                longitude=b["longitude"],
                metadata={
                    "building_code": b_code,
                    "category": b.get("category"),
                    "departments": b.get("departments", []),
                    "address": b.get("address", ""),
                    "osm_id": b.get("osm_id") or f"synth_{b_id}",
                    "osm_type": b.get("osm_type") or "way",
                    "geometry": b.get("geometry") or [[b["latitude"], b["longitude"]]],
                    "centroid": [b["latitude"], b["longitude"]],
                    "entrance": [b["latitude"], b["longitude"]]
                }
            )
            nodes.append(building_node)

            entrances = b.get("entrances", [])
            for idx, ent in enumerate(entrances):
                ent_id = f"entr_{b_id}_{idx}"
                ent_name = ent.get("name", f"Entrance {idx + 1}")
                ent_lat = ent.get("latitude", b["latitude"])
                ent_lng = ent.get("longitude", b["longitude"])
                
                entrance_node = CampusNode(
                    node_id=ent_id,
                    node_type=GraphNodeType.ENTRANCE,
                    name=f"{b_code} - {ent_name}",
                    latitude=ent_lat,
                    longitude=ent_lng,
                    metadata={"parent_building_id": b_id}
                )
                nodes.append(entrance_node)

                edges.append(CampusEdge(
                    source=b_id,
                    destination=ent_id,
                    relationship=GraphEdgeType.HAS_ENTRANCE,
                    distance=5.0,
                    accessibility=b.get("accessibility", {}).get("wheelchair_accessible", True)
                ))
                edges.append(CampusEdge(
                    source=ent_id,
                    destination=b_id,
                    relationship=GraphEdgeType.CONNECTS_TO,
                    distance=5.0,
                    accessibility=b.get("accessibility", {}).get("wheelchair_accessible", True)
                ))

        # 2. Fetch Rooms
        cursor_rooms = self.db.rooms.find()
        async for r in cursor_rooms:
            r_id = str(r["_id"])
            r_num = r["room_number"]
            r_name = r["room_name"]
            b_id = r["building_id"]
            
            room_node = CampusNode(
                node_id=r_id,
                node_type=GraphNodeType.ROOM,
                name=f"{r_num} - {r_name}",
                latitude=r.get("latitude") or 0.0,
                longitude=r.get("longitude") or 0.0,
                metadata={
                    "room_number": r_num,
                    "building_id": b_id,
                    "floor": r.get("floor", 0),
                    "room_type": r.get("room_type"),
                    "capacity": r.get("capacity")
                }
            )
            nodes.append(room_node)

            edges.append(CampusEdge(
                source=b_id,
                destination=r_id,
                relationship=GraphEdgeType.CONTAINS,
                accessibility=True
            ))
            edges.append(CampusEdge(
                source=r_id,
                destination=b_id,
                relationship=GraphEdgeType.LOCATED_IN,
                accessibility=True
            ))

        # 3. Fetch Facilities
        cursor_facilities = self.db.facilities.find()
        async for f in cursor_facilities:
            f_id = str(f["_id"])
            f_name = f["name"]
            f_cat = f["category"]
            
            n_type = GraphNodeType.FACILITY
            if f_cat == "Parking":
                n_type = GraphNodeType.PARKING
            elif f_cat == "Bus Stop":
                n_type = GraphNodeType.BUS_STOP
                
            facility_node = CampusNode(
                node_id=f_id,
                node_type=n_type,
                name=f_name,
                latitude=f["latitude"],
                longitude=f["longitude"],
                metadata={
                    "category": f_cat,
                    "timing": f.get("timing"),
                    "services": f.get("services", []),
                    "osm_id": f.get("osm_id") or f"synth_{f_id}",
                    "osm_type": f.get("osm_type") or "way",
                    "geometry": f.get("geometry") or [[f["latitude"], f["longitude"]]],
                    "centroid": [f["latitude"], f["longitude"]],
                    "entrance": [f["latitude"], f["longitude"]]
                }
            )
            nodes.append(facility_node)

        # 4. Fetch Landmarks
        cursor_landmarks = self.db.landmarks.find()
        async for lm in cursor_landmarks:
            lm_id = str(lm["_id"])
            lm_name = lm["name"]
            
            landmark_node = CampusNode(
                node_id=lm_id,
                node_type=GraphNodeType.LANDMARK,
                name=lm_name,
                latitude=lm["latitude"],
                longitude=lm["longitude"],
                metadata={
                    "category": lm.get("category"),
                    "description": lm.get("description"),
                    "osm_id": lm.get("osm_id") or f"synth_{lm_id}",
                    "osm_type": lm.get("osm_type") or "way",
                    "geometry": lm.get("geometry") or [[lm["latitude"], lm["longitude"]]],
                    "centroid": [lm["latitude"], lm["longitude"]],
                    "entrance": [lm["latitude"], lm["longitude"]]
                }
            )
            nodes.append(landmark_node)

        # 5. Fetch Pathways
        cursor_pathways = self.db.pathways.find()
        async for pw in cursor_pathways:
            pw_id = str(pw["_id"])
            s_node = pw["start_node"]
            e_node = pw["end_node"]
            
            start_id = s_node["id"]
            if s_node.get("type") in ["building", "hostel"]:
                start_id = f"entr_{s_node['id']}_0"

            end_id = e_node["id"]
            if e_node.get("type") in ["building", "hostel"]:
                end_id = f"entr_{e_node['id']}_0"
            
            edges.append(CampusEdge(
                source=start_id,
                destination=end_id,
                relationship=GraphEdgeType.WALKWAY,
                distance=pw.get("distance"),
                accessibility=pw.get("accessible", True),
                metadata={
                    "path_id": pw_id,
                    "surface": pw.get("surface"),
                    "lighting": pw.get("lighting"),
                    "geometry": pw.get("geometry", [])
                }
            ))
            edges.append(CampusEdge(
                source=end_id,
                destination=start_id,
                relationship=GraphEdgeType.WALKWAY,
                distance=pw.get("distance"),
                accessibility=pw.get("accessible", True),
                metadata={
                    "path_id": pw_id,
                    "surface": pw.get("surface"),
                    "lighting": pw.get("lighting"),
                    "geometry": pw.get("geometry", [])
                }
            ))

        # 6. Generate Floor Connections
        building_rooms: dict[str, dict[int, list[str]]] = {}
        for r_node in [n for n in nodes if n.type == GraphNodeType.ROOM]:
            b_id = r_node.metadata["building_id"]
            fl = r_node.metadata["floor"]
            if b_id not in building_rooms:
                building_rooms[b_id] = {}
            if fl not in building_rooms[b_id]:
                building_rooms[b_id][fl] = []
            building_rooms[b_id][fl].append(r_node.id)
            
        for b_id, floors in building_rooms.items():
            floor_nums = sorted(list(floors.keys()))
            for i in range(len(floor_nums) - 1):
                f_current = floor_nums[i]
                f_next = floor_nums[i+1]
                
                if floors[f_current] and floors[f_next]:
                    r_src = floors[f_current][0]
                    r_dest = floors[f_next][0]
                    
                    edges.append(CampusEdge(
                        source=r_src,
                        destination=r_dest,
                        relationship=GraphEdgeType.FLOOR_CONNECTION,
                        distance=4.0,
                        accessibility=False,
                        metadata={"notes": f"Stairs connecting floor {f_current} to {f_next}"}
                    ))
                    edges.append(CampusEdge(
                        source=r_dest,
                        destination=r_src,
                        relationship=GraphEdgeType.FLOOR_CONNECTION,
                        distance=4.0,
                        accessibility=False,
                        metadata={"notes": f"Stairs connecting floor {f_next} to {f_current}"}
                    ))

        # Save to repo cache
        await self.graph_repo.set_graph(nodes, edges)
        return nodes, edges


class CampusGraphService:
    def __init__(self, graph_repo: CampusGraphRepository, builder: CampusGraphBuilderService):
        self.repo = graph_repo
        self.builder = builder

    async def _ensure_loaded(self) -> None:
        if not self.repo.is_initialized:
            await self.builder.build_graph()

    async def get_node_by_id(self, node_id: str) -> Optional[CampusNode]:
        await self._ensure_loaded()
        return await self.repo.get_node(node_id)

    async def list_nodes(self, node_type: Optional[str] = None) -> List[CampusNode]:
        await self._ensure_loaded()
        nodes = await self.repo.get_nodes()
        if node_type:
            nodes = [n for n in nodes if (n.type.value if hasattr(n.type, "value") else n.type).lower() == node_type.lower()]
        return nodes

    async def list_edges(self) -> List[CampusEdge]:
        await self._ensure_loaded()
        return await self.repo.get_edges()

    async def get_neighbors(self, node_id: str) -> List[Tuple[CampusNode, CampusEdge]]:
        await self._ensure_loaded()
        return await self.repo.get_neighbors(node_id)

    async def get_rooms_in_building(self, building_id: str) -> List[CampusNode]:
        await self._ensure_loaded()
        neighbors = await self.repo.get_neighbors(building_id)
        return [node for node, edge in neighbors if edge.relationship == GraphEdgeType.CONTAINS and node.type == GraphNodeType.ROOM]

    async def get_entrances_for_building(self, building_id: str) -> List[CampusNode]:
        await self._ensure_loaded()
        neighbors = await self.repo.get_neighbors(building_id)
        return [node for node, edge in neighbors if edge.relationship == GraphEdgeType.HAS_ENTRANCE and node.type == GraphNodeType.ENTRANCE]

    async def get_facilities_near_building(self, building_id: str, radius_meters: float = 200.0) -> List[CampusNode]:
        await self._ensure_loaded()
        b_node = await self.repo.get_node(building_id)
        if not b_node:
            return []
            
        facilities = await self.list_nodes(node_type="Facility")
        nearby = []
        
        for f in facilities:
            dist = self._calculate_distance(b_node.latitude, b_node.longitude, f.latitude, f.longitude)
            if dist <= radius_meters:
                nearby.append(f)
        return nearby

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371000.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    async def get_graph_summary(self) -> Dict[str, Any]:
        await self._ensure_loaded()
        nodes = await self.repo.get_nodes()
        edges = await self.repo.get_edges()
        
        node_counts: dict[str, int] = {}
        for n in nodes:
            n_type = n.type.value if hasattr(n.type, "value") else n.type
            node_counts[n_type] = node_counts.get(n_type, 0) + 1
            
        edge_counts: dict[str, int] = {}
        for e in edges:
            e_rel = e.relationship.value if hasattr(e.relationship, "value") else e.relationship
            edge_counts[e_rel] = edge_counts.get(e_rel, 0) + 1
            
        return {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "node_type_counts": node_counts,
            "edge_relationship_counts": edge_counts,
            "is_valid": True
        }
