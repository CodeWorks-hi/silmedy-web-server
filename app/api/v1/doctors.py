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

@router.get(
    "/doctors",
    tags=["관리자 - 직원 관리"],
    summary="병원에 속한 의사 목록을 조회합니다.",
    description="현재 로그인한 관리자의 병원 ID를 기준으로 해당 병원에 소속된 의사 목록을 조회합니다.",
)
async def read_doctors(admin=Depends(get_current_admin)):
    hospital_id = admin["hospital_id"]
    return {"doctors": get_doctors_by_hospital(hospital_id)}

@router.post(
    "/doctors",
    tags=["관리자 - 직원 관리"],
    summary="새로운 의사를 등록합니다.",
    description="요청 본문에 포함된 의사 정보를 기반으로 새로운 의사를 등록합니다.",
)
async def create_new_doctor(payload: dict, admin=Depends(get_current_admin)):
    return create_doctor(payload)

@router.patch(
    "/doctors/{license_number}",
    tags=["관리자 - 직원 관리"],
    summary="의사 정보를 수정합니다.",
    description="면허번호에 해당하는 의사의 정보를 수정합니다. 일부 필드만 전달하여 부분 업데이트가 가능합니다.",
)
async def update_doctor_info(license_number: str, payload: dict, admin=Depends(get_current_admin)):
    return update_doctor(license_number, payload)

@router.delete(
    "/doctors/{license_number}",
    tags=["관리자 - 직원 관리"],
    summary="의사 정보를 삭제합니다.",
    description="해당 면허번호를 가진 의사의 정보를 시스템에서 삭제합니다.",
)
async def delete_doctor_info(license_number: str, admin=Depends(get_current_admin)):
    return delete_doctor(license_number)

@router.post(
    "/doctors/{license_number}/profile",
    tags=["관리자 - 직원 관리"],
    summary="의사 프로필 사진 업로드",
    description="프로필 사진을 S3에 업로드하고, 기존 이미지를 삭제한 후 Firestore에 URL을 갱신합니다.",
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