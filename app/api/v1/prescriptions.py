# app/api/v1/prescriptions.py

from fastapi import APIRouter
from app.services.prescription_service import (
    get_all_prescription_records,
    create_prescription_record,
    update_prescription_record,
    delete_prescription_record
)

router = APIRouter()

@router.get("/prescriptions")
async def read_prescriptions():
    return {"prescriptions": get_all_prescription_records()}

@router.post("/prescriptions")
async def create_prescription(payload: dict):
    return create_prescription_record(payload)

@router.put("/prescriptions/{prescription_id}")
async def update_prescription(prescription_id: str, payload: dict):
    return update_prescription_record(prescription_id, payload)

@router.delete("/prescriptions/{prescription_id}")
async def delete_prescription(prescription_id: str):
    return delete_prescription_record(prescription_id)