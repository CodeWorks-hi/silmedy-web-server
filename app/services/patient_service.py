from typing import Dict
from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr
import datetime

# … 기존에 사용 중인 JWT 발행/검증 유틸을 import하세요.
from app.core.security import create_access_token, create_refresh_token

# ──────────────────────────────────────────────────────────
# 1) 로그인 요청 스키마
# ──────────────────────────────────────────────────────────
class PatientLoginPayload(BaseModel):
    email:      EmailStr
    password:   str


# ──────────────────────────────────────────────────────────
# 2) 로그인 응답 스키마
# ──────────────────────────────────────────────────────────
class PatientLoginResponse(BaseModel):
    access_token:  str
    refresh_token: str
    patient_id:    str
    token_type:    str = "bearer"


# ──────────────────────────────────────────────────────────
# 3) FCM 토큰 등록 스키마
# ──────────────────────────────────────────────────────────
class FcmTokenPayload(BaseModel):
    fcm_token: str


# ──────────────────────────────────────────────────────────
# 4) 로그인 비즈니스 로직
# ──────────────────────────────────────────────────────────
def login_patient(email: str, password: str) -> PatientLoginResponse:
    # 1) DB에서 사용자 조회 (예: Firestore, SQL 등)
    user = get_user_by_email(email)  # 직접 구현해주세요
    if not user or not verify_password(password, user.hashed_password):
        # 이메일 또는 비밀번호 불일치
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2) JWT 생성
    now = datetime.datetime.utcnow()
    access_token  = create_access_token({"sub": user.id}, expires_delta=datetime.timedelta(minutes=30))
    refresh_token = create_refresh_token({"sub": user.id})

    # 3) (선택) 리프레시 토큰 저장 로직 등 추가 가능

    return PatientLoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        patient_id=user.id,
    )


# ──────────────────────────────────────────────────────────
# 5) FCM 토큰 저장 로직
# ──────────────────────────────────────────────────────────
def save_patient_fcm_token(patient_id: str, fcm_token: str) -> bool:
    """
    Firestore 'patients/{patient_id}' 문서에
    fcm_token 필드를 추가/업데이트 합니다.
    """
    try:
        from app.core.config import get_firestore_client
        db = get_firestore_client()
        db.collection("patients").document(patient_id).update({
            "fcm_token": fcm_token
        })
        return True
    except Exception as e:
        # 로깅
        print(f"❌ save_patient_fcm_token error: {e}")
        return False


# ──────────────────────────────────────────────────────────
# 6) (예시) 비밀번호 검증 & 유저 조회 Helpers
# ──────────────────────────────────────────────────────────
def get_user_by_email(email: str):
    # TODO: 실제 DB/Firestore에서 patient 조회
    # return Patient(id="123", email=email, hashed_password="…")
    ...

def verify_password(plain: str, hashed: str) -> bool:
    # TODO: bcrypt, argon2 등으로 해시 비교
    return True