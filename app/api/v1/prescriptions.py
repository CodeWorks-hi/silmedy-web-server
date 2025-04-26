from fastapi import APIRouter
from app.services.prescription_service import (
    get_all_prescription_records,
    create_prescription
)

router = APIRouter()

@router.get("/prescription_records")
async def list_prescription_records():
    return {"prescription_records": get_all_prescription_records()}

@router.post("/prescriptions/create")
async def create_prescription_api(payload: dict):
    return create_prescription(payload)