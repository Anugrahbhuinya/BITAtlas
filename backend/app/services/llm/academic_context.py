"""
Academic context generation extension point for Gemini.
Loads and formats database contexts (timetable, attendance, planner, calendar)
for injection into LLM prompts.
"""

from typing import Dict, Any, Optional
from app.core.database import get_database
from app.repositories.academic_repository import AcademicRepository
from app.repositories.timetable_repository import TimetableRepository
from app.repositories.attendance_repository import AttendanceRepository
from app.repositories.planner_repository import PlannerRepository

from app.context.student_context_provider import StudentContextProvider
from app.context.academic_context_provider import AcademicContextProvider
from app.context.timetable_context_provider import TimetableContextProvider
from app.context.attendance_context_provider import AttendanceContextProvider
from app.context.planner_context_provider import PlannerContextProvider
from app.context.calendar_context_provider import CalendarContextProvider
from app.navigation.ai.context_provider import NavigationContextProvider
from app.services.academic_context_service import AcademicContextService

async def get_academic_prompt_context(
    student_id: str,
    student_data: Optional[Dict[str, Any]] = None,
    nav_data: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generates structured academic and navigation context for the student to inject into the LLM prompt.
    """
    if not student_id:
        return ""

    try:
        db = get_database()
        
        # Instantiate repos, providers, and aggregation service
        academic_repo = AcademicRepository(db)
        timetable_repo = TimetableRepository(db)
        attendance_repo = AttendanceRepository(db)
        planner_repo = PlannerRepository(db)

        service = AcademicContextService(
            StudentContextProvider(),
            AcademicContextProvider(academic_repo),
            TimetableContextProvider(timetable_repo),
            AttendanceContextProvider(attendance_repo),
            PlannerContextProvider(planner_repo),
            CalendarContextProvider(),
            NavigationContextProvider(db, nav_data)
        )

        ctx = await service.get_academic_context(student_id, student_data)
        return service.format_context_to_string(ctx)
    except Exception as e:
        # Graceful fallback: return empty context so prompt building doesn't crash
        import logging
        logging.getLogger("academic_context").error(f"Failed to compile academic prompt context: {e}", exc_info=True)
        return ""
