from fastapi import APIRouter
from app.services.drug_service import get_all_drugs

router = APIRouter()

@router.get("/drugs")
async def list_drugs():
    return {"drugs": get_all_drugs()}