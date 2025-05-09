from pydantic import BaseModel
from typing import Optional, Dict, List

class Doctor(BaseModel):
    hospital_id: int
    name: str
    email: str
    password: str
    department: str
    contact: str
    gender: Optional[str] = None
    profile_url: Optional[str] = None
    availability: Optional[Dict[str, str]] = {}
    created_at: Optional[str] = None