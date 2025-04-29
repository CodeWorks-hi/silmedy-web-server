# app/api/v1/hospitals.py

from fastapi import APIRouter, Depends
from app.services.hospital_service import get_all_hospitals
from app.core.dependencies import get_current_user

router = APIRouter()

# 수정된 hospitals.py
@router.get("/hospitals")
async def read_hospitals():
    return {"hospitals": get_all_hospitals()}