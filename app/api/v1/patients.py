# app/api/v1/patients.py

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Body,
    status,
)
from fastapi.security import OAuth2PasswordBearer

# Pydantic 스키마와 비즈니스 로직 함수(import)
from app.services.patient_service import (
    PatientLoginPayload,      # 로그인 요청 바디 모델 (email, password)
    PatientLoginResponse,     # 로그인 응답 바디 모델 (access/refresh token 등)
    FcmTokenPayload,          # FCM 토큰 등록 요청 바디 모델 (fcm_token)
    login_patient,            # 로그인 처리 함수 (이메일/비밀번호 검증 → JWT 발행)
    save_patient_fcm_token,   # FCM 토큰 저장 함수 (Firestore 업데이트)
)
from app.core.dependencies import get_current_user  # JWT 검증용 Depends

# 이 라우터는 main.py에서 include_router(..., prefix="/api/v1") 으로 등록됩니다.
router = APIRouter()

# OAuth2PasswordBearer: Authorization 헤더의 Bearer 토큰을 파싱해 줍니다.
# tokenUrl은 클라이언트가 로그인하여 토큰을 발급받을 엔드포인트 경로입니다.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/patients/login")


@router.post(
    "/patients/login",                     # 최종 경로: /api/v1/patients/login
    response_model=PatientLoginResponse,   # 성공 시 이 Pydantic 모델로 응답
    status_code=status.HTTP_200_OK,        # HTTP 200 리턴
    summary="환자 로그인 (이메일/비밀번호 → JWT 발급)",
)
async def patient_login(
    payload: PatientLoginPayload = Body(...),  # 요청 JSON → PatientLoginPayload(email, password)
):
    """
    1) 요청 바디에서 email, password를 꺼냅니다.
    2) login_patient() 호출하여:
       • DB에서 해당 이메일의 환자 레코드 조회
       • 비밀번호 해시 검증
       • JWT access/refresh 토큰 생성
       • PatientLoginResponse(access_token, refresh_token, patient_id) 반환
    3) 인증 실패 시 HTTPException(401) 발생
    4) 예기치 않은 에러 시 HTTPException(500) 발생
    """
    try:
        return login_patient(payload.email, payload.password)
    except HTTPException:
        # login_patient 내부에서 인증 실패(401) 등을 던지면 그대로 재전달
        raise
    except Exception:
        # 그 외 예기치 않은 서버 오류
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그인 처리 중 서버 오류가 발생했습니다."
        )


@router.post(
    "/patients/fcm-token",              # 최종 경로: /api/v1/patients/fcm-token
    status_code=status.HTTP_200_OK,     # HTTP 200 리턴
    summary="환자 FCM 토큰 등록",
)
async def register_fcm_token(
    payload: FcmTokenPayload = Body(...),    # 요청 JSON → { "fcm_token": "..." }
    token: str = Depends(oauth2_scheme),     # Authorization 헤더의 Bearer 토큰 추출
    current=Depends(get_current_user),        # 위 토큰을 검증하고, payload(sub 등)를 리턴
):
    """
    1) Authorization: Bearer {access_token} 인증
    2) get_current_user()를 통해 토큰이 유효한지 검증
    3) 현재 토큰의 sub(claim)에 담긴 환자 ID를 current["sub"]에서 얻습니다.
    4) save_patient_fcm_token(patient_id, fcm_token)로 Firestore에 저장 시도
    5) 저장 실패 시 HTTP 500 에러, 성공 시 간단 메시지 반환
    """
    # 토큰의 sub에서 가져온 환자 ID
    patient_id = current["sub"]

    # Firestore 'patients/{patient_id}' 문서에 fcm_token 업데이트
    success = save_patient_fcm_token(patient_id, payload.fcm_token)
    if not success:
        # 저장 실패 시 내부 로깅 후 500 리턴
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="FCM 토큰 저장에 실패했습니다."
        )

    # 저장 완료 응답
    return {"message": "FCM 토큰 저장 완료"}