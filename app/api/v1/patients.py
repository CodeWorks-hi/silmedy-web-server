from fastapi import APIRouter, Depends, HTTPException, Path, Body, status
from fastapi.security import OAuth2PasswordBearer

# → 서비스 모듈에서 스키마와 로직을 가져옵니다.
from app.services.patient_service import (
    PatientLoginPayload,
    PatientLoginResponse,
    FcmTokenPayload,
    login_patient,
    save_patient_fcm_token,
)
from app.core.dependencies import get_current_user  # JWT 검증용 Depends

router = APIRouter(prefix="/patients", tags=["patients"])

# OAuth2PasswordBearer는 내부적으로 Authorization 헤더의 Bearer 토큰을 꺼냅니다.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="patients/login")


@router.post(
    "/login",
    response_model=PatientLoginResponse,
    status_code=status.HTTP_200_OK,
    summary="환자 로그인 (이메일/비밀번호 → JWT 발행)",
)
async def patient_login(payload: PatientLoginPayload = Body(...)):
    """
    1) 이메일/비밀번호 검증  
    2) access_token, refresh_token, patient_id 반환  
    """
    try:
        return login_patient(payload.email, payload.password)
    except HTTPException as e:
        # login_patient에서 401 에러를 던졌을 때 그대로 전달
        raise e
    except Exception:
        # 의도치 않은 에러
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그인 처리 중 서버 오류가 발생했습니다."
        )


@router.post(
    "/{patient_id}/fcm-token",
    status_code=status.HTTP_200_OK,
    summary="환자 FCM 토큰 등록",
)
async def register_fcm_token(
    patient_id: str = Path(..., description="환자 ID (JWT sub)"),
    payload: FcmTokenPayload = Body(...),
    token: str = Depends(oauth2_scheme),      # Authorization: Bearer {access_token}
    current=Depends(get_current_user),         # 토큰 검증 후 유저 정보
):
    """
    1) Bearer 토큰 검증  
    2) Firestore에 fcm_token 저장  
    """
    # (선택) path patient_id와 토큰의 sub가 같은지 추가 검증 가능
    success = save_patient_fcm_token(patient_id, payload.fcm_token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="FCM 토큰 저장에 실패했습니다."
        )
    return {"message": "FCM 토큰 저장 완료"}