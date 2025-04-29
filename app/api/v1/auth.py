# app/api/v1/auth.py

from fastapi import APIRouter
from app.services.auth_service import login_user

router = APIRouter()

# 로그인 (doctor / admin 구분)
@router.post("/login")
async def login(payload: dict):
    return login_user(payload)