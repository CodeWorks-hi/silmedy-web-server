# app/api/v1/drugs.py

from fastapi import APIRouter, Depends
from app.services.drug_service import get_all_drugs
from app.core.dependencies import get_current_user

router = APIRouter()

# 의약품 목록 조회
@router.get(
    "/drugs",
    tags=["의사 - 처방 관리"],
    summary="의약품 목록을 조회합니다.",
    description="처방을 위해 사용 가능한 의약품 전체 목록을 조회하는 기능입니다."
)
async def read_drugs(user=Depends(get_current_user)):
    return {"drugs": get_all_drugs()}