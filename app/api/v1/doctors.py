# app/api/v1/doctors.py

from fastapi import APIRouter, Depends
from app.services.doctor_service import (
    get_all_doctors,
    create_doctor,
    update_doctor,
    delete_doctor
)
from app.core.dependencies import get_current_user

router = APIRouter()

# 의사 목록 조회
@router.get("/doctors")
async def read_doctors(user=Depends(get_current_user)):
    return {"doctors": get_all_doctors()}

# 의사 등록
@router.post("/doctors")
async def create_new_doctor(payload: dict, user=Depends(get_current_user)):
    return create_doctor(payload)

# 의사 정보 수정
@router.put("/doctors/{license_number}")
async def update_doctor_info(license_number: str, payload: dict, user=Depends(get_current_user)):
    return update_doctor(license_number, payload)

# 의사 삭제
@router.delete("/doctors/{license_number}")
async def delete_doctor_info(license_number: str, user=Depends(get_current_user)):
    return delete_doctor(license_number)