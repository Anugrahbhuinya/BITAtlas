from datetime import datetime, timezone, timedelta
import uuid
import math
from fastapi import HTTPException, status
from typing import Dict, Any, List, Optional

from app.repositories.attendance_repository import AttendanceRepository
from app.repositories.timetable_repository import TimetableRepository
from app.models.attendance import (
    AttendanceRecordModel,
    AttendanceLogModel,
    AttendanceLogCreateRequest,
    AttendanceLogUpdateRequest
)
from app.services.attendance_calculator import calculate_stats

def get_india_now() -> datetime:
    """Returns the current datetime in India Standard Time (IST - UTC+5:30)."""
    return datetime.now(timezone(timedelta(hours=5, minutes=30)))

def get_india_date_str() -> str:
    """Returns today's date in IST as a YYYY-MM-DD string."""
    return get_india_now().strftime("%Y-%m-%d")

def is_future_date(date_str: str) -> bool:
    """Returns True if the date_str (YYYY-MM-DD) is in the future relative to IST today."""
    try:
        today = get_india_now().date()
        target = datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
        return target > today
    except Exception:
        return True

class AttendanceService:
    def __init__(self, repo: AttendanceRepository, timetable_repo: TimetableRepository):
        self.repo = repo
        self.timetable_repo = timetable_repo

    async def sync_timetable_subjects(self, student_id: str, student_profile: Dict[str, Any]) -> None:
        """
        Extracts unique subjects from the student's timetable and ensures
        an AttendanceRecord document exists in MongoDB for each subject.
        """
        timetable = await self.timetable_repo.get_by_student_id(student_id)
        if not timetable or not timetable.get("classes"):
            return

        classes = timetable.get("classes", [])
        seen_subjects = {}
        for cls in classes:
            sub_name = cls.get("subject", "").strip()
            if sub_name and sub_name.lower() not in seen_subjects:
                seen_subjects[sub_name.lower()] = {
                    "subject_name": sub_name,
                    "faculty": cls.get("faculty", "Unknown Faculty"),
                    "subject_id": cls.get("id") or str(uuid.uuid4())
                }

        # For each subject in the timetable, ensure an attendance record exists
        for sub_lower, sub_info in seen_subjects.items():
            record = await self.repo.get_record_by_subject_name(student_id, sub_info["subject_name"])
            if not record:
                new_record = AttendanceRecordModel(
                    student_id=student_id,
                    subject_id=sub_info["subject_id"],
                    subject_name=sub_info["subject_name"],
                    faculty=sub_info["faculty"],
                    semester=student_profile.get("semester") or int(timetable.get("semester", 1)),
                    section=student_profile.get("section") or timetable.get("section", "A"),
                    department=student_profile.get("department") or timetable.get("department", "General")
                )
                await self.repo.create_record(new_record.to_dict())

    async def get_all_records(self, student_id: str, student_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Syncs and returns all attendance records for a student."""
        await self.sync_timetable_subjects(student_id, student_profile)
        return await self.repo.get_records_by_student(student_id)

    async def recalculate_record_totals(self, record_id: str) -> Optional[Dict[str, Any]]:
        """
        Queries all logs for a record, recalculates conducted/attended classes,
        computes safe leaves and required classes, and updates the database record.
        """
        record = await self.repo.get_record_by_id(record_id)
        if not record:
            return None

        logs = await self.repo.get_logs_by_record_id(record_id)
        
        total_conducted = 0
        total_attended = 0
        
        for log in logs:
            status_val = log.get("status")
            if status_val == "Present":
                total_conducted += 1
                total_attended += 1
            elif status_val == "Absent":
                total_conducted += 1
            # Cancelled, Holiday, and Medical Leave are excluded from totals

        stats = calculate_stats(total_attended, total_conducted, threshold=0.75)

        update_data = {
            "total_conducted": total_conducted,
            "total_attended": total_attended,
            "attendance_percentage": stats["attendancePercentage"],
            "safe_leaves": stats["safeLeaves"],
            "required_classes": stats["requiredClasses"],
            "updated_at": datetime.now(timezone.utc)
        }

        return await self.repo.update_record(record_id, update_data)

    async def get_dashboard_summary(self, student_id: str, student_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Compiles the dashboard summary statistics, recent activity, and today's schedule logging status."""
        records = await self.get_all_records(student_id, student_profile)
        
        total_conducted = 0
        total_attended = 0
        below_threshold_count = 0
        
        best_subject = None
        lowest_subject = None
        
        for rec in records:
            cond = rec.get("total_conducted", 0)
            attn = rec.get("total_attended", 0)
            pct = rec.get("attendance_percentage", 100.0)
            
            total_conducted += cond
            total_attended += attn
            
            if cond > 0:
                if pct < 75.0:
                    below_threshold_count += 1
                    
                # Track best subject
                if best_subject is None or pct > best_subject.get("attendance_percentage", 0.0):
                    best_subject = rec
                elif pct == best_subject.get("attendance_percentage", 0.0) and cond > best_subject.get("total_conducted", 0):
                    best_subject = rec
                    
                # Track lowest subject
                if lowest_subject is None or pct < lowest_subject.get("attendance_percentage", 100.0):
                    lowest_subject = rec
                elif pct == lowest_subject.get("attendance_percentage", 100.0) and cond > lowest_subject.get("total_conducted", 0):
                    lowest_subject = rec

        overall_pct = (total_attended / total_conducted) * 100.0 if total_conducted > 0 else 100.0

        # Fetch recent logs across all records
        record_ids = [rec["_id"] for rec in records]
        all_logs = await self.repo.get_all_logs_for_records(record_ids)
        
        recent_logs_enriched = []
        for log in all_logs[:5]:  # Get recent 5
            # Find matching record to attach subject info
            matched_rec = next((r for r in records if r["_id"] == log["attendance_record_id"]), None)
            recent_logs_enriched.append({
                "id": log["id"],
                "attendance_record_id": log["attendance_record_id"],
                "subject_name": matched_rec["subject_name"] if matched_rec else "Unknown",
                "class_date": log["class_date"],
                "status": log["status"],
                "remarks": log.get("remarks", ""),
                "created_at": log["created_at"].isoformat()
            })

        # Today's Classes and logging status
        today_weekday = get_india_now().strftime("%A")
        timetable = await self.timetable_repo.get_by_student_id(student_id)
        today_classes = []
        
        if timetable and timetable.get("classes"):
            for cls in timetable.get("classes", []):
                if cls.get("day", "").strip().lower() == today_weekday.lower():
                    # Check if logged today
                    sub_name = cls.get("subject", "").strip()
                    matched_rec = next((r for r in records if r["subject_name"].lower() == sub_name.lower()), None)
                    
                    logged_status = None
                    log_id = None
                    if matched_rec:
                        today_log = await self.repo.get_log_by_record_and_date(matched_rec["_id"], get_india_date_str())
                        if today_log:
                            logged_status = today_log.get("status")
                            log_id = today_log.get("id")

                    today_classes.append({
                        "id": cls.get("id"),
                        "subject": sub_name,
                        "faculty": cls.get("faculty", "Unknown"),
                        "start_time": cls.get("start_time"),
                        "end_time": cls.get("end_time"),
                        "classroom": cls.get("classroom"),
                        "building": cls.get("building"),
                        "remarks": cls.get("remarks"),
                        "logged_status": logged_status,
                        "log_id": log_id,
                        "attendance_record_id": matched_rec["_id"] if matched_rec else None
                    })

        # Calculate Weekly and Monthly statistics (conducated vs attended)
        # Find dates corresponding to last 7 days and last 30 days
        india_now = get_india_now().date()
        date_7_days_ago = (india_now - timedelta(days=7)).strftime("%Y-%m-%d")
        date_30_days_ago = (india_now - timedelta(days=30)).strftime("%Y-%m-%d")
        
        weekly_conducted = 0
        weekly_attended = 0
        monthly_conducted = 0
        monthly_attended = 0
        
        for log in all_logs:
            c_date = log["class_date"]
            status_val = log["status"]
            
            # Check 7 days limit
            if c_date >= date_7_days_ago:
                if status_val == "Present":
                    weekly_conducted += 1
                    weekly_attended += 1
                elif status_val == "Absent":
                    weekly_conducted += 1
                    
            # Check 30 days limit
            if c_date >= date_30_days_ago:
                if status_val == "Present":
                    monthly_conducted += 1
                    monthly_attended += 1
                elif status_val == "Absent":
                    monthly_conducted += 1

        weekly_pct = (weekly_attended / weekly_conducted) * 100.0 if weekly_conducted > 0 else 100.0
        monthly_pct = (monthly_attended / monthly_conducted) * 100.0 if monthly_conducted > 0 else 100.0

        def format_sub(rec):
            if not rec:
                return None
            return {
                "subject_id": rec["subject_id"],
                "subject_name": rec["subject_name"],
                "faculty": rec["faculty"],
                "attendance_percentage": rec["attendance_percentage"],
                "total_conducted": rec["total_conducted"],
                "total_attended": rec["total_attended"],
                "safe_leaves": rec["safe_leaves"],
                "required_classes": rec["required_classes"],
                "updated_at": rec["updated_at"]
            }

        return {
            "overall_attendance": round(overall_pct, 2),
            "total_conducted": total_conducted,
            "total_attended": total_attended,
            "best_subject": format_sub(best_subject),
            "lowest_subject": format_sub(lowest_subject),
            "below_threshold_count": below_threshold_count,
            "recent_logs": recent_logs_enriched,
            "today_attendance": today_classes,
            "weekly_summary": {
                "conducted": weekly_conducted,
                "attended": weekly_attended,
                "percentage": round(weekly_pct, 2)
            },
            "monthly_summary": {
                "conducted": monthly_conducted,
                "attended": monthly_attended,
                "percentage": round(monthly_pct, 2)
            }
        }

    async def get_history(self, student_id: str, subject_id: str) -> List[Dict[str, Any]]:
        """Retrieves all logs for a specific subject belonging to the student."""
        record = await self.repo.get_record_by_subject_id(student_id, subject_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance record not found for this subject."
            )
        return await self.repo.get_logs_by_record_id(record["_id"])

    async def create_log(self, student_id: str, student_profile: Dict[str, Any], payload: AttendanceLogCreateRequest) -> Dict[str, Any]:
        """Creates an attendance log for a subject. Ensures validations are passed and totals updated."""
        # 1. Validation - Status
        allowed_statuses = {"Present", "Absent", "Cancelled", "Holiday", "Medical Leave"}
        if payload.status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {payload.status}. Must be one of: {', '.join(allowed_statuses)}"
            )

        # 2. Validation - Future Date
        if is_future_date(payload.class_date):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot log attendance for future dates."
            )

        # 3. Resolve or Create the AttendanceRecord
        record = await self.repo.get_record_by_subject_name(student_id, payload.subject_name)
        if not record:
            # Try to get faculty from timetable
            faculty_name = "Unknown Faculty"
            timetable = await self.timetable_repo.get_by_student_id(student_id)
            if timetable and timetable.get("classes"):
                for cls in timetable["classes"]:
                    if cls.get("subject", "").strip().lower() == payload.subject_name.strip().lower():
                        faculty_name = cls.get("faculty", "Unknown Faculty")
                        break

            new_record = AttendanceRecordModel(
                student_id=student_id,
                subject_id=str(uuid.uuid4()),
                subject_name=payload.subject_name.strip(),
                faculty=faculty_name,
                semester=student_profile.get("semester", 1),
                section=student_profile.get("section", "A"),
                department=student_profile.get("department", "General")
            )
            record = await self.repo.create_record(new_record.to_dict())

        # 4. Validation - Duplicate date check per subject
        existing_log = await self.repo.get_log_by_record_and_date(record["_id"], payload.class_date)
        if existing_log:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Attendance already logged for '{payload.subject_name}' on {payload.class_date}."
            )

        # 5. Insert Log
        new_log = AttendanceLogModel(
            attendance_record_id=record["_id"],
            class_date=payload.class_date,
            status=payload.status,
            remarks=payload.remarks
        )
        await self.repo.create_log(new_log.to_dict())

        # 6. Recalculate totals
        updated_record = await self.recalculate_record_totals(record["_id"])
        if not updated_record:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to recalculate totals after logging attendance."
            )
        return updated_record

    async def update_log(self, student_id: str, log_id: str, payload: AttendanceLogUpdateRequest) -> Dict[str, Any]:
        """Updates an attendance log, verifies ownership, checks validations, and triggers recalculation."""
        log = await self.repo.get_log_by_id(log_id)
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance log not found."
            )

        # Verify ownership
        record = await self.repo.get_record_by_id(log["attendance_record_id"])
        if not record or record["student_id"] != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You do not own this attendance record."
            )

        update_fields = {}
        
        # Validate status if provided
        if payload.status is not None:
            allowed_statuses = {"Present", "Absent", "Cancelled", "Holiday", "Medical Leave"}
            if payload.status not in allowed_statuses:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {payload.status}. Must be one of: {', '.join(allowed_statuses)}"
                )
            update_fields["status"] = payload.status

        # Validate date if provided
        if payload.class_date is not None:
            if is_future_date(payload.class_date):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot update attendance to a future date."
                )
            # Duplicate check
            if payload.class_date != log["class_date"]:
                duplicate = await self.repo.get_log_by_record_and_date(record["_id"], payload.class_date)
                if duplicate:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Attendance already logged for this subject on {payload.class_date}."
                    )
            update_fields["class_date"] = payload.class_date

        if payload.remarks is not None:
            update_fields["remarks"] = payload.remarks

        if update_fields:
            update_fields["updated_at"] = datetime.now(timezone.utc)
            await self.repo.update_log(log_id, update_fields)

        # Recalculate totals
        updated_record = await self.recalculate_record_totals(record["_id"])
        if not updated_record:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to recalculate totals after updating attendance."
            )
        return updated_record

    async def delete_log(self, student_id: str, log_id: str) -> Dict[str, Any]:
        """Deletes an attendance log, verifies ownership, and triggers recalculation."""
        log = await self.repo.get_log_by_id(log_id)
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance log not found."
            )

        # Verify ownership
        record = await self.repo.get_record_by_id(log["attendance_record_id"])
        if not record or record["student_id"] != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You do not own this attendance record."
            )

        # Delete
        await self.repo.delete_log(log_id)

        # Recalculate totals
        updated_record = await self.recalculate_record_totals(record["_id"])
        if not updated_record:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to recalculate totals after deleting attendance."
            )
        return updated_record

    async def get_analytics(self, student_id: str) -> Dict[str, Any]:
        """Generates weekly trends, monthly trends, subject comparisons, and distribution analysis."""
        records = await self.repo.get_records_by_student(student_id)
        record_ids = [r["_id"] for r in records]
        
        all_logs = await self.repo.get_all_logs_for_records(record_ids)
        # Sort oldest first for plotting trends
        all_logs_sorted = sorted(all_logs, key=lambda x: x["class_date"])

        # 1. Status Distribution
        distribution = {"Present": 0, "Absent": 0, "Cancelled": 0, "Holiday": 0, "Medical Leave": 0}
        for log in all_logs:
            status_val = log["status"]
            if status_val in distribution:
                distribution[status_val] += 1

        # 2. Subject Comparison
        subject_comparison = []
        for rec in records:
            subject_comparison.append({
                "subject_name": rec["subject_name"],
                "percentage": rec["attendance_percentage"],
                "conducted": rec["total_conducted"],
                "attended": rec["total_attended"]
            })

        # 3. Weekly trend (last 4 weeks)
        # Group logs by week end date
        india_now = get_india_now().date()
        weekly_trend = []
        
        for w in range(3, -1, -1):
            start_d = india_now - timedelta(days=(w+1)*7)
            end_d = india_now - timedelta(days=w*7)
            
            w_cond = 0
            w_attn = 0
            for log in all_logs:
                c_date = datetime.strptime(log["class_date"], "%Y-%m-%d").date()
                if start_d < c_date <= end_d:
                    if log["status"] == "Present":
                        w_cond += 1
                        w_attn += 1
                    elif log["status"] == "Absent":
                        w_cond += 1
            
            w_pct = (w_attn / w_cond) * 100.0 if w_cond > 0 else 100.0
            label = f"Wk -{w}" if w > 0 else "This Wk"
            weekly_trend.append({
                "label": label,
                "percentage": round(w_pct, 1),
                "conducted": w_cond,
                "attended": w_attn
            })

        # 4. Monthly trend (last 4 months)
        monthly_trend = []
        for m in range(3, -1, -1):
            # approximate 30 days per month
            start_d = india_now - timedelta(days=(m+1)*30)
            end_d = india_now - timedelta(days=m*30)
            
            m_cond = 0
            m_attn = 0
            for log in all_logs:
                c_date = datetime.strptime(log["class_date"], "%Y-%m-%d").date()
                if start_d < c_date <= end_d:
                    if log["status"] == "Present":
                        m_cond += 1
                        m_attn += 1
                    elif log["status"] == "Absent":
                        m_cond += 1
                        
            m_pct = (m_attn / m_cond) * 100.0 if m_cond > 0 else 100.0
            
            # Label as month names
            month_label = (get_india_now() - timedelta(days=m*30)).strftime("%b")
            monthly_trend.append({
                "label": month_label,
                "percentage": round(m_pct, 1),
                "conducted": m_cond,
                "attended": m_attn
            })

        # 5. Average Attendance
        total_conducted = sum(r.get("total_conducted", 0) for r in records)
        total_attended = sum(r.get("total_attended", 0) for r in records)
        avg_pct = (total_attended / total_conducted) * 100.0 if total_conducted > 0 else 100.0

        return {
            "weekly_trend": weekly_trend,
            "monthly_trend": monthly_trend,
            "subject_comparison": subject_comparison,
            "status_distribution": distribution,
            "average_attendance": round(avg_pct, 2)
        }

    # --- AI Context Engine Extension Points ---

    async def getAttendanceSummary(self, student_id: str) -> Dict[str, Any]:
        """AI Extension: Retrieve a concise overview of the student's attendance."""
        records = await self.repo.get_records_by_student(student_id)
        total_conducted = sum(r.get("total_conducted", 0) for r in records)
        total_attended = sum(r.get("total_attended", 0) for r in records)
        overall_pct = (total_attended / total_conducted) * 100.0 if total_conducted > 0 else 100.0
        
        return {
            "overall_attendance_percentage": round(overall_pct, 2),
            "total_subjects_tracked": len(records),
            "total_conducted_classes": total_conducted,
            "total_attended_classes": total_attended
        }

    async def getSubjectAttendance(self, student_id: str, subject_id: str) -> Optional[Dict[str, Any]]:
        """AI Extension: Retrieve detailed stats for a specific subject ID."""
        return await self.repo.get_record_by_subject_id(student_id, subject_id)

    async def getSafeLeaves(self, student_id: str) -> Dict[str, int]:
        """AI Extension: Returns safe leaves remaining for each subject."""
        records = await self.repo.get_records_by_student(student_id)
        return {r["subject_name"]: r.get("safe_leaves", 0) for r in records}

    async def getAttendanceRisk(self, student_id: str) -> List[Dict[str, Any]]:
        """AI Extension: Returns subjects where attendance is below 75% or at risk (below 78%)."""
        records = await self.repo.get_records_by_student(student_id)
        at_risk = []
        for r in records:
            pct = r.get("attendance_percentage", 100.0)
            if pct < 78.0:
                at_risk.append({
                    "subject_name": r["subject_name"],
                    "attendance_percentage": pct,
                    "required_classes_to_clear": r.get("required_classes", 0),
                    "status": "critical" if pct < 75.0 else "warning"
                })
        return at_risk

    async def getRecentAttendance(self, student_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """AI Extension: Returns the most recent attendance logs with subject details."""
        records = await self.repo.get_records_by_student(student_id)
        record_ids = [r["_id"] for r in records]
        logs = await self.repo.get_all_logs_for_records(record_ids)
        
        recent = []
        for log in logs[:limit]:
            matched_rec = next((r for r in records if r["_id"] == log["attendance_record_id"]), None)
            recent.append({
                "subject_name": matched_rec["subject_name"] if matched_rec else "Unknown",
                "class_date": log["class_date"],
                "status": log["status"],
                "remarks": log.get("remarks", "")
            })
        return recent
