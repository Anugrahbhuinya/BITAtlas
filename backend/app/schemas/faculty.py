from pydantic import BaseModel, Field
from typing import List, Optional

class FacultySummary(BaseModel):
    id: str = Field(..., description="Unique deterministic identifier of the faculty member")
    name: str = Field(..., description="Full name of the faculty member")
    designation: Optional[str] = Field(None, description="Faculty designation or academic rank")
    department: str = Field(..., description="Normalized department name")
    email: str = Field(..., description="Validated primary email address")
    phone: Optional[str] = Field(None, description="Normalized phone or mobile number")
    research_interests: List[str] = Field(default_factory=list, description="List of research fields or interests")

class FacultyResponse(FacultySummary):
    office: Optional[str] = Field(None, description="Office location details")
    building: Optional[str] = Field(None, description="Building name")
    office_hours: Optional[str] = Field(None, description="Available office consultation hours")
    website: Optional[str] = Field(None, description="Personal or scholar website URL")
    photo: Optional[str] = Field(None, description="Profile photo URL or path")

class FacultyListResponse(BaseModel):
    success: bool = Field(True, description="Indicating if the operation was successful")
    data: List[FacultyResponse] = Field(default_factory=list, description="List of faculty records")
    count: int = Field(0, description="Total number of returned records")
    message: str = Field("Faculty retrieved successfully", description="API response status message")

class FacultySingleResponse(BaseModel):
    success: bool = Field(True, description="Indicating if the operation was successful")
    data: Optional[FacultyResponse] = Field(None, description="Detailed faculty record")
    message: str = Field("Faculty retrieved successfully", description="API response status message")

class DepartmentResponse(BaseModel):
    success: bool = Field(True, description="Indicating if the operation was successful")
    data: List[str] = Field(default_factory=list, description="List of normalized departments")
    count: int = Field(0, description="Total number of departments")
    message: str = Field("Departments retrieved successfully", description="API response status message")

class StatsData(BaseModel):
    total_faculty: int = Field(..., description="Total count of unique faculty members")
    departments: int = Field(..., description="Total count of unique departments")
    faculty_with_phone: int = Field(..., description="Count of faculty with a listed phone number")
    faculty_with_email: int = Field(..., description="Count of faculty with a listed email address")

class StatsResponse(BaseModel):
    success: bool = Field(True, description="Indicating if the operation was successful")
    data: StatsData = Field(..., description="Directory statistical indicators")
    message: str = Field("Statistics retrieved successfully", description="API response status message")

class ErrorResponse(BaseModel):
    success: bool = Field(False, description="Indicating a failed operation")
    message: str = Field(..., description="Detailed description of the error")
