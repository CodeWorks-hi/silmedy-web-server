# app/core/dependencies.py

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import decode_access_token

security = HTTPBearer()

# 공통 - 토큰 유효성 검증
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload

# 의사 전용
def get_current_doctor(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None or payload.get("role") != "doctor":
        raise HTTPException(status_code=403, detail="의사 전용 API입니다.")
    return payload

# 관리자 전용
def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_access_token(token)
    print("🔍 관리자용 디코딩된 payload:", payload)  # 추가
    print("📌 decoded payload:", payload)  # ✅ 이 로그 추가 필요

    if payload is None or payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="관리자 전용 API입니다.")
    return payload