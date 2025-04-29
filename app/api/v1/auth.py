# app/api/v1/auth.py

from fastapi import APIRouter, Depends
from app.services.auth_service import (
    login_user,
    register_user,
    get_current_user_info
)
from app.core.dependencies import get_current_user

router = APIRouter()

@router.post("/login")
async def login(payload: dict):
    return login_user(payload)

@router.post("/register")
async def register(payload: dict):
    return register_user(payload)

@router.get("/me")
async def get_user_info(user=Depends(get_current_user)):
    return get_current_user_info(user)