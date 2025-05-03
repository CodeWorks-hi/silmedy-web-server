from typing import Optional
from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr
import datetime

from app.core.security import create_access_token, create_refresh_token
from app.core.config import get_firestore_client

# ─── Pydantic 스키마 정의 ────────────────────────────────
class PatientLoginPayload(BaseModel):
    """
    로그인 요청 바디 스키마
    - email: 사용자가 입력한 이메일 (유효성 검증 포함)
    - password: 사용자가 입력한 원문 비밀번호
    """
    email: EmailStr
    password: str

class PatientLoginResponse(BaseModel):
    """
    로그인 응답 바디 스키마
    - access_token: 클라이언트가 API 호출 시 사용할 JWT access 토큰
    - refresh_token: access 토큰 만료 시 재발급용 JWT refresh 토큰
    - name: 환자 이름 (클라이언트 UI 표시용)
    - fcm_token: 클라이언트에서 전달받은 FCM 토큰 (등록 완료 후 반환)
    """
    access_token: str
    refresh_token: str
    name: str
    fcm_token: Optional[str] = None

class FcmTokenPayload(BaseModel):
    """
    FCM 토큰 등록 요청 바디 스키마
    - fcm_token: 클라이언트 디바이스에서 획득한 Firebase Cloud Messaging 토큰
    """
    fcm_token: str

# ─── 비즈니스 로직 함수 ────────────────────────────────
def login_patient(email: str, password: str) -> PatientLoginResponse:
    """
    1) Firestore 'patients' 컬렉션에서 이메일로 문서 조회
    2) 비밀번호 검증 (실제 시스템에서는 해시 비교 필요)
    3) JWT access/refresh 토큰 발급
    4) 환자 이름과 토큰을 포함한 응답 객체 반환
    """
    # Firestore 클라이언트 획득
    db = get_firestore_client()
    # 이메일 일치 문서 조회 (최초 1개)
    docs = db.collection("patients").where("email", "==", email).limit(1).get()
    if not docs:
        # 해당 이메일의 환자 문서가 없으면 인증 실패
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다."
        )
    user = docs[0].to_dict()

    # 비밀번호 검증 (여기서는 단순 문자열 비교)
    if password != user.get("password"):
        # 비밀번호 불일치 시 인증 실패
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다."
        )

    # JWT payload에 sub로 식별자(email) 포함
    # access 토큰: 짧은 유효기간 (예: 30분)
    access_token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=datetime.timedelta(minutes=30)
    )
    # refresh 토큰: 긴 유효기간 (config에서 설정)
    refresh_token = create_refresh_token(data={"sub": user["email"]})

    # 응답 객체 생성: 환자 이름과 토큰 정보 반환
    return PatientLoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        name=user.get("name"),
    )

def save_patient_fcm_token(patient_email: str, fcm_token: str) -> bool:
    """
    Firestore 'patients' 컬렉션에서 지정 이메일의 문서를 찾아
    'fcm_token' 필드를 업데이트합니다.

    Returns:
        True: 업데이트 성공
        False: 문서 미발견 또는 예외 발생
    """
    try:
        db = get_firestore_client()
        # 해당 이메일로 문서 조회
        docs = db.collection("patients").where("email", "==", patient_email).limit(1).get()
        if not docs:
            # 문서가 없으면 False
            return False
        # 문서 참조 획득 후 업데이트
        doc_ref = docs[0].reference
        doc_ref.update({"fcm_token": fcm_token})
        return True
    except Exception as e:
        # 예외 발생 시 로깅 후 False 반환
        print(f"❌ save_patient_fcm_token error: {e}")
        return False

# ─── 모듈 외부에 노출할 이름 설정 ────────────────────────────────
__all__ = [
    "PatientLoginPayload",
    "PatientLoginResponse",
    "FcmTokenPayload",
    "login_patient",
    "save_patient_fcm_token",
]