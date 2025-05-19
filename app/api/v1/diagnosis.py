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
@router.get(
    "/diagnosis",
    tags=["의사 - 진료 관리"],
    summary="전체 진단 기록을 조회합니다.",
    description="모든 환자에 대한 진단 기록을 조회하는 기능입니다."
)
async def read_all_diagnosis(user=Depends(get_current_user)):
    try:
        return {"diagnosis_records": get_all_diagnosis_records()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 진단 등록
@router.post(
    "/diagnosis",
    tags=["의사 - 진료 관리"],
    summary="새로운 진단 정보를 등록합니다.",
    description="의사가 환자에 대해 새로운 진단 정보를 등록하는 기능입니다."
)
async def create_diagnosis_record(payload: dict, user=Depends(get_current_user)):
    try:
        return create_diagnosis(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 특정 환자의 진단 이력 조회
@router.get(
    "/diagnosis/patient/{patient_id}",
    tags=["의사 - 진료 관리"],
    summary="특정 환자의 진단 이력을 조회합니다.",
    description="환자 ID를 기반으로 해당 환자의 진단 이력을 조회하는 기능입니다."
)
async def read_patient_diagnosis(patient_id: str, user=Depends(get_current_user)):
    try:
        return {"diagnosis_records": get_diagnosis_by_patient_id(patient_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))