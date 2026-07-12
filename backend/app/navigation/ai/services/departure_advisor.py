# backend/app/navigation/ai/services/departure_advisor.py

from datetime import datetime, timedelta
from typing import Dict, Any

class DepartureAdvisor:
    def calculate_departure_plan(
        self,
        current_time: datetime,
        class_start_str: str,  # "HH:MM" e.g., "09:00"
        walking_seconds: float,
        buffer_minutes: float = 2.0
    ) -> Dict[str, Any]:
        """
        Computes recommended departure time and relative status.
        """
        try:
            # Parse class start time
            hour, minute = map(int, class_start_str.split(":"))
            class_start = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
        except Exception:
            return {
                "advisable": False,
                "status": "unknown",
                "message": "Invalid class start time format."
            }

        # If class time resolved is in the past (e.g. checking late night for next day), roll forward
        if class_start < current_time - timedelta(hours=4):
            class_start += timedelta(days=1)

        # Walking time duration
        walking_duration = timedelta(seconds=walking_seconds)
        buffer_duration = timedelta(minutes=buffer_minutes)

        # Recommended departure = class_start - walking - buffer
        recommended_departure = class_start - walking_duration - buffer_duration

        # Time difference in minutes from current time
        seconds_to_leave = (recommended_departure - current_time).total_seconds()
        minutes_to_leave = seconds_to_leave / 60.0

        # Total travel time needed (walking + buffer)
        total_time_needed = walking_seconds + (buffer_minutes * 60.0)
        seconds_to_class = (class_start - current_time).total_seconds()

        if seconds_to_class < 0:
            status = "already_started"
            message = "Your class has already started."
        elif seconds_to_class < walking_seconds:
            status = "late"
            message = "You are already late and cannot make it to class on time."
        elif minutes_to_leave <= 0:
            status = "urgent"
            message = f"You should leave immediately to reach on time (walking duration is {round(walking_seconds/60.0)} mins)."
        elif minutes_to_leave <= 5:
            status = "soon"
            message = f"You should leave in {round(minutes_to_leave)} minute(s)."
        else:
            status = "safe"
            message = f"You have enough time to stop at the cafeteria before heading to class. Recommended departure in {round(minutes_to_leave)} minute(s)."

        return {
            "advisable": True,
            "class_start": class_start.strftime("%I:%M %p"),
            "walking_minutes": round(walking_seconds / 60.0, 1),
            "recommended_departure_time": recommended_departure.strftime("%I:%M %p"),
            "minutes_remaining_to_leave": round(minutes_to_leave, 1),
            "status": status,
            "recommendation": message
        }
