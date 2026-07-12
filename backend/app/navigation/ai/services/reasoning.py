# backend/app/navigation/ai/services/reasoning.py

from typing import Dict, Any, List, Optional

class NavigationReasoningService:
    def reason_over_student_state(
        self,
        timetable_context: Dict[str, Any],
        attendance_context: Dict[str, Any],
        planner_context: Dict[str, Any],
        departure_plan: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Integrates planner deadlines and attendance warnings with routing and departure plans.
        """
        reasoning_alerts = []
        action_priorities = []
        suggested_destination = None

        # 1. Attendance urgency check
        # If attendance below 75% threshold in today's upcoming subject, raise priority
        if departure_plan and departure_plan.get("advisable"):
            subject_name = departure_plan.get("subject_name", "")
            
            # Find subject in attendance details
            subject_details = attendance_context.get("subject_details", [])
            target_subj = next((s for s in subject_details if s["subject_name"].lower() == subject_name.lower()), None)
            
            if target_subj:
                pct = target_subj.get("attendance_percentage", 100.0)
                if pct < 75.0:
                    reasoning_alerts.append(
                        f"CRITICAL WARNING: Your attendance in '{subject_name}' is currently {pct:.1f}% (below 75%). "
                        "Missing this class will further jeopardize your eligibility. Prioritize heading to class immediately."
                    )
                    action_priorities.append("high_attendance_urgency")

        # 2. Planner deadline check
        # If an assignment or exam is due today, recommend study spaces
        pending_tasks = planner_context.get("pending_tasks", [])
        has_due_today = any(t.get("priority") == "High" or "exam" in t.get("title", "").lower() for t in pending_tasks)
        
        if has_due_today:
            reasoning_alerts.append(
                "You have pending high-priority tasks or exams scheduled. "
                "Consider visiting the Central Library or Department Lab for study sessions before class starts."
            )
            action_priorities.append("study_needed")
            suggested_destination = "Central Library"

        # Determine overall directive
        if "high_attendance_urgency" in action_priorities:
            directive = "Head directly to class now. Attendance is critical."
        elif departure_plan and departure_plan.get("status") in ["urgent", "late"]:
            directive = "Leave immediately for class."
        elif "study_needed" in action_priorities:
            directive = "Use your free time to study at the Library or Department Lab."
        else:
            directive = "Enjoy your free time, check nearby cafeteria recommendations."

        return {
            "alerts": reasoning_alerts,
            "priorities": action_priorities,
            "suggested_destination": suggested_destination,
            "directive": directive
        }
