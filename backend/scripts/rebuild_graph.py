# backend/scripts/rebuild_graph.py

import os
import sys
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.core import config
from app.navigation.graph.services import CampusGraphBuilderService
from app.navigation.graph.repositories import CampusGraphRepository

async def run_rebuild():
    client = AsyncIOMotorClient(config.MONGO_URI)
    db = client[config.MONGO_DB]
    
    # Instantiate repository
    repo = CampusGraphRepository()
    # Instantiate builder
    builder = CampusGraphBuilderService(db, repo)
    
    print("Starting graph build reconstruction...")
    nodes, edges = await builder.build_graph()
    
    # Re-cache the generated graph data so the frontend can load it fast next time
    osm_dir = os.path.join(os.path.dirname(BACKEND_DIR), "data", "osm")
    nodes_cache_path = os.path.join(osm_dir, "graph_nodes.json")
    edges_cache_path = os.path.join(osm_dir, "graph_edges.json")
    
    import json
    
    nodes_data = [n.to_dict() for n in nodes]
    edges_data = [e.to_dict() for e in edges]
        
    with open(nodes_cache_path, "w", encoding="utf-8") as f:
        json.dump(nodes_data, f, indent=2)
        
    with open(edges_cache_path, "w", encoding="utf-8") as f:
        json.dump(edges_data, f, indent=2)
        
    print(f"Graph rebuild complete. Generated {len(nodes)} nodes and {len(edges)} edges.")
    print(f"Cached data saved to {nodes_cache_path}")

if __name__ == "__main__":
    asyncio.run(run_rebuild())
