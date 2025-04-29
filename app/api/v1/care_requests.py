# app/api/v1/care_requests.py

from fastapi import APIRouter, Depends, HTTPException
from app.services.care_request_service import (
    get_waiting_care_requests_by_doctor,
    complete_care_request
)
from app.core.dependencies import get_current_user

router = APIRouter()

# 🔵 대기 중인 진료 요청 목록 조회 (로그인된 의사 기준)
@router.get("/care-requests/waiting", summary="대기 중인 진료 요청 조회", description="로그인한 의사에게 배정된 대기 환자 목록을 조회합니다.")
async def read_waiting_care_requests(user=Depends(get_current_user)):
    try:
        if user.get("role") != "doctor":
            raise HTTPException(status_code=403, detail="의사 권한이 필요합니다.")

        doctor_id = user.get("license_number")
        return {"waiting_list": get_waiting_care_requests_by_doctor(doctor_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🔵 진료 완료 처리
@router.put("/care-requests/{request_id}/complete", summary="진료 완료 처리", description="특정 진료 요청을 완료 처리하고 완료 시간을 기록합니다.")
async def complete_request(request_id: int, user=Depends(get_current_user)):
    try:
        if user.get("role") != "doctor":
            raise HTTPException(status_code=403, detail="의사 권한이 필요합니다.")

        return complete_care_request(request_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))