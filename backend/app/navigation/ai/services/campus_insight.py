# backend/app/navigation/ai/services/campus_insight.py

from typing import Dict, Any, List, Optional

class CampusInsightService:
    def compile_spatial_insights(
        self,
        current_building: Optional[Dict[str, Any]],
        next_class_info: Optional[Dict[str, Any]],
        closest_hostel: Optional[Dict[str, Any]],
        closest_services: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Creates a list of answers to common campus questions.
        """
        insights = {}
        
        # 1. Where am I?
        if current_building:
            insights["current_location"] = f"You are currently at {current_building['name']} ({current_building['category']})."
        else:
            insights["current_location"] = "Your current coordinates are not within a registered building. You are in transit on campus."

        # 2. Next class
        if next_class_info:
            insights["next_class"] = f"Your next class '{next_class_info['subject']}' is scheduled in {next_class_info['classroom']} ({next_class_info['building']}) starting at {next_class_info['start_time']}."
        else:
            insights["next_class"] = "You have no remaining classes scheduled for today."

        # 3. Closest Hostel
        if closest_hostel:
            insights["closest_hostel"] = f"The closest hostel to you is {closest_hostel['name']} ({closest_hostel['distance_meters']}m away)."

        # 4. Nearest Xerox/Printer
        xerox = closest_services.get("xerox", [])
        if xerox:
            insights["nearest_printer"] = f"The nearest copy center / printer is {xerox[0]['name']} ({xerox[0]['distance_meters']}m away)."
        else:
            insights["nearest_printer"] = "No registered Xerox shops found within 500m."

        # 5. Nearest ATM
        atms = closest_services.get("atms", [])
        if atms:
            insights["nearest_atm"] = f"The nearest ATM is {atms[0]['name']} ({atms[0]['distance_meters']}m away)."

        return insights
