# app/api/v1/hospitals.py

from fastapi import APIRouter, Depends
from app.services.hospital_service import get_all_hospitals
from app.core.dependencies import get_current_user

router = APIRouter()

# 수정된 hospitals.py
@router.get(
    "/hospitals",
    tags=["공통 - 로그인"],
    summary="병원 목록을 조회합니다.",
    description="전체 병원 목록을 조회하는 기능입니다. 일반 사용자 또는 관리자 모두 사용할 수 있습니다."
)
async def read_hospitals():
    return {"hospitals": get_all_hospitals()}