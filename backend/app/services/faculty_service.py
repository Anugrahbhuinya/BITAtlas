import os
import json
import re
from typing import List, Dict, Any, Optional

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.normpath(os.path.join(CURRENT_DIR, "..", "data", "faculty", "faculty_directory.json"))

def normalize_whitespace(s: str) -> str:
    if not s:
        return ""
    return " ".join(s.split())

class FacultyService:
    _cached_data: Optional[List[Dict[str, Any]]] = None

    @classmethod
    def _load_data(cls) -> List[Dict[str, Any]]:
        """Loads and caches the faculty directory JSON dataset in memory."""
        if cls._cached_data is None:
            if not os.path.exists(JSON_PATH):
                raise FileNotFoundError(f"Faculty directory JSON file not found at: {JSON_PATH}")
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                cls._cached_data = json.load(f)
        return cls._cached_data

    @classmethod
    def get_all(cls) -> List[Dict[str, Any]]:
        """Returns all faculty members."""
        return cls._load_data()

    @classmethod
    def get_by_id(cls, faculty_id: str) -> Optional[Dict[str, Any]]:
        """Returns a single faculty member by ID, or None if not found."""
        data = cls._load_data()
        # Direct lookup (IDs are unique)
        for member in data:
            if member.get("id") == faculty_id:
                return member
        return None

    @classmethod
    def search(cls, query: str) -> List[Dict[str, Any]]:
        """
        Searches faculty members by name, email, department, designation, office, building, or research interests.
        Case-insensitive, whitespace tolerant, and partial matching.
        """
        if not query or not query.strip():
            return []
            
        data = cls._load_data()
        q_norm = normalize_whitespace(query.lower())
        
        matches = []
        for m in data:
            name = normalize_whitespace(m.get("name", "").lower())
            email = m.get("email", "").lower()
            dept = normalize_whitespace(m.get("department", "").lower())
            designation = normalize_whitespace(m.get("designation", "").lower()) if m.get("designation") else ""
            office = normalize_whitespace(m.get("office", "").lower()) if m.get("office") else ""
            building = normalize_whitespace(m.get("building", "").lower()) if m.get("building") else ""
            interests = [normalize_whitespace(i.lower()) for i in m.get("research_interests", [])]
            
            if (q_norm in name or 
                q_norm in email or 
                q_norm in dept or 
                q_norm in designation or
                q_norm in office or
                q_norm in building or
                any(q_norm in interest for interest in interests)):
                matches.append(m)
                
        return matches

    @classmethod
    def get_departments(cls) -> List[str]:
        """Returns a sorted list of all unique normalized department names."""
        data = cls._load_data()
        depts = set(m.get("department") for m in data if m.get("department"))
        return sorted(list(depts))

    @classmethod
    def get_by_department(cls, department: str) -> List[Dict[str, Any]]:
        """Returns all faculty members belonging to a specific department (case-insensitive)."""
        if not department or not department.strip():
            return []
            
        data = cls._load_data()
        target_dept = normalize_whitespace(department.lower())
        
        matches = []
        for m in data:
            dept = normalize_whitespace(m.get("department", "").lower())
            if target_dept == dept:
                matches.append(m)
        return matches

    @classmethod
    def get_by_research_interest(cls, interest: str) -> List[Dict[str, Any]]:
        """Returns all faculty members matching a specific research interest (case-insensitive substring match)."""
        if not interest or not interest.strip():
            return []
            
        data = cls._load_data()
        target_interest = normalize_whitespace(interest.lower())
        
        matches = []
        for m in data:
            interests = [normalize_whitespace(i.lower()) for i in m.get("research_interests", [])]
            if any(target_interest in i for i in interests):
                matches.append(m)
        return matches

    @classmethod
    def get_stats(cls) -> Dict[str, int]:
        """Returns key statistical indicators of the faculty directory."""
        data = cls._load_data()
        depts = set(m.get("department") for m in data if m.get("department"))
        
        faculty_with_phone = sum(1 for m in data if m.get("phone"))
        faculty_with_email = sum(1 for m in data if m.get("email"))
        
        return {
            "total_faculty": len(data),
            "departments": len(depts),
            "faculty_with_phone": faculty_with_phone,
            "faculty_with_email": faculty_with_email
        }
