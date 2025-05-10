# app/api/v1/doctors.py
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from app.services.doctor_service import (
    get_doctors_by_hospital,
    create_doctor,
    update_doctor,
    delete_doctor,
    upload_doctor_profile_service  # 서비스 함수로 변경
)
from app.core.dependencies import get_current_admin
from botocore.exceptions import ClientError

router = APIRouter()

@router.get("/doctors")
async def read_doctors(admin=Depends(get_current_admin)):
    hospital_id = admin["hospital_id"]
    return {"doctors": get_doctors_by_hospital(hospital_id)}

@router.post("/doctors")
async def create_new_doctor(payload: dict, admin=Depends(get_current_admin)):
    return create_doctor(payload)

@router.patch("/doctors/{license_number}")
async def update_doctor_info(license_number: str, payload: dict, admin=Depends(get_current_admin)):
    return update_doctor(license_number, payload)

@router.delete("/doctors/{license_number}")
async def delete_doctor_info(license_number: str, admin=Depends(get_current_admin)):
    return delete_doctor(license_number)

@router.post(
    "/doctors/{license_number}/profile",
    summary="의사 프로필 사진 업로드",
    description="S3에 업로드→기존삭제→Firestore 갱신",
    response_model=dict,
)
async def upload_doctor_profile_endpoint(
    license_number: str,
    file: UploadFile = File(...),
    admin=Depends(get_current_admin),
):
    try:
        contents = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"파일 읽기 실패: {e}")

    try:
        new_url = upload_doctor_profile_service(
            license_number, contents, file.content_type
        )
    except ClientError as e:
        raise HTTPException(status_code=502, detail=f"S3 오류: {e}")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {"profile_url": new_url}