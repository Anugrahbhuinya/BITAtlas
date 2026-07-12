# backend/osm/osm_cache.py

import os
import json
from typing import Dict, List, Tuple, Any

def save_graph_to_cache(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]], nodes_path: str, edges_path: str):
    """
    Saves the processed graph nodes and edges list to JSON cache files.
    """
    os.makedirs(os.path.dirname(nodes_path), exist_ok=True)
    os.makedirs(os.path.dirname(edges_path), exist_ok=True)

    with open(nodes_path, "w", encoding="utf-8") as f:
        json.dump(nodes, f, indent=2, ensure_ascii=False)

    with open(edges_path, "w", encoding="utf-8") as f:
        json.dump(edges, f, indent=2, ensure_ascii=False)
    print(f"Graph nodes and edges successfully cached to {nodes_path} and {edges_path}")

def load_graph_from_cache(nodes_path: str, edges_path: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Loads graph nodes and edges list from the JSON cache files.
    """
    if not os.path.exists(nodes_path) or not os.path.exists(edges_path):
        raise FileNotFoundError("Graph cache files not found.")

    with open(nodes_path, "r", encoding="utf-8") as f:
        nodes = json.load(f)

    with open(edges_path, "r", encoding="utf-8") as f:
        edges = json.load(f)

    return nodes, edges
