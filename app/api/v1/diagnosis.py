# app/api/v1/diagnosis.py

from fastapi import APIRouter, Depends, HTTPException
from app.services.diagnosis_service import (
    get_all_diagnosis_records,
    create_diagnosis,
    get_diagnosis_by_patient_id
)
from app.core.dependencies import get_current_user

router = APIRouter()

# 전체 진단 기록 조회
@router.get("/diagnosis")
async def read_all_diagnosis(user=Depends(get_current_user)):
    try:
        return {"diagnosis_records": get_all_diagnosis_records()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 진단 등록
@router.post("/diagnosis")
async def create_diagnosis_record(payload: dict, user=Depends(get_current_user)):
    try:
        return create_diagnosis(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 특정 환자의 진단 이력 조회
@router.get("/diagnosis/patient/{patient_id}")
async def read_patient_diagnosis(patient_id: str, user=Depends(get_current_user)):
    try:
        return {"diagnosis_records": get_diagnosis_by_patient_id(patient_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))