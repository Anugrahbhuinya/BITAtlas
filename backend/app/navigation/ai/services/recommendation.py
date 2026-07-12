# backend/app/navigation/ai/services/recommendation.py

from typing import List, Dict, Any

class RecommendationService:
    def get_contextual_suggestions(self, minutes_before_class: float) -> List[Dict[str, Any]]:
        """
        Suggests activities based on available time margin.
        """
        if minutes_before_class <= 0:
            return [{
                "action": "Navigate to Next Class",
                "label": "Head to class immediately",
                "suggestion": "You are late. Run to class."
            }]
        elif minutes_before_class < 10:
            return [
                {
                    "action": "Navigate to Next Class",
                    "label": "Head to class now",
                    "suggestion": "Head straight to your lecture room."
                },
                {
                    "action": "Show Water Station",
                    "label": "Get water",
                    "suggestion": "Quick stop at the nearest water dispenser."
                }
            ]
        elif minutes_before_class < 25:
            return [
                {
                    "action": "Show Cafeteria",
                    "label": "Grab Coffee",
                    "suggestion": "Grab a quick coffee or snack at the Canteen."
                },
                {
                    "action": "Navigate to Next Class",
                    "label": "Head to class",
                    "suggestion": "Walk slowly towards your classroom building."
                }
            ]
        else:
            return [
                {
                    "action": "Show Library",
                    "label": "Visit Library",
                    "suggestion": "Study or read at the Central Library."
                },
                {
                    "action": "Show Cafeteria",
                    "label": "Visit Food Court",
                    "suggestion": "Hang out at the Food Court or SAC."
                }
            ]

    def categorize_nearby_recommendations(self, nearby_places: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        categorized: Dict[str, List[Dict[str, Any]]] = {
            "cafeterias": [],
            "atms": [],
            "washrooms": [],
            "xerox": [],
            "study_areas": []
        }

        for place in nearby_places:
            cat = place["category"].lower()
            name = place["name"].lower()
            
            if "cafe" in cat or "canteen" in cat or "food" in cat or "nescafe" in name:
                categorized["cafeterias"].append(place)
            elif "atm" in cat or "bank" in cat or "sbi" in name:
                categorized["atms"].append(place)
            elif "washroom" in cat or "toilet" in cat or "restroom" in cat:
                categorized["washrooms"].append(place)
            elif "xerox" in cat or "printer" in cat or "copy" in name:
                categorized["xerox"].append(place)
            elif "library" in cat or "study" in cat or "reading" in cat:
                categorized["study_areas"].append(place)

        return categorized
