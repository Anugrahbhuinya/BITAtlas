from datetime import datetime, timezone, timedelta
import uuid
from fastapi import HTTPException, status
from typing import Dict, Any, List, Optional

from app.repositories.timetable_repository import TimetableRepository
from app.models.timetable import (
    TimetableModel, 
    ClassEntryModel, 
    ClassEntryCreateRequest, 
    ClassEntryUpdateRequest
)

def get_india_now() -> datetime:
    """Returns the current datetime in India Standard Time (IST - UTC+5:30)."""
    return datetime.now(timezone(timedelta(hours=5, minutes=30)))

def parse_time_to_minutes(time_str: str) -> int:
    """Parses a time string in format HH:MM into minutes from midnight."""
    try:
        parts = time_str.split(":")
        hours = int(parts[0])
        minutes = int(parts[1])
        if not (0 <= hours < 24 and 0 <= minutes < 60):
            raise ValueError()
        return hours * 60 + minutes
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid time format: {time_str}. Must be HH:MM in 24-hour format."
        )

def check_timing_overlap(
    existing_classes: List[Dict[str, Any]], 
    day: str, 
    start_time_str: str, 
    end_time_str: str, 
    exclude_entry_id: Optional[str] = None
) -> None:
    """
    Validates that the class slot does not overlap with any existing classes.
    """
    start_mins = parse_time_to_minutes(start_time_str)
    end_mins = parse_time_to_minutes(end_time_str)

    if start_mins >= end_mins:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start time must be strictly before end time."
        )

    # Check for overlaps with classes on the same day
    for entry in existing_classes:
        day_val = entry.get("day")
        if not day_val or day_val.strip().lower() != day.strip().lower():
            continue
        if exclude_entry_id and entry.get("id") == exclude_entry_id:
            continue
            
        exist_start = parse_time_to_minutes(entry.get("start_time") or "")
        exist_end = parse_time_to_minutes(entry.get("end_time") or "")

        # Intersection check: max(start1, start2) < min(end1, end2)
        if max(start_mins, exist_start) < min(end_mins, exist_end):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Timetable conflict: Slot overlaps with '{entry.get('subject')}' "
                    f"({entry.get('start_time')} - {entry.get('end_time')}) in {entry.get('classroom')}."
                )
            )

class TimetableService:
    def __init__(self, repo: TimetableRepository):
        self.repo = repo

    async def get_or_create_timetable(self, student_id: str, student_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gets the student's timetable. If not found, creates an empty one prefilled with their profile.
        """
        timetable = await self.repo.get_by_student_id(student_id)
        if not timetable:
            model = TimetableModel(
                student_id=student_id,
                semester=student_profile.get("semester", 1),
                department=student_profile.get("department", "General"),
                section=student_profile.get("section", "A"),
                academic_year=student_profile.get("year", 1),
                classes=[]
            )
            timetable = await self.repo.create(model.to_dict())
        return timetable

    async def get_week_grouped_timetable(self, student_id: str, student_profile: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Returns the timetable grouped by weekday, with classes sorted by start time.
        """
        timetable = await self.get_or_create_timetable(student_id, student_profile)
        classes = timetable.get("classes", [])

        grouped: Dict[str, List[Dict[str, Any]]] = {
            "Monday": [],
            "Tuesday": [],
            "Wednesday": [],
            "Thursday": [],
            "Friday": [],
            "Saturday": []
        }

        for item in classes:
            day = item.get("day")
            if day in grouped:
                grouped[day].append(item)

        # Sort each day's classes by start_time
        for day in grouped:
            grouped[day].sort(key=lambda x: parse_time_to_minutes(x.get("start_time") or "00:00"))

        return grouped

    async def add_class_entry(self, student_id: str, student_profile: Dict[str, Any], payload: ClassEntryCreateRequest) -> Dict[str, Any]:
        """
        Adds a new validated class entry to the student's timetable.
        """
        timetable = await self.get_or_create_timetable(student_id, student_profile)
        classes = timetable.get("classes", [])

        # Validate day name
        standard_days = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"}
        day_standardized = payload.day.strip().capitalize()
        if day_standardized not in standard_days:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Day must be one of: {', '.join(standard_days)}"
            )

        # Check overlaps
        check_timing_overlap(
            existing_classes=classes,
            day=day_standardized,
            start_time_str=payload.start_time,
            end_time_str=payload.end_time
        )

        # Create new class model
        entry_model = ClassEntryModel(
            id=str(uuid.uuid4()),
            day=day_standardized,
            subject=payload.subject.strip(),
            faculty=payload.faculty.strip(),
            classroom=payload.classroom.strip(),
            building=payload.building.strip() if payload.building else None,
            start_time=payload.start_time,
            end_time=payload.end_time,
            remarks=payload.remarks.strip() if payload.remarks else None
        )

        classes.append(entry_model.model_dump())
        
        update_data = {
            "classes": classes,
            "updated_at": datetime.now(timezone.utc)
        }
        
        updated = await self.repo.update(student_id, update_data)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add class entry to timetable"
            )
        return updated

    async def update_class_entry(
        self, 
        student_id: str, 
        student_profile: Dict[str, Any], 
        entry_id: str, 
        payload: ClassEntryUpdateRequest
    ) -> Dict[str, Any]:
        """
        Updates an existing class entry with overlap validation.
        """
        timetable = await self.get_or_create_timetable(student_id, student_profile)
        classes = timetable.get("classes", [])

        # Find target entry index
        entry_index = -1
        for idx, entry in enumerate(classes):
            if entry.get("id") == entry_id:
                entry_index = idx
                break

        if entry_index == -1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class entry not found in student timetable."
            )

        target = classes[entry_index]

        # Standardize and validate parameters
        day = payload.day.strip().capitalize() if payload.day else target.get("day")
        start_time = payload.start_time if payload.start_time else target.get("start_time")
        end_time = payload.end_time if payload.end_time else target.get("end_time")

        standard_days = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"}
        if day not in standard_days:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Day must be one of: {', '.join(standard_days)}"
            )

        # Validate overlaps excluding target entry
        check_timing_overlap(
            existing_classes=classes,
            day=day,
            start_time_str=start_time,
            end_time_str=end_time,
            exclude_entry_id=entry_id
        )

        # Apply updates
        target["day"] = day
        target["start_time"] = start_time
        target["end_time"] = end_time

        if payload.subject is not None:
            target["subject"] = payload.subject.strip()
        if payload.faculty is not None:
            target["faculty"] = payload.faculty.strip()
        if payload.classroom is not None:
            target["classroom"] = payload.classroom.strip()
        if payload.building is not None:
            target["building"] = payload.building.strip() if payload.building else None
        if payload.remarks is not None:
            target["remarks"] = payload.remarks.strip() if payload.remarks else None

        classes[entry_index] = target

        update_data = {
            "classes": classes,
            "updated_at": datetime.now(timezone.utc)
        }

        updated = await self.repo.update(student_id, update_data)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update class entry"
            )
        return updated

    async def delete_class_entry(self, student_id: str, student_profile: Dict[str, Any], entry_id: str) -> Dict[str, Any]:
        """
        Deletes a class entry from the student's timetable.
        """
        timetable = await self.get_or_create_timetable(student_id, student_profile)
        classes = timetable.get("classes", [])

        # Filter out the entry
        filtered_classes = [entry for entry in classes if entry.get("id") != entry_id]
        
        if len(filtered_classes) == len(classes):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class entry not found in student timetable."
            )

        update_data = {
            "classes": filtered_classes,
            "updated_at": datetime.now(timezone.utc)
        }

        updated = await self.repo.update(student_id, update_data)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete class entry"
            )
        return updated

    async def confirm_timetable(self, student_id: str, student_profile: Dict[str, Any], classes_payload: List[ClassEntryCreateRequest]) -> Dict[str, Any]:
        """
        Overwrites the student's classes with a list of verified entries (typically from AI import).
        """
        # Validate that none of the imported classes overlap
        validated_entries: List[Dict[str, Any]] = []
        for new_class in classes_payload:
            # Check overlap against currently accumulated list of new classes
            standard_day = new_class.day.strip().capitalize()
            check_timing_overlap(
                existing_classes=validated_entries,
                day=standard_day,
                start_time_str=new_class.start_time,
                end_time_str=new_class.end_time
            )
            
            entry = ClassEntryModel(
                id=str(uuid.uuid4()),
                day=standard_day,
                subject=new_class.subject.strip(),
                faculty=new_class.faculty.strip(),
                classroom=new_class.classroom.strip(),
                building=new_class.building.strip() if new_class.building else None,
                start_time=new_class.start_time,
                end_time=new_class.end_time,
                remarks=new_class.remarks.strip() if new_class.remarks else None
            )
            validated_entries.append(entry.model_dump())

        # Retrieve or create timetable shell
        await self.get_or_create_timetable(student_id, student_profile)

        update_data = {
            "classes": validated_entries,
            "updated_at": datetime.now(timezone.utc)
        }

        updated = await self.repo.update(student_id, update_data)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save confirmed timetable schedule"
            )
        return updated

    # ==========================================================================
    # AI EXTENSION METHODS (FOR FUTURE LLM CONTEXT EXTRACTIONS)
    # ==========================================================================

    async def get_today_classes_list(self, student_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves classes scheduled for today, sorted by start time.
        """
        timetable = await self.repo.get_by_student_id(student_id)
        if not timetable:
            return []
            
        today_day = get_india_now().strftime("%A")
        classes = timetable.get("classes", [])
        
        today_classes = [c for c in classes if c.get("day") == today_day]
        today_classes.sort(key=lambda x: parse_time_to_minutes(x.get("start_time")))
        return today_classes

    async def get_tomorrow_classes_list(self, student_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves classes scheduled for tomorrow, sorted by start time.
        """
        timetable = await self.repo.get_by_student_id(student_id)
        if not timetable:
            return []
            
        tomorrow_day = (get_india_now() + timedelta(days=1)).strftime("%A")
        classes = timetable.get("classes", [])
        
        tomorrow_classes = [c for c in classes if c.get("day") == tomorrow_day]
        tomorrow_classes.sort(key=lambda x: parse_time_to_minutes(x.get("start_time")))
        return tomorrow_classes

    async def get_current_lecture(self, student_id: str) -> Optional[Dict[str, Any]]:
        """
        Returns the lecture currently in progress based on India Standard Time.
        """
        today_classes = await self.get_today_classes_list(student_id)
        if not today_classes:
            return None

        now = get_india_now()
        current_mins = now.hour * 60 + now.minute

        for entry in today_classes:
            start_mins = parse_time_to_minutes(entry.get("start_time") or "")
            end_mins = parse_time_to_minutes(entry.get("end_time") or "")
            if start_mins <= current_mins <= end_mins:
                return entry
        return None

    async def get_next_lecture(self, student_id: str) -> Optional[Dict[str, Any]]:
        """
        Returns the next upcoming lecture of today. If none are left today, returns first class of tomorrow.
        """
        today_classes = await self.get_today_classes_list(student_id)
        now = get_india_now()
        current_mins = now.hour * 60 + now.minute

        # Find first class of today that has not started yet
        for entry in today_classes:
            start_mins = parse_time_to_minutes(entry.get("start_time") or "")
            if start_mins > current_mins:
                return entry

        # Fallback to first class of tomorrow
        tomorrow_classes = await self.get_tomorrow_classes_list(student_id)
        if tomorrow_classes:
            return tomorrow_classes[0]

        return None

    async def get_subject_schedule(self, student_id: str, subject_name: str) -> List[Dict[str, Any]]:
        """
        Retrieves all weekly schedule entries matching a subject name (case-insensitive).
        """
        timetable = await self.repo.get_by_student_id(student_id)
        if not timetable:
            return []
        
        classes = timetable.get("classes", [])
        subject_name_lower = subject_name.strip().lower()
        
        matches = [c for c in classes if subject_name_lower in c.get("subject", "").lower()]
        
        # Sort matches by weekday index and start time
        weekday_order = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5}
        matches.sort(key=lambda x: (weekday_order.get(x.get("day"), 6), parse_time_to_minutes(x.get("start_time"))))
        return matches
