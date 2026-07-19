import time
import logging
from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse
from app.services.faculty_service import FacultyService
from app.schemas.faculty import (
    FacultyListResponse,
    FacultySingleResponse,
    DepartmentResponse,
    StatsResponse,
    ErrorResponse
)

logger = logging.getLogger("faculty_api")
router = APIRouter(prefix="/api/faculty", tags=["Faculty Directory"])

@router.get("", response_model=FacultyListResponse, summary="Get all faculty members", description="Retrieves a list of all normalized faculty members in the directory.")
def get_all_faculty():
    start_time = time.time()
    try:
        data = FacultyService.get_all()
        duration = time.time() - start_time
        logger.info(f"GET /api/faculty - Records: {len(data)} - Duration: {duration:.4f}s")
        return {
            "success": True,
            "data": data,
            "count": len(data),
            "message": "Faculty retrieved successfully"
        }
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"GET /api/faculty - Error: {str(e)} - Duration: {duration:.4f}s", exc_info=False)
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "An internal server error occurred."}
        )

@router.get("/search", response_model=FacultyListResponse, responses={400: {"model": ErrorResponse}}, summary="Search faculty members", description="Searches faculty members by name, email, department, or research interests using case-insensitive partial matching.")
def search_faculty(q: str = Query(..., description="Query string to search name, email, interests, or department")):
    start_time = time.time()
    try:
        if not q or not q.strip():
            duration = time.time() - start_time
            logger.warning(f"GET /api/faculty/search - Empty query - Duration: {duration:.4f}s")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": "Query parameter 'q' must not be empty"}
            )
            
        data = FacultyService.search(q)
        duration = time.time() - start_time
        logger.info(f"GET /api/faculty/search?q={q} - Records: {len(data)} - Duration: {duration:.4f}s")
        return {
            "success": True,
            "data": data,
            "count": len(data),
            "message": "Faculty retrieved successfully"
        }
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"GET /api/faculty/search?q={q} - Error: {str(e)} - Duration: {duration:.4f}s", exc_info=False)
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "An internal server error occurred."}
        )

@router.get("/departments", response_model=DepartmentResponse, summary="Get all departments", description="Retrieves a sorted list of all unique normalized department names.")
def get_departments():
    start_time = time.time()
    try:
        data = FacultyService.get_departments()
        duration = time.time() - start_time
        logger.info(f"GET /api/faculty/departments - Departments: {len(data)} - Duration: {duration:.4f}s")
        return {
            "success": True,
            "data": data,
            "count": len(data),
            "message": "Departments retrieved successfully"
        }
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"GET /api/faculty/departments - Error: {str(e)} - Duration: {duration:.4f}s", exc_info=False)
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "An internal server error occurred."}
        )

@router.get("/department/{department}", response_model=FacultyListResponse, responses={400: {"model": ErrorResponse}}, summary="Get faculty by department", description="Retrieves all faculty members belonging to a specific department.")
def get_by_department(department: str):
    start_time = time.time()
    try:
        if not department or not department.strip():
            duration = time.time() - start_time
            logger.warning(f"GET /api/faculty/department - Empty department param - Duration: {duration:.4f}s")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": "Department parameter must not be empty"}
            )
            
        data = FacultyService.get_by_department(department)
        duration = time.time() - start_time
        logger.info(f"GET /api/faculty/department/{department} - Records: {len(data)} - Duration: {duration:.4f}s")
        return {
            "success": True,
            "data": data,
            "count": len(data),
            "message": "Faculty retrieved successfully"
        }
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"GET /api/faculty/department/{department} - Error: {str(e)} - Duration: {duration:.4f}s", exc_info=False)
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "An internal server error occurred."}
        )

@router.get("/research", response_model=FacultyListResponse, responses={400: {"model": ErrorResponse}}, summary="Get faculty by research interest", description="Retrieves faculty members matching a specific research interest.")
def get_by_research_interest(interest: str = Query(..., description="Query string to search inside research interests")):
    start_time = time.time()
    try:
        if not interest or not interest.strip():
            duration = time.time() - start_time
            logger.warning(f"GET /api/faculty/research - Empty interest param - Duration: {duration:.4f}s")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": "Interest parameter must not be empty"}
            )
            
        data = FacultyService.get_by_research_interest(interest)
        duration = time.time() - start_time
        logger.info(f"GET /api/faculty/research?interest={interest} - Records: {len(data)} - Duration: {duration:.4f}s")
        return {
            "success": True,
            "data": data,
            "count": len(data),
            "message": "Faculty retrieved successfully"
        }
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"GET /api/faculty/research?interest={interest} - Error: {str(e)} - Duration: {duration:.4f}s", exc_info=False)
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "An internal server error occurred."}
        )

@router.get("/stats", response_model=StatsResponse, summary="Get directory stats", description="Retrieves statistical metrics of the faculty directory.")
def get_stats():
    start_time = time.time()
    try:
        data = FacultyService.get_stats()
        duration = time.time() - start_time
        logger.info(f"GET /api/faculty/stats - Duration: {duration:.4f}s")
        return {
            "success": True,
            "data": data,
            "message": "Statistics retrieved successfully"
        }
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"GET /api/faculty/stats - Error: {str(e)} - Duration: {duration:.4f}s", exc_info=False)
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "An internal server error occurred."}
        )

@router.get("/{id}", response_model=FacultySingleResponse, responses={404: {"model": ErrorResponse}}, summary="Get faculty member by ID", description="Retrieves detailed information of a single faculty member by their unique ID.")
def get_faculty_by_id(id: str):
    start_time = time.time()
    try:
        member = FacultyService.get_by_id(id)
        duration = time.time() - start_time
        if not member:
            logger.warning(f"GET /api/faculty/{id} - Not Found - Duration: {duration:.4f}s")
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"success": False, "message": "Faculty not found"}
            )
            
        logger.info(f"GET /api/faculty/{id} - Found: {member['name']} - Duration: {duration:.4f}s")
        return {
            "success": True,
            "data": member,
            "message": "Faculty retrieved successfully"
        }
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"GET /api/faculty/{id} - Error: {str(e)} - Duration: {duration:.4f}s", exc_info=False)
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "An internal server error occurred."}
        )
