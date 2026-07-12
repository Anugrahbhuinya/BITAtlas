# backend/app/navigation/graph/repositories.py

import asyncio
from typing import Dict, List, Optional, Tuple
from app.navigation.graph.models import CampusNode, CampusEdge

class CampusGraphRepository:
    def __init__(self):
        # In-memory indices
        self._nodes: Dict[str, CampusNode] = {}
        self._edges: List[CampusEdge] = []
        
        # Adjacency maps for fast traversals: NodeId -> List of edges starting from NodeId
        self._adjacency: Dict[str, List[CampusEdge]] = {}
        # Inward adjacency map for reverse traversal: NodeId -> List of edges ending at NodeId
        self._inward_adjacency: Dict[str, List[CampusEdge]] = {}
        
        self._lock = asyncio.Lock()
        self._initialized = False

    async def clear(self) -> None:
        async with self._lock:
            self._nodes.clear()
            self._edges.clear()
            self._adjacency.clear()
            self._inward_adjacency.clear()
            self._initialized = False

    async def set_graph(self, nodes: List[CampusNode], edges: List[CampusEdge]) -> None:
        async with self._lock:
            self._nodes = {node.id: node for node in nodes}
            self._edges = list(edges)
            
            # Rebuild adjacency maps
            self._adjacency = {node.id: [] for node in nodes}
            self._inward_adjacency = {node.id: [] for node in nodes}
            
            for edge in edges:
                if edge.source in self._adjacency:
                    self._adjacency[edge.source].append(edge)
                if edge.destination in self._inward_adjacency:
                    self._inward_adjacency[edge.destination].append(edge)
                    
            self._initialized = True

    async def get_node(self, node_id: str) -> Optional[CampusNode]:
        return self._nodes.get(node_id)

    async def get_nodes(self) -> List[CampusNode]:
        return list(self._nodes.values())

    async def get_edges(self) -> List[CampusEdge]:
        return list(self._edges)

    async def get_neighbors(self, node_id: str) -> List[Tuple[CampusNode, CampusEdge]]:
        # Returns tuples of (NeighborNode, ConnectingEdge)
        edges = self._adjacency.get(node_id, [])
        results = []
        for edge in edges:
            dest_node = self._nodes.get(edge.destination)
            if dest_node:
                results.append((dest_node, edge))
        return results

    async def get_inward_neighbors(self, node_id: str) -> List[Tuple[CampusNode, CampusEdge]]:
        edges = self._inward_adjacency.get(node_id, [])
        results = []
        for edge in edges:
            src_node = self._nodes.get(edge.source)
            if src_node:
                results.append((src_node, edge))
        return results

    @property
    def is_initialized(self) -> bool:
        return self._initialized

# Global Singleton Repository Instance
_global_graph_repository = CampusGraphRepository()

def get_graph_repository() -> CampusGraphRepository:
    return _global_graph_repository
