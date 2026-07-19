from pydantic import BaseModel
from typing import Dict, Any

class ResolvedFaculty(BaseModel):
    faculty: Dict[str, Any]
    score: float
    normalized_name: str
