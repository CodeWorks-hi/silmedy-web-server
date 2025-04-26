from fastapi import APIRouter
from app.services.patient_service import get_all_patients

router = APIRouter()

@router.get("/patients")
async def list_patients():
    return {"patients": get_all_patients()}