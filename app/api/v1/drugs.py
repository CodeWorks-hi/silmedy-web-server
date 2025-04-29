# app/api/v1/drugs.py

from fastapi import APIRouter, Depends
from app.services.drug_service import get_all_drugs
from app.core.dependencies import get_current_user

router = APIRouter()

# 의약품 목록 조회
@router.get("/drugs")
async def read_drugs(user=Depends(get_current_user)):
    return {"drugs": get_all_drugs()}