# app/api/v1/care_requests.py

from fastapi import APIRouter, Depends, HTTPException
from app.services.care_request_service import (
    get_waiting_care_requests_by_doctor,
    complete_care_request,
    get_care_request_detail
)
from app.core.dependencies import get_current_user

router = APIRouter()

@router.get("/care-requests/waiting", summary="대기 중인 진료 요청 조회", description="로그인한 의사에게 배정된 대기 환자 목록을 조회합니다.")
def get_waiting_list(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "doctor":
        raise HTTPException(status_code=403, detail="의사 권한이 필요합니다.")
    
    # 🔐 보안을 위해 doctor_id는 토큰에서만 추출
    return {"waiting_list": get_waiting_care_requests_by_doctor(current_user)}


@router.put("/care-requests/{request_id}/complete", summary="진료 완료 처리", description="특정 진료 요청을 완료 처리하고 완료 시간을 기록합니다.")
async def complete_request(request_id: int, user=Depends(get_current_user)):
    try:
        if user.get("role") != "doctor":
            raise HTTPException(status_code=403, detail="의사 권한이 필요합니다.")
        return complete_care_request(request_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/care-requests/{request_id}", summary="진료 요청 상세 조회", description="특정 진료 요청의 상세 정보 (환자 포함)를 반환합니다.")
async def read_care_request_detail(request_id: int, user=Depends(get_current_user)):
    try:
        return get_care_request_detail(request_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
