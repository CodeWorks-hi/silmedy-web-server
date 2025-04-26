from fastapi import APIRouter, HTTPException
from app.services.auth_service import doctor_login, admin_login

router = APIRouter()

@router.post("/login/doctor")
async def login_doctor(payload: dict):
    return doctor_login(payload)

@router.post("/login/admin")
async def login_admin(payload: dict):
    return admin_login(payload)