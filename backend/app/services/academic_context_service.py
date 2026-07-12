import asyncio
from typing import Dict, Any, Optional

from app.context.student_context_provider import StudentContextProvider
from app.context.academic_context_provider import AcademicContextProvider
from app.context.timetable_context_provider import TimetableContextProvider
from app.context.attendance_context_provider import AttendanceContextProvider
from app.context.planner_context_provider import PlannerContextProvider
from app.context.calendar_context_provider import CalendarContextProvider

class AcademicContextService:
    def __init__(
        self,
        student_provider: StudentContextProvider,
        academic_provider: AcademicContextProvider,
        timetable_provider: TimetableContextProvider,
        attendance_provider: AttendanceContextProvider,
        planner_provider: PlannerContextProvider,
        calendar_provider: CalendarContextProvider,
        navigation_provider: Optional[Any] = None
    ):
        self.student_provider = student_provider
        self.academic_provider = academic_provider
        self.timetable_provider = timetable_provider
        self.attendance_provider = attendance_provider
        self.planner_provider = planner_provider
        self.calendar_provider = calendar_provider
        self.navigation_provider = navigation_provider

    async def get_academic_context(self, student_id: str, student_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Asynchronously aggregates academic contexts from all modular providers."""
        # Execute all providers concurrently
        student_task = self.student_provider.get_context(student_data)
        academic_task = self.academic_provider.get_context(student_id)
        timetable_task = self.timetable_provider.get_context(student_id)
        attendance_task = self.attendance_provider.get_context(student_id)
        planner_task = self.planner_provider.get_context(student_id)
        calendar_task = self.calendar_provider.get_context()

        results = await asyncio.gather(
            student_task,
            academic_task,
            timetable_task,
            attendance_task,
            planner_task,
            calendar_task,
            return_exceptions=True
        )

        # Handle exceptions gracefully
        def resolve_result(idx, default_val):
            r = results[idx]
            if isinstance(r, Exception):
                print(f"Error in context provider {idx}: {r}")
                return default_val
            return r

        timetable_ctx = resolve_result(2, {})
        attendance_ctx = resolve_result(3, {})
        planner_ctx = resolve_result(4, {})

        nav_ctx = {}
        if self.navigation_provider:
            try:
                nav_ctx = await self.navigation_provider.get_context(
                    student_id=student_id,
                    timetable_context=timetable_ctx,
                    attendance_context=attendance_ctx,
                    planner_context=planner_ctx
                )
            except Exception as e:
                print(f"Error in navigation context provider: {e}")

        return {
            "student": resolve_result(0, {}),
            "workspace": resolve_result(1, {}),
            "timetable": timetable_ctx,
            "attendance": attendance_ctx,
            "planner": planner_ctx,
            "calendar": resolve_result(5, {}),
            "navigation": nav_ctx
        }

    def format_context_to_string(self, ctx: Dict[str, Any]) -> str:
        """Converts the normalized context dictionary into structured Markdown context for LLM injection."""
        lines = []

        # 1. Student Info
        student = ctx.get("student", {})
        if student.get("status") == "authenticated":
            lines.append("### Student Profile")
            lines.append(f"- **Name**: {student.get('name')}")
            lines.append(f"- **Roll Number**: {student.get('roll_number')}")
            lines.append(f"- **Department**: {student.get('department')}")
            lines.append(f"- **Semester**: {student.get('semester')}")
            lines.append(f"- **Section**: {student.get('section')}")
            lines.append("")
        else:
            # Anonymous context
            lines.append("### Student Profile")
            lines.append("- Anonymous/Guest Student session. No profile fields available.")
            lines.append("")

        # 2. Timetable Info
        tt = ctx.get("timetable", {})
        if tt.get("timetable_configured"):
            lines.append("### Student Weekly Timetable")
            lines.append(f"- **Busiest Day**: {tt.get('busiest_day')} (with {tt.get('max_classes_in_a_day')} classes)")
            lines.append("- **Classes Scheduled today (IST)**:")
            today_cls = tt.get("today_classes", [])
            if today_cls:
                for idx, c in enumerate(today_cls, 1):
                    lines.append(f"  {idx}. {c['subject']} with {c['faculty']} at {c['time']} in {c['classroom']} (Building: {c.get('building', 'N/A')})")
            else:
                lines.append("  - No classes scheduled today.")

            lines.append("- **Classes Scheduled tomorrow (IST)**:")
            tom_cls = tt.get("tomorrow_classes", [])
            if tom_cls:
                for idx, c in enumerate(tom_cls, 1):
                    lines.append(f"  {idx}. {c['subject']} with {c['faculty']} at {c['time']} in {c['classroom']} (Building: {c.get('building', 'N/A')})")
            else:
                lines.append("  - No classes scheduled tomorrow.")

            lines.append("- **Full Weekly Class Schedule**:")
            for day, day_classes in tt.get("day_wise_schedule", {}).items():
                lines.append(f"  - **{day}**:")
                for c in day_classes:
                    lines.append(f"    - {c['subject']} with {c['faculty']} in {c['classroom']} at {c['time']}")
            lines.append("")

        # 3. Attendance Info
        att = ctx.get("attendance", {})
        if att.get("has_attendance_data"):
            lines.append("### Cumulative Attendance Summary")
            lines.append(f"- **Overall Cumulative Attendance**: {att.get('overall_attendance_percentage'):.1f}%")
            
            below = att.get("subjects_below_75_threshold", [])
            if below:
                lines.append("- **At Risk Subjects (Below 75% threshold)**:")
                for b in below:
                    lines.append(f"  - {b['subject_name']}: {b['attendance_percentage']:.1f}% (Conducted: {b['total_conducted']}, Attended: {b['total_attended']}, Recovery: {b['required_classes']} classes needed)")
            else:
                lines.append("- **At Risk Subjects**: None. All classes are above the 75% threshold.")

            lowest = att.get("lowest_attendance_subject")
            if lowest:
                lines.append(f"- **Lowest Attendance subject**: {lowest['subject_name']} ({lowest['attendance_percentage']:.1f}%)")

            lines.append("- **Course-wise Attendance Breakdown & Safe Leaves (Bunks)**:")
            for s in att.get("subject_details", []):
                lines.append(f"  - {s['subject_name']} by {s['faculty']}: {s['attendance_percentage']:.1f}% (Conducted: {s['total_conducted']}, Attended: {s['total_attended']}, Safe Leaves (bunks remaining): {s['safe_leaves']})")
            lines.append("")

        # 4. Planner Info
        pl = ctx.get("planner", {})
        if pl.get("has_planner_data"):
            lines.append("### Planner Checklist Tasks")
            lines.append(f"- **Pending Tasks Count**: {pl.get('pending_tasks_count')}")
            lines.append(f"- **Completed Tasks Count**: {pl.get('completed_tasks_count')}")
            
            pending = pl.get("pending_tasks", [])
            if pending:
                lines.append("- **Pending Task Items**:")
                for p in pending:
                    time_info = f" at {p['due_time']}" if p.get("due_time") else ""
                    desc = f" ({p['description']})" if p.get("description") else ""
                    lines.append(f"  - [{p['priority']} Priority] {p['title']} - Due: {p['due_date']}{time_info}{desc} [Category: {p['category']}]")
            
            exams = pl.get("upcoming_exams", [])
            if exams:
                lines.append("- **Upcoming Exam Tasks**:")
                for e in exams:
                    lines.append(f"  - {e['title']} scheduled on {e['due_date']}")

            quizzes = pl.get("upcoming_quizzes", [])
            if quizzes:
                lines.append("- **Upcoming Class Quizzes**:")
                for q in quizzes:
                    lines.append(f"  - {q['title']} scheduled on {q['due_date']}")
            lines.append("")

        # 5. Calendar Info
        cal = ctx.get("calendar", {})
        milestones = cal.get("upcoming_academic_calendar_commencements", [])
        if not milestones:
            milestones = cal.get("upcoming_academic_calendar_milestones", [])
            
        if milestones:
            lines.append("### Academic Calendar Commencement & Events")
            for m in milestones:
                end_str = f" to {m['end_date']}" if m['end_date'] != m['start_date'] else ""
                lines.append(f"- {m['event']}: {m['start_date']}{end_str}")
            lines.append("")

        # 6. Navigation and Campus AI Context
        nav = ctx.get("navigation", {})
        if nav:
            lines.append("### Student Navigation & Campus Context")
            
            # Location
            curr_bldg = nav.get("current_building")
            if curr_bldg:
                lines.append(f"- **Current Location**: Housed at {curr_bldg['name']}")
            
            # Routing
            routing = nav.get("routing")
            if routing:
                lines.append(f"- **Active Route**: From '{routing['start']}' to '{routing['destination']}' ({routing['distance_meters']}m, approx. {routing['walking_time_minutes']} mins walking, Type: {routing['route_type']}, Wheelchair Accessible: {routing['accessible']})")

            # Departure Advisor
            advisor = nav.get("departure_advisor")
            if advisor and advisor.get("advisable"):
                lines.append(f"- **Next Class Departure**: Starts at {advisor['class_start']}. Walk time: {advisor['walking_minutes']} mins. Recommended Leave Time: {advisor['recommended_departure_time']} ({advisor['recommendation']})")

            # Insights
            insights = nav.get("campus_insights", {})
            if insights:
                lines.append("- **Campus Spatial Answers**:")
                for k, v in insights.items():
                    lines.append(f"  - {k}: {v}")

            # Nearby Services
            nearby = nav.get("nearby_services", {})
            if nearby and any(nearby.values()):
                lines.append("- **Nearby Services (Sorted by Distance)**:")
                for service_type, places in nearby.items():
                    if places:
                        place_strs = [f"{p['name']} ({p['distance_meters']}m)" for p in places]
                        lines.append(f"  - **{service_type.capitalize()}**: {', '.join(place_strs)}")

            # Contextual AI Actions / Suggestions
            reasoning = nav.get("reasoning", {})
            if reasoning:
                lines.append(f"- **AI Directive**: {reasoning.get('directive')}")
                alerts = reasoning.get("alerts", [])
                if alerts:
                    lines.append("- **Critical Alerts**:")
                    for a in alerts:
                        lines.append(f"  - {a}")
            lines.append("")

        return "\n".join(lines)
