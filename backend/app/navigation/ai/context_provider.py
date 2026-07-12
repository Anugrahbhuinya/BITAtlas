# backend/app/navigation/ai/context_provider.py

from typing import Dict, Any, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.navigation.ai.services.nearby import NearbyService
from app.navigation.ai.services.departure_advisor import DepartureAdvisor
from app.navigation.ai.services.recommendation import RecommendationService
from app.navigation.ai.services.campus_insight import CampusInsightService
from app.navigation.ai.services.reasoning import NavigationReasoningService

from app.navigation.routing.services.routing import RoutingService
from app.navigation.graph.repositories import get_graph_repository
from app.navigation.routing.repositories.route_cache import get_route_cache_repository
from app.navigation.routing.services.eta import ETAService
from app.navigation.routing.services.instruction import InstructionService
from app.services.timetable_service import get_india_now

class NavigationContextProvider:
    def __init__(self, db: AsyncIOMotorDatabase, nav_data: Optional[Dict[str, Any]] = None):
        self.db = db
        self.nav_data = nav_data or {}
        
        self.nearby_service = NearbyService(db)
        self.departure_advisor = DepartureAdvisor()
        self.recommendation_service = RecommendationService()
        self.campus_insight_service = CampusInsightService()
        self.reasoning_service = NavigationReasoningService()
        
        graph_repo = get_graph_repository()
        route_cache = get_route_cache_repository()
        eta_service = ETAService()
        instruction_service = InstructionService()
        self.routing_service = RoutingService(graph_repo, route_cache, eta_service, instruction_service)

    async def get_context(
        self,
        student_id: str,
        timetable_context: Dict[str, Any],
        attendance_context: Dict[str, Any],
        planner_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Gathers complete navigation context, calculating coordinates routing, ETA and departure urgency.
        """
        current_loc_id = self.nav_data.get("currentLocationNodeId")
        dest_loc_id = self.nav_data.get("currentDestinationNodeId")
        access_mode = self.nav_data.get("accessibilityMode", False)

        lat = None
        lon = None
        current_building = None
        nearby_places = []
        closest_services = {}

        # 1. Resolve current building & coordinates
        if current_loc_id:
            node = await self.db.nodes.find_one({"id": current_loc_id})
            if node:
                lat = node.get("latitude")
                lon = node.get("longitude")
                current_building = {
                    "id": current_loc_id,
                    "name": node.get("name"),
                    "category": node.get("type")
                }
                
                # Fetch nearby options within 500m
                nearby_places = await self.nearby_service.find_nearby_places(lat, lon)
                closest_services = self.recommendation_service.categorize_nearby_recommendations(nearby_places)

        # 2. Resolve active routing context
        routing_info = None
        if current_loc_id and dest_loc_id:
            strategy = "accessible" if access_mode else "shortest"
            try:
                route = await self.routing_service.calculate_route(current_loc_id, dest_loc_id, strategy)
                if route:
                    routing_info = {
                        "start": route.start_node.name,
                        "destination": route.destination_node.name,
                        "distance_meters": round(route.total_distance, 1),
                        "walking_time_seconds": round(route.estimated_walking_time, 1),
                        "walking_time_minutes": round(route.estimated_walking_time / 60.0, 1),
                        "accessible": route.accessibility_information,
                        "route_type": strategy
                    }
            except Exception:
                pass

        # 3. Resolve upcoming class departure plan
        departure_plan = None
        next_class_info = None
        india_now = get_india_now()
        
        # Check today's classes
        today_classes = timetable_context.get("today_classes", [])
        if today_classes:
            # Find first class starting after india_now time
            curr_time_str = india_now.strftime("%H:%M")
            upcoming = [c for c in today_classes if c.get("start_time", "") > curr_time_str]
            if upcoming:
                next_class = upcoming[0]
                class_start_str = next_class.get("start_time")
                
                # Resolve building code
                room_code = next_class.get("classroom", "")
                building_name = next_class.get("building") or ""
                
                # Try to locate the classroom node
                class_node_id = None
                class_node = await self.db.nodes.find_one({
                    "$or": [
                        {"name": {"$regex": room_code, "$options": "i"}},
                        {"name": {"$regex": building_name, "$options": "i"}}
                    ]
                })
                if class_node:
                    class_node_id = class_node.get("id")

                # If current location and next class node coordinates are both known, compute walking distance
                walking_seconds = 420.0  # default 7 mins
                if current_loc_id and class_node_id:
                    try:
                        route = await self.routing_service.calculate_route(current_loc_id, class_node_id, "shortest")
                        if route:
                            walking_seconds = route.estimated_walking_time
                    except Exception:
                        pass
                
                departure_plan = self.departure_advisor.calculate_departure_plan(
                    current_time=india_now,
                    class_start_str=class_start_str,
                    walking_seconds=walking_seconds
                )
                departure_plan["subject_name"] = next_class.get("subject")
                next_class_info = next_class

        # 4. Contextual suggestions (cafeteria, water, study room)
        suggestions = []
        if departure_plan and departure_plan.get("advisable"):
            min_remaining = departure_plan.get("minutes_remaining_to_leave", 15.0)
            suggestions = self.recommendation_service.get_contextual_suggestions(min_remaining)

        # 5. Closest hostel helper
        closest_hostel = None
        if lat and lon:
            hostel_nodes = await self.nearby_service.find_nearby_places(lat, lon, radius=800.0)
            hostels = [h for h in hostel_nodes if "hostel" in h["category"].lower() or h["type"] == "hostel"]
            if hostels:
                closest_hostel = hostels[0]

        # 6. Reasoning & Action Alerts
        reasoning = self.reasoning_service.reason_over_student_state(
            timetable_context=timetable_context,
            attendance_context=attendance_context,
            planner_context=planner_context,
            departure_plan=departure_plan
        )

        # 7. Compile direct spatial answers (Campus Insights)
        insights = self.campus_insight_service.compile_spatial_insights(
            current_building=current_building,
            next_class_info=next_class_info,
            closest_hostel=closest_hostel,
            closest_services=closest_services
        )

        # Construct structured JSON context response
        return {
            "current_location_id": current_loc_id,
            "destination_location_id": dest_loc_id,
            "accessibility_mode": access_mode,
            "current_building": current_building,
            "routing": routing_info,
            "departure_advisor": departure_plan,
            "contextual_suggestions": suggestions,
            "reasoning": reasoning,
            "campus_insights": insights,
            "nearby_services": {
                "cafeterias": closest_services.get("cafeterias", [])[:3],
                "atms": closest_services.get("atms", [])[:3],
                "washrooms": closest_services.get("washrooms", [])[:3],
                "xerox": closest_services.get("xerox", [])[:3],
                "study_areas": closest_services.get("study_areas", [])[:3]
            }
        }
