# app/api/v1/common.py

from fastapi import APIRouter, Depends
from app.services.common_service import (
    get_departments,
    get_symptom_parts,
    get_symptom_types
)
from app.core.dependencies import get_current_user

router = APIRouter()

# 공통 - 진료과 목록 조회
@router.get("/departments")
async def read_departments(user=Depends(get_current_user)):
    return {"departments": get_departments()}

# 공통 - 증상 부위 목록 조회
@router.get("/symptom-parts")
async def read_symptom_parts(user=Depends(get_current_user)):
    return {"symptom_parts": get_symptom_parts()}

# 공통 - 증상 종류 목록 조회
@router.get("/symptom-types")
async def read_symptom_types(user=Depends(get_current_user)):
    return {"symptom_types": get_symptom_types()}