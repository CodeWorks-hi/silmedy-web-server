# app/api/v1/auth.py

from fastapi import APIRouter
from app.services.auth_service import login_user

router = APIRouter()

# 로그인 엔드포인트 (doctor / admin 공통)
@router.post("/login")
async def login(payload: dict):
    return login_user(payload)