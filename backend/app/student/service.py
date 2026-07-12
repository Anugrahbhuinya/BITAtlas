import os
from datetime import datetime, timezone
from fastapi import HTTPException, status, UploadFile
from typing import Dict, Any, List, Optional
from bson import ObjectId

from app.student.repository import StudentRepository
from app.auth.password_service import PasswordService
from app.student.schemas import (
    StudentRegisterRequest,
    StudentProfileUpdateRequest,
    AdminStudentUpdateRequest
)
from app.student.validators import validate_profile_picture, generate_profile_picture_filename

class RegistrationService:
    def __init__(self, student_repo: StudentRepository):
        self.student_repo = student_repo

    async def register_student(self, request: StudentRegisterRequest) -> dict:
        """
        Validates details, ensures uniqueness, hashes password, and saves the student.
        """
        # Ensure email uniqueness
        existing_email = await self.student_repo.get_by_email(request.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered"
            )

        # Ensure roll number uniqueness
        existing_roll = await self.student_repo.get_by_roll_number(request.roll_number)
        if existing_roll:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Roll number is already registered"
            )

        # Hash the plain text password using bcrypt
        password_hash = PasswordService.hash_password(request.password)

        # Build database document
        student_data = request.dict(exclude={"password"})
        student_data.update({
            "password_hash": password_hash,
            "role": "student",
            "status": "active",
            "is_deleted": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        })

        saved_student = await self.student_repo.create(student_data)
        saved_student["_id"] = str(saved_student["_id"])

        # Auto-seed default preferences
        try:
            from app.student_preferences.repository import PreferencesRepository
            from app.student_preferences.service import PreferencesService
            from app.core.database import get_database
            pref_db = get_database()
            pref_repo = PreferencesRepository(pref_db)
            pref_service = PreferencesService(pref_repo)
            await pref_service.create_default_preferences(saved_student["_id"])
        except Exception as e:
            # Fallback warning
            print(f"Warning: Failed to seed student default preferences: {e}")

        return saved_student

class ProfileService:
    def __init__(self, student_repo: StudentRepository):
        self.student_repo = student_repo

    async def get_profile(self, student_id: str) -> dict:
        """
        Retrieves a student profile.
        """
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found"
            )
        student["_id"] = str(student["_id"])
        return student

    async def update_student_profile(self, student_id: str, request: StudentProfileUpdateRequest) -> dict:
        """
        Updates the student's editable profile fields (name, email) with uniqueness checks.
        """
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found"
            )

        # Check email uniqueness if email has changed
        email_new = request.email.strip().lower()
        if student.get("email") != email_new:
            conflict = await self.student_repo.get_by_email(email_new)
            if conflict:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email address is already in use by another user"
                )

        update_data = {
            "name": request.name.strip(),
            "email": email_new,
            "updated_at": datetime.now(timezone.utc)
        }

        updated = await self.student_repo.update_profile(student_id, update_data)
        updated["_id"] = str(updated["_id"])
        return updated

    async def update_profile_picture(self, student_id: str, file: UploadFile) -> str:
        """
        Validates, saves the profile picture, deletes the previous image, and returns the path.
        """
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found"
            )

        # 1. Validate file extension and type
        ext = validate_profile_picture(file)

        # 2. Validate file size (under 5MB)
        file_content = await file.read()
        if len(file_content) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds maximum limit of 5 MB."
            )

        # Generate unique filename
        filename = generate_profile_picture_filename(student_id, ext)
        relative_path = f"/uploads/profile_pictures/{filename}"
        absolute_dir = os.path.join("uploads", "profile_pictures")
        absolute_path = os.path.join(absolute_dir, filename)

        # 3. Delete old profile picture if exists
        old_pic = student.get("profile_picture")
        if old_pic and old_pic.startswith("/uploads/profile_pictures/"):
            old_filename = old_pic.split("/")[-1]
            old_filepath = os.path.join(absolute_dir, old_filename)
            if os.path.exists(old_filepath):
                try:
                    os.remove(old_filepath)
                except Exception as e:
                    print(f"Error removing old profile picture: {e}")

        # 4. Save new file
        try:
            with open(absolute_path, "wb") as f:
                f.write(file_content)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save profile picture on server: {str(e)}"
            )

        # 5. Save to database
        await self.student_repo.update_profile(student_id, {
            "profile_picture": relative_path,
            "updated_at": datetime.now(timezone.utc)
        })

        return relative_path

    async def change_student_password(self, student_id: str, current_pwd: str, new_pwd: str) -> bool:
        """
        Modifies password after validating the existing password.
        """
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found"
            )

        # Verify old password
        if not PasswordService.verify_password(current_pwd, student.get("password_hash", "")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password"
            )

        # Hash new password
        new_hash = PasswordService.hash_password(new_pwd)
        
        await self.student_repo.update_password(student_id, new_hash)
        return True

class StudentManagementService:
    def __init__(self, student_repo: StudentRepository):
        self.student_repo = student_repo

    async def list_students(
        self,
        search: Optional[str] = None,
        department: Optional[str] = None,
        program: Optional[str] = None,
        year: Optional[int] = None,
        semester: Optional[int] = None,
        page: int = 1,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Generates matching filters and retrieves a paginated student registry.
        """
        query: Dict[str, Any] = {}
        
        if search:
            search_clean = search.strip()
            query["$or"] = [
                {"name": {"$regex": search_clean, "$options": "i"}},
                {"roll_number": {"$regex": search_clean, "$options": "i"}},
                {"email": {"$regex": search_clean, "$options": "i"}}
            ]
            
        if department:
            query["department"] = department
        if program:
            query["program"] = program
        if year is not None:
            query["year"] = year
        if semester is not None:
            query["semester"] = semester

        skip = (page - 1) * limit
        
        students = await self.student_repo.list_students(query, skip=skip, limit=limit)
        total = await self.student_repo.count_students(query.copy()) # Copy query to prevent mutations
        
        # Serialize list
        serialized_students = []
        for s in students:
            s_copy = s.copy()
            s_copy["_id"] = str(s_copy["_id"])
            if "password_hash" in s_copy:
                del s_copy["password_hash"]
            serialized_students.append(s_copy)

        pages = (total + limit - 1) // limit if total > 0 else 1

        return {
            "students": serialized_students,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages
        }

    async def get_student_by_id(self, student_id: str) -> dict:
        """
        Fetch a student profile by ID.
        """
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found"
            )
        student["_id"] = str(student["_id"])
        if "password_hash" in student:
            del student["password_hash"]
        return student

    async def update_student_academics(self, student_id: str, request: AdminStudentUpdateRequest) -> dict:
        """
        Administrative updates for a student details, verifying uniqueness checks.
        """
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found"
            )

        # Verify email conflict
        email_new = request.email.strip().lower()
        if student.get("email") != email_new:
            conflict = await self.student_repo.get_by_email(email_new)
            if conflict:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email is already in use by another user"
                )

        # Verify roll number conflict
        roll_new = request.roll_number.strip()
        if student.get("roll_number") != roll_new:
            conflict = await self.student_repo.get_by_roll_number(roll_new)
            if conflict:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Roll number is already in use by another user"
                )

        update_data = {
            "roll_number": roll_new,
            "name": request.name.strip(),
            "email": email_new,
            "department": request.department.strip(),
            "program": request.program.strip(),
            "year": request.year,
            "semester": request.semester,
            "section": request.section.strip(),
            "status": request.status,
            "updated_at": datetime.now(timezone.utc)
        }

        updated = await self.student_repo.update(student_id, update_data)
        updated["_id"] = str(updated["_id"])
        if "password_hash" in updated:
            del updated["password_hash"]
        return updated

    async def update_student_status(self, student_id: str, status_str: str) -> dict:
        """
        Administratively change student status.
        """
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found"
            )

        updated = await self.student_repo.update_status(student_id, status_str)
        updated["_id"] = str(updated["_id"])
        if "password_hash" in updated:
            del updated["password_hash"]
        return updated

    async def reset_student_password(self, student_id: str, new_password: str) -> bool:
        """
        Administrative password reset override.
        """
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found"
            )

        new_hash = PasswordService.hash_password(new_password)
        await self.student_repo.update_password(student_id, new_hash)
        return True

    async def soft_delete_student(self, student_id: str) -> bool:
        """
        Soft deletes the student record.
        """
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found"
            )

        return await self.student_repo.soft_delete(student_id)
