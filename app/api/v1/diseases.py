# app/api/v1/diseases.py

from fastapi import APIRouter, Depends
from app.services.disease_service import get_all_diseases
from app.core.dependencies import get_current_user

router = APIRouter()

# 질병 코드 전체 조회
@router.get(
    "/diseases",
    tags=["의사 - 진료 관리"],
    summary="질병 코드를 전체 조회합니다.",
    description="진단에 사용되는 질병 코드 목록을 전체 조회하는 기능입니다."
)
async def read_diseases(user=Depends(get_current_user)):
    return {"diseases": get_all_diseases()}