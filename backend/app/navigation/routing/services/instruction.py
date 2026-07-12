# backend/app/navigation/routing/services/instruction.py

import math
from typing import List
from app.navigation.graph.models import CampusNode, CampusEdge

class InstructionService:
    def _calculate_bearing(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        # returns bearing in degrees from 0 to 360
        d_lon = math.radians(lon2 - lon1)
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        y = math.sin(d_lon) * math.cos(lat2_rad)
        x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(d_lon)
        bearing = math.atan2(y, x)
        return (math.degrees(bearing) + 360) % 360

    def _bearing_to_direction(self, bearing: float) -> str:
        if 337.5 <= bearing or bearing < 22.5:
            return "north"
        elif 22.5 <= bearing < 67.5:
            return "northeast"
        elif 67.5 <= bearing < 112.5:
            return "east"
        elif 112.5 <= bearing < 157.5:
            return "southeast"
        elif 157.5 <= bearing < 202.5:
            return "south"
        elif 202.5 <= bearing < 247.5:
            return "southwest"
        elif 247.5 <= bearing < 292.5:
            return "west"
        else:
            return "northwest"

    def generate_instructions(self, nodes: List[CampusNode], edges: List[CampusEdge]) -> List[str]:
        if not nodes:
            return ["No route found."]
        if len(nodes) == 1:
            return [f"You are already at {nodes[0].name}."]

        instructions = []
        start_node = nodes[0]
        instructions.append(f"Start at {start_node.name}.")

        prev_bearing = None

        for i in range(len(edges)):
            edge = edges[i]
            curr_node = nodes[i]
            next_node = nodes[i+1]

            dist = edge.distance if edge.distance is not None else 1.0
            dist_str = f"{dist:.1f} meters" if dist >= 1.0 else "a few steps"

            rel = edge.relationship.value if hasattr(edge.relationship, 'value') else str(edge.relationship)

            if rel == "HAS_ENTRANCE":
                instructions.append(f"Walk to the entrance '{next_node.name}'.")
            elif rel == "CONNECTS_TO":
                instructions.append(f"Go through the entrance into '{next_node.name}'.")
            elif rel == "CONTAINS":
                instructions.append(f"Head inside towards '{next_node.name}'.")
            elif rel == "LOCATED_IN":
                instructions.append(f"Exit room into '{next_node.name}'.")
            elif rel == "FLOOR_CONNECTION":
                curr_floor = curr_node.metadata.get("floor", 0)
                next_floor = next_node.metadata.get("floor", 0)
                if next_floor > curr_floor:
                    instructions.append(f"Take stairs up to Floor {next_floor}.")
                else:
                    instructions.append(f"Take stairs down to Floor {next_floor}.")
            elif rel == "WALKWAY":
                surf = (edge.metadata or {}).get("surface", "concrete")
                bearing = self._calculate_bearing(curr_node.latitude, curr_node.longitude, next_node.latitude, next_node.longitude)
                direction = self._bearing_to_direction(bearing)
                
                if prev_bearing is None:
                    # First walkway
                    instructions.append(f"Walk {direction} {dist_str} along the {surf} pathway towards '{next_node.name}'.")
                else:
                    # Calculate turn angle
                    diff = (bearing - prev_bearing + 540) % 360 - 180
                    if -135 < diff < -45:
                        turn = "Turn left"
                    elif 45 < diff < 135:
                        turn = "Turn right"
                    elif diff >= 135 or diff <= -135:
                        turn = "Make a U-turn"
                    else:
                        turn = "Continue straight"
                    instructions.append(f"{turn} and walk {dist_str} along the {surf} pathway towards '{next_node.name}'.")
                
                prev_bearing = bearing
            else:
                instructions.append(f"Head towards '{next_node.name}' ({dist_str}).")

        instructions.append(f"Arrived at your destination: {nodes[-1].name}.")
        return instructions
