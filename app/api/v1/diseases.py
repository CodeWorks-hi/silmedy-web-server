# app/api/v1/diseases.py

from fastapi import APIRouter, Depends
from app.services.disease_service import get_all_diseases
from app.core.dependencies import get_current_user

router = APIRouter()

# 질병 코드 전체 조회
@router.get("/diseases")
async def read_diseases(user=Depends(get_current_user)):
    return {"diseases": get_all_diseases()}