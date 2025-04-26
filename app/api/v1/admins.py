from fastapi import APIRouter, HTTPException
from app.services.admin_service import (
    get_all_admins,
    delete_admin_by_id,
    update_admin_by_id,
    register_admin
)

router = APIRouter()

@router.get("/admins")
async def list_admins():
    return {"admins": get_all_admins()}

@router.delete("/delete/admin/{admin_id}")
async def delete_admin(admin_id: str):
    delete_admin_by_id(admin_id)
    return {"message": "삭제 완료"}

@router.put("/update/admin/{admin_id}")
async def update_admin(admin_id: str, payload: dict):
    update_admin_by_id(admin_id, payload)
    return {"message": "수정 완료"}

@router.post("/register/admin")
async def register_admin_api(payload: dict):
    return register_admin(payload)