# backend/app/navigation/graph/utils.py

from typing import List, Dict, Any, Set
from app.navigation.graph.models import CampusNode, CampusEdge, GraphNodeType, GraphEdgeType
from app.navigation.graph.repositories import CampusGraphRepository

class CampusGraphValidator:
    def __init__(self, graph_repo: CampusGraphRepository):
        self.repo = graph_repo

    async def validate_graph(self) -> Dict[str, Any]:
        nodes = await self.repo.get_nodes()
        edges = await self.repo.get_edges()
        
        node_ids = {n.id for n in nodes}
        errors = []
        
        # 1. Check for Duplicate Nodes (handled partially by dict mapping, but let's check input list counts)
        # Check duplicate IDs
        seen_nodes = set()
        for n in nodes:
            if n.id in seen_nodes:
                errors.append({
                    "type": "duplicate_node",
                    "message": f"Duplicate node ID found: '{n.id}' ({n.name})",
                    "severity": "ERROR",
                    "details": {"node_id": n.id}
                })
            seen_nodes.add(n.id)

        # 2. Check for Invalid References (edges pointing to non-existent nodes)
        for e in edges:
            if e.source not in node_ids:
                errors.append({
                    "type": "invalid_reference",
                    "message": f"Edge references missing source node: '{e.source}' to '{e.destination}'",
                    "severity": "ERROR",
                    "details": {"source": e.source, "destination": e.destination, "relationship": e.relationship}
                })
            if e.destination not in node_ids:
                errors.append({
                    "type": "invalid_reference",
                    "message": f"Edge references missing destination node: '{e.destination}' from '{e.source}'",
                    "severity": "ERROR",
                    "details": {"source": e.source, "destination": e.destination, "relationship": e.relationship}
                })

        # 3. Check for Duplicate Edges (same source, destination, and relationship type)
        seen_edges = set()
        for e in edges:
            edge_key = (e.source, e.destination, e.relationship)
            if edge_key in seen_edges:
                errors.append({
                    "type": "duplicate_edge",
                    "message": f"Duplicate edge relationship found: '{e.source}' -[{e.relationship}]-> '{e.destination}'",
                    "severity": "WARNING",
                    "details": {"source": e.source, "destination": e.destination, "relationship": e.relationship}
                })
            seen_edges.add(edge_key)

        # 4. Check for Orphan Nodes (nodes with no incoming or outgoing edges)
        connected_nodes = set()
        for e in edges:
            connected_nodes.add(e.source)
            connected_nodes.add(e.destination)
            
        for n in nodes:
            if n.id not in connected_nodes:
                errors.append({
                    "type": "orphan",
                    "message": f"Orphan node detected with zero connections: '{n.name}' ({n.id})",
                    "severity": "WARNING",
                    "details": {"node_id": n.id, "node_type": n.type}
                })

        # 5. Check for Circular Containment (e.g. A contains B, B contains A)
        contains_edges = [e for e in edges if e.relationship == GraphEdgeType.CONTAINS]
        contains_adjacency: Dict[str, Set[str]] = {}
        for e in contains_edges:
            if e.source not in contains_adjacency:
                contains_adjacency[e.source] = set()
            contains_adjacency[e.source].add(e.destination)
            
        # Recursive DFS to find cycles in containment
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs_cycle(v: str, path: List[str]):
            visited.add(v)
            rec_stack.add(v)
            path.append(v)
            
            neighbors = contains_adjacency.get(v, set())
            for neighbor in neighbors:
                if neighbor not in visited:
                    if dfs_cycle(neighbor, path):
                        return True
                elif neighbor in rec_stack:
                    cycle_start_idx = path.index(neighbor)
                    cycle_path = path[cycle_start_idx:] + [neighbor]
                    cycles.append(cycle_path)
                    return True
                    
            rec_stack.remove(v)
            path.pop()
            return False

        for n_id in contains_adjacency:
            if n_id not in visited:
                dfs_cycle(n_id, [])
                
        for cyc in cycles:
            errors.append({
                "type": "circle",
                "message": f"Circular containment cycle detected: {' -> '.join(cyc)}",
                "severity": "ERROR",
                "details": {"cycle": cyc}
            })

        # 6. Check for Invalid Room assignments (rooms referencing non-existent parent buildings)
        for n in nodes:
            if n.type == GraphNodeType.ROOM:
                b_id = n.metadata.get("building_id")
                if not b_id or b_id not in node_ids:
                    errors.append({
                        "type": "invalid_room_assignment",
                        "message": f"Room '{n.name}' ({n.id}) references missing building parent ID '{b_id}'",
                        "severity": "ERROR",
                        "details": {"room_id": n.id, "building_id": b_id}
                    })

        total_errors = sum(1 for e in errors if e["severity"] == "ERROR")
        total_warnings = sum(1 for e in errors if e["severity"] == "WARNING")
        
        return {
            "is_valid": total_errors == 0,
            "errors": errors,
            "total_errors": total_errors,
            "total_warnings": total_warnings
        }
