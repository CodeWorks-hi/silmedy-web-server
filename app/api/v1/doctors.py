# app/api/v1/doctors.py

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from app.services.doctor_service import (
    get_all_doctors,
    create_doctor,
    update_doctor,
    delete_doctor,
    set_profile_url
)
from app.core.dependencies import get_current_admin

router = APIRouter()

# 의사 목록 조회
@router.get("/doctors")
async def read_doctors(admin=Depends(get_current_admin)):
    return {"doctors": get_all_doctors()}

# 의사 등록
@router.post("/doctors")
async def create_new_doctor(payload: dict, admin=Depends(get_current_admin)):
    return create_doctor(payload)

# 의사 정보 수정
@router.patch("/doctors/{license_number}")
async def update_doctor_info(license_number: str, payload: dict, admin=Depends(get_current_admin)):
    return update_doctor(license_number, payload)

# 의사 삭제
@router.delete("/doctors/{license_number}")
async def delete_doctor_info(license_number: str, admin=Depends(get_current_admin)):
    return delete_doctor(license_number)



@router.post("/doctors/{license_number}/profile")
async def upload_doctor_profile(
    license_number: str,
    file: UploadFile = File(...),
    admin=Depends(get_current_admin)
) -> dict:
    # 1) 파일 읽어서 bytes로 변환
    content = await file.read()
    try:
        url = set_profile_url(license_number, content, file.content_type)
    except Exception as e:
        raise HTTPException(400, str(e))
    return {"profile_url": url}