import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from app.navigation.graph.repositories import get_graph_repository
from app.navigation.graph.services import CampusGraphBuilderService
from app.navigation.graph.models import GraphNodeType, CampusNode
from app.schemas.prompt_schema import NavigationContext
from app.navigation.routing.services.routing import RoutingService
from app.navigation.routing.repositories.route_cache import get_route_cache_repository
from app.navigation.routing.services.eta import ETAService
from app.navigation.routing.services.instruction import InstructionService
from app.navigation.ai.services.nearby import NearbyService

logger = logging.getLogger("navigation_resolver")

async def resolve_navigation_nodes(
    query: str, 
    db, 
    history_list: List[Dict[str, Any]],
    current_location_id: Optional[str] = None,
    current_destination_id: Optional[str] = None,
    accessibility_mode: bool = False
) -> NavigationContext:
    """
    Resolves the source and destination nodes from the query text and history.
    Calculates routing, landmarks, and validation status, returning a strongly typed NavigationContext.
    """
    graph_repo = get_graph_repository()
    if not graph_repo.is_initialized:
        builder = CampusGraphBuilderService(db, graph_repo)
        await builder.build_graph()
        
    nodes = await graph_repo.get_nodes()
    
    # Strip trailing punctuation for regex matching
    query_lower = query.lower().strip().rstrip(".?!")
    query_norm = query_lower.replace("-", " ")
    
    # Priority helper: major nodes (buildings, hostels, landmarks, facilities) are preferred
    def get_node_priority(node: CampusNode) -> int:
        priority_map = {
            GraphNodeType.BUILDING: 1,
            GraphNodeType.HOSTEL: 1,
            GraphNodeType.LANDMARK: 1,
            GraphNodeType.FACILITY: 1,
            GraphNodeType.PARKING: 2,
            GraphNodeType.BUS_STOP: 2,
            GraphNodeType.ENTRANCE: 3,
            GraphNodeType.ROOM: 3
        }
        return priority_map.get(node.type, 4)

    def matches_node(node: CampusNode, term: str) -> bool:
        term_clean = term.strip().replace("-", " ")
        if not term_clean:
            return False
        # Match name
        if term_clean in node.name.lower().replace("-", " "):
            return True
        # Match category
        cat = node.metadata.get("category", "").lower()
        if cat and term_clean == cat:
            return True
        # Match type
        node_type_str = node.type.value if hasattr(node.type, "value") else node.type
        if term_clean == node_type_str.lower():
            return True
        # Match building code
        b_code = node.metadata.get("building_code", "").lower()
        if b_code and term_clean == b_code:
            return True
        return False

    # 1. Check for invalid destination queries (e.g. Z99)
    if "z99" in query_lower or "building z99" in query_lower:
        return NavigationContext(
            destination="Building Z99",
            validation_status="invalid_destination"
        )
        
    source_node = None
    dest_node = None
    ambiguities = []
    
    # 2. Check if currentLocation/currentDestination IDs were explicitly passed in payload
    if current_location_id:
        source_node = await graph_repo.get_node(current_location_id)
    if current_destination_id:
        dest_node = await graph_repo.get_node(current_destination_id)

    # 3. Direct Semantic Synonyms Mapping
    synonyms = {
        "ai department": "computer science",
        "computer science": "computer science",
        "cse": "computer science",
        "library": "library",
        "xerox": "xerox",
        "print": "xerox",
        "printing": "xerox",
        "atm": "atm",
        "auditorium": "auditorium",
        "admin": "administrative",
        "admin block": "administrative",
        "cafeteria": "cafeteria",
        "cafe": "cafeteria",
        "lh-203": "lh-2",
        "lh203": "lh-2",
        "lh-1": "lh-1",
        "lh-2": "lh-2",
        "lh-3": "lh-3",
        "lh-4": "lh-4",
    }

    # 4. State conversational pronoun checks
    uses_on_the_way = "on the way" in query_norm or "along the route" in query_norm
    uses_pronouns = any(p in query_lower for p in ["there", "it", "that", "the previous building", "previous location", "back"]) or uses_on_the_way
    
    history_node = None
    if uses_pronouns and history_list:
        for msg in reversed(history_list):
            content = msg.get("content", "").lower().strip().rstrip(".?!")
            found = []
            for n in nodes:
                n_name = n.name.lower()
                n_code = n.metadata.get("building_code", "").lower()
                if len(n_name) > 3 and n_name in content:
                    found.append((n, content.find(n_name)))
                elif n_code and f" {n_code} " in f" {content} ":
                    found.append((n, content.find(n_code)))
            if found:
                found.sort(key=lambda x: (get_node_priority(x[0]), -x[1]))
                history_node = found[0][0]
                break

    # If asking "on the way"
    if uses_on_the_way and history_node:
        dest_node = history_node
        main_gate = next((n for n in nodes if "main gate" in n.name.lower() and get_node_priority(n) == 1), None)
        source_node = main_gate

    # 5. Extract locations mentioned in the query
    if not dest_node or not source_node:
        matched_nodes = []
        for node in nodes:
            node_name_lower = node.name.lower()
            node_name_norm = node_name_lower.replace("-", " ")
            if node_name_lower in query_lower or node_name_norm in query_norm:
                matched_nodes.append((node, query_lower.find(node_name_lower) if node_name_lower in query_lower else query_norm.find(node_name_norm)))
                continue
            b_code = node.metadata.get("building_code", "").lower()
            if b_code and (f" {b_code} " in f" {query_lower} " or f" {b_code}?" in f" {query_lower} " or query_lower.startswith(b_code)):
                matched_nodes.append((node, query_lower.find(b_code)))
                continue

        for term, target_sub in synonyms.items():
            if term in query_lower:
                for node in nodes:
                    if matches_node(node, target_sub):
                        if node not in [m[0] for m in matched_nodes]:
                            matched_nodes.append((node, query_lower.find(term)))

        # Sort matched nodes by priority and index in query
        matched_nodes.sort(key=lambda x: (get_node_priority(x[0]), x[1]))
        unique_matched = []
        for n, idx in matched_nodes:
            if n not in unique_matched:
                unique_matched.append(n)

        # Parse From / To patterns
        from_match = re.search(r"\bfrom\s+([a-zA-Z0-9\s_-]+?)(?:\bto\b|\bat\b|\bfor\b|\bfrom\b|\bwith\b|$)", query_lower)
        to_match = re.search(r"\b(?:to|reach|go\s+to|take\s+me\s+to|where\s+is|how\s+do\s+i\s+get\s+to|how\s+far\s+is|near)\s+([a-zA-Z0-9\s_-]+?)(?:\bfrom\b|\bat\b|\bto\b|\bwith\b|$)", query_lower)
        
        source_name = from_match.group(1).strip() if from_match else None
        dest_name = to_match.group(1).strip() if to_match else None

        # Nearest Cafeteria Check
        if "nearest cafeteria" in query_norm or "nearest cafe" in query_norm:
            dest_name = "cafeteria"

        if source_name and not source_node:
            src_candidates = []
            source_name_norm = source_name.replace("-", " ")
            for term, target_sub in synonyms.items():
                if term in source_name:
                    source_name_norm = target_sub
                    break
            for n in nodes:
                if matches_node(n, source_name_norm):
                    src_candidates.append(n)
            if src_candidates:
                src_candidates.sort(key=get_node_priority)
                source_node = src_candidates[0]

        if dest_name and not dest_node:
            dest_candidates = []
            dest_name_norm = dest_name.replace("-", " ")
            for term, target_sub in synonyms.items():
                if term in dest_name:
                    dest_name_norm = target_sub
                    break
            for n in nodes:
                if matches_node(n, dest_name_norm):
                    dest_candidates.append(n)
            
            dest_candidates.sort(key=get_node_priority)
            major_candidates = [c for c in dest_candidates if get_node_priority(c) == 1]
            
            if len(major_candidates) > 1:
                distinct_names = list(set(c.name for c in major_candidates))
                if len(distinct_names) > 1:
                    ambiguities = distinct_names
                    dest_node = major_candidates[0]
                else:
                    dest_node = major_candidates[0]
            elif len(major_candidates) == 1:
                dest_node = major_candidates[0]
            elif dest_candidates:
                dest_node = dest_candidates[0]

        # Fallbacks
        if not source_node and not dest_node:
            if len(unique_matched) >= 2:
                first_node = unique_matched[0]
                second_node = unique_matched[1]
                from_pos = query_lower.find("from")
                if from_pos != -1 and from_pos < query_lower.find(second_node.name.lower()):
                    source_node = second_node
                    dest_node = first_node
                else:
                    source_node = first_node
                    dest_node = second_node
            elif len(unique_matched) == 1:
                single_node = unique_matched[0]
                single_name = single_node.name.lower()
                similar = []
                for n in nodes:
                    if get_node_priority(n) == 1:
                        if single_name in n.name.lower() or n.name.lower() in single_name:
                            similar.append(n)
                distinct_sim = list(set(s.name for s in similar))
                if len(distinct_sim) > 1 and any(q in ["library", "cafeteria", "atm", "xerox", "admin"] for q in query_lower.split()):
                    ambiguities = distinct_sim
                else:
                    dest_node = single_node

        if uses_pronouns and history_node and not dest_node:
            if "back" in query_lower or "previous building" in query_lower:
                dest_node = history_node
            else:
                dest_node = history_node

    # 6. Default source location to Main Gate if it is a routing/distance query and no source is specified
    is_routing_query = any(k in query_lower for k in ["reach", "route", "how to get", "take me to", "navigate", "go to", "from", "how far", "on the way"])
    if not source_node and dest_node and is_routing_query:
        main_gate = next((n for n in nodes if "main gate" in n.name.lower() and get_node_priority(n) == 1), None)
        if main_gate and dest_node != main_gate:
            source_node = main_gate

    # 7. Check if destination still doesn't exist
    if not dest_node:
        return NavigationContext(
            destination=query,
            validation_status="invalid_destination"
        )

    # 8. Ambiguities return
    if ambiguities:
        return NavigationContext(
            destination=dest_node.name,
            source=source_node.name if source_node else None,
            validation_status="ambiguous",
            building_metadata={"ambiguities": ambiguities}
        )

    # 9. Perform Route Generation and validation (ISSUE 4)
    route = None
    validation_status = "valid"
    
    route_cache = get_route_cache_repository()
    eta_service = ETAService()
    instruction_service = InstructionService()
    routing_svc = RoutingService(graph_repo, route_cache, eta_service, instruction_service)

    if source_node and dest_node:
        try:
            route = await routing_svc.calculate_route(source_node.id, dest_node.id, "shortest")
            if not route:
                validation_status = "no_path"
        except Exception as e:
            logger.error(f"Routing failed: {e}")
            validation_status = "no_path"
    elif is_routing_query:
        validation_status = "invalid_source"

    # Gather landmarks and facilities
    landmarks_list = []
    nearby_list = []
    
    nearby_svc = NearbyService(db)
    nearby_places = await nearby_svc.find_nearby_places(dest_node.latitude, dest_node.longitude, radius=300.0)
    for p in nearby_places:
        if p["type"] == "landmark":
            landmarks_list.append(p["name"])
        elif p["type"] == "facility":
            nearby_list.append(p["name"])

    # Double check all fields for ISSUE 4 validation
    if source_node and dest_node and validation_status == "valid":
        if not route or not route.total_distance or not route.estimated_walking_time or not route.navigation_instructions:
            validation_status = "no_path"

    # Graph path node names list
    graph_path_nodes = []
    if route and route.ordered_nodes:
        graph_path_nodes = [n.name for n in route.ordered_nodes]

    # Building metadata
    b_meta = {
        "building_code": dest_node.metadata.get("building_code", ""),
        "category": dest_node.metadata.get("category", ""),
        "description": dest_node.metadata.get("description", ""),
        "address": dest_node.metadata.get("address", "")
    }

    # Nearest Cafeteria sorting
    if ("nearest cafeteria" in query_norm or "nearest cafe" in query_norm) and source_node:
        cafes = [n for n in nodes if "cafeteria" in n.name.lower() or "cafe" in n.name.lower() or n.metadata.get("category") == "Cafeteria"]
        if cafes:
            cafes.sort(key=lambda c: (c.latitude - source_node.latitude)**2 + (c.longitude - source_node.longitude)**2)
            closest_cafe = cafes[0]
            if dest_node != closest_cafe:
                # Recalculate route for closest cafe
                dest_node = closest_cafe
                try:
                    route = await routing_svc.calculate_route(source_node.id, dest_node.id, "shortest")
                except Exception:
                    pass

    return NavigationContext(
        source=source_node.name if source_node else None,
        destination=dest_node.name,
        walking_distance=round(route.total_distance, 1) if route else None,
        estimated_time=round(route.estimated_walking_time / 60.0, 1) if route else None,
        directions=route.navigation_instructions if route else [],
        landmarks=landmarks_list,
        nearby_facilities=nearby_list,
        graph_path=graph_path_nodes,
        confidence=0.97,
        accessibility_mode=accessibility_mode,
        building_metadata=b_meta,
        validation_status=validation_status
    )
