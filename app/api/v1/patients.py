# app/api/v1/patients.py

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Body,
    status,
)
from fastapi.security import OAuth2PasswordBearer

# 서비스 모듈에서 스키마(Pydantic 모델)와 로직 함수를 가져옵니다.
from app.services.patient_service import (
    PatientLoginPayload,      # 로그인 요청 바디 스키마
    PatientLoginResponse,     # 로그인 응답 바디 스키마
    FcmTokenPayload,          # FCM 토큰 등록 바디 스키마
    login_patient,            # 이메일/비밀번호 검증 → JWT 발행 로직
    save_patient_fcm_token,   # Firestore에 FCM 토큰 저장 로직
)
from app.core.dependencies import get_current_user  # JWT 검증용 Dependency

# 이 router는 메인 app.include_router(..., prefix="/api/v1")에서
# URL 앞에 "/api/v1"을 자동으로 붙여 줍니다.
router = APIRouter(tags=["patients"])

# OAuth2PasswordBearer: Authorization 헤더에서 Bearer 토큰을 꺼내어
# Depends(oauth2_scheme)로 주입해 주는 역할을 합니다.
# tokenUrl은 토큰(=JWT)을 발급해 주는 로그인 엔드포인트를 가리킵니다.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/patients/login")


@router.post(
    "/patients/login",
    response_model=PatientLoginResponse,
    status_code=status.HTTP_200_OK,
    summary="환자 로그인 (이메일/비밀번호 → JWT 발행)",
)
async def patient_login(
    payload: PatientLoginPayload = Body(...),  # {"email": ..., "password": ...}
):
    """
    1) 이메일/비밀번호를 검증하고
    2) access_token, refresh_token, patient_id를 반환합니다.
    """
    try:
        # 서비스 로직에서 HTTPException을 직접 던질 수 있습니다.
        return login_patient(payload.email, payload.password)
    except HTTPException as e:
        # 인증 실패(401) 등은 서비스 로직에서 던진 예외를 그대로 전달
        raise e
    except Exception:
        # 그 외 예기치 못한 서버 에러
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그인 처리 중 서버 오류가 발생했습니다."
        )


@router.post(
    "/patients/{patient_id}/fcm-token",
    status_code=status.HTTP_200_OK,
    summary="환자 FCM 토큰 등록",
)
async def register_fcm_token(
    # URL 경로 변수: JWT의 sub(claim)으로 발급된 patient_id
    patient_id: str = Path(..., description="환자 ID (JWT sub)"),

    # 요청 바디: {"fcm_token": "..."}
    payload: FcmTokenPayload = Body(...),

    # Authorization 헤더에서 Bearer 토큰을 꺼내 옵니다.
    token: str = Depends(oauth2_scheme),

    # token을 검증한 후, get_current_user에서 리턴한 사용자 정보를 받을 수 있습니다.
    current=Depends(get_current_user),
):
    """
    1) Authorization: Bearer {access_token} 토큰 검증
    2) Firestore의 patients/{patient_id} 문서에 fcm_token 필드 저장
    """
    # (선택) patient_id와 current.sub가 같은지 추가 검증 가능
    success = save_patient_fcm_token(patient_id, payload.fcm_token)
    if not success:
        # 저장 실패 시 500 에러 리턴
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="FCM 토큰 저장에 실패했습니다."
        )

    # 성공 시 간단 메시지 반환
    return {"message": "FCM 토큰 저장 완료"}