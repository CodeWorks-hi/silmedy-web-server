# app/api/v1/patients.py

from fastapi import APIRouter, Depends
from app.services.patient_service import (
    get_all_patients,
    create_patient,
    update_patient,
    delete_patient
)
from app.core.dependencies import get_current_user

router = APIRouter()

# 환자 목록 조회
@router.get("/patients")
async def read_patients(user=Depends(get_current_user)):
    return {"patients": get_all_patients()}

# 환자 등록
@router.post("/patients")
async def create_new_patient(payload: dict, user=Depends(get_current_user)):
    return create_patient(payload)

# 환자 정보 수정
@router.put("/patients/{patient_id}")
async def update_patient_info(patient_id: str, payload: dict, user=Depends(get_current_user)):
    return update_patient(patient_id, payload)

# 환자 삭제
@router.delete("/patients/{patient_id}")
async def delete_patient_info(patient_id: str, user=Depends(get_current_user)):
    return delete_patient(patient_id)