from fastapi import APIRouter, HTTPException
from app.services.doctor_service import (
    get_all_doctors,
    delete_doctor_by_license,
    update_doctor_by_license,
    register_doctor
)

router = APIRouter()

@router.get("/doctors")
async def list_doctors():
    return {"doctors": get_all_doctors()}

@router.delete("/delete/doctor/{license_number}")
async def delete_doctor(license_number: str):
    delete_doctor_by_license(license_number)
    return {"message": "삭제 완료"}

@router.put("/update/doctor/{license_number}")
async def update_doctor(license_number: str, payload: dict):
    update_doctor_by_license(license_number, payload)
    return {"message": "수정 완료"}

@router.post("/register/doctor")
async def register_doctor_api(payload: dict):
    return register_doctor(payload)