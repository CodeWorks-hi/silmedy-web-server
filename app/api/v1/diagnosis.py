from fastapi import APIRouter
from app.services.diagnosis_service import (
    get_all_diagnosis_records,
    create_diagnosis,
    get_diagnosis_by_patient_id
)

router = APIRouter()

@router.get("/diagnosis-records")
async def list_diagnosis_records():
    return {"diagnosis_records": get_all_diagnosis_records()}

@router.post("/diagnosis/create")
async def create_diagnosis_api(payload: dict):
    return create_diagnosis(payload)

@router.get("/diagnosis/patient/{patient_id}")
async def diagnosis_by_patient(patient_id: str):
    return {"diagnosis": get_diagnosis_by_patient_id(patient_id)}