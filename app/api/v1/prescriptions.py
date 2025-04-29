# app/api/v1/prescriptions.py

from fastapi import APIRouter, Depends, HTTPException
from app.services.prescription_service import create_prescription
from app.core.dependencies import get_current_user

router = APIRouter()

# 처방전 등록 API
@router.post("/prescriptions", summary="처방전 등록", description="특정 진단 ID에 대한 처방전을 생성합니다.")
async def register_prescription(payload: dict, user=Depends(get_current_user)):
    try:
        return create_prescription(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))