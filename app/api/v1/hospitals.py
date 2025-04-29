# app/api/v1/hospitals.py

from fastapi import APIRouter, Depends
from app.services.hospital_service import get_all_hospitals
from app.core.dependencies import get_current_user

router = APIRouter()

# 병원 목록 조회
@router.get("/hospitals")
async def read_hospitals(user=Depends(get_current_user)):
    return {"hospitals": get_all_hospitals()}