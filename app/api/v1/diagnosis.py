# app/api/v1/diagnosis.py

from fastapi import APIRouter, Depends
from app.services.diagnosis_service import (
    get_all_diagnosis_records,
    create_diagnosis_record,
    get_diagnosis_by_patient
)
from app.core.dependencies import get_current_user

router = APIRouter()

# 진단 기록 전체 조회
@router.get("/diagnosis-records")
async def read_diagnosis_records(user=Depends(get_current_user)):
    return {"diagnosis_records": get_all_diagnosis_records()}

# 진단 기록 생성
@router.post("/diagnosis-records")
async def create_diagnosis(payload: dict, user=Depends(get_current_user)):
    return create_diagnosis_record(payload)

# 특정 환자 진단 이력 조회
@router.get("/diagnosis-records/patient/{patient_id}")
async def get_diagnosis_by_patient_id(patient_id: str, user=Depends(get_current_user)):
    return {"diagnosis_records": get_diagnosis_by_patient(patient_id)}