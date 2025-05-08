# app/core/security.py
import os
import jwt
from datetime import datetime, timedelta
from typing import Optional

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM  = "HS256"

ACCESS_EXPIRE_SECONDS  = int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", 3600))
REFRESH_EXPIRE_SECONDS = int(os.getenv("REFRESH_TOKEN_EXPIRE_SECONDS", 604800))
# ────────────────────────────────────────────────────────
# 1. 액세스 토큰
# ────────────────────────────────────────────────────────
def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)) -> str:
    """
    data: payload에 담을 정보 (예: {"sub": user_id, "role": "..."} )
    expires_delta: 토큰 유효기간 (기본 1시간)
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    """
    토큰을 디코드해서 payload(dict)를 반환합니다.
    만료되었거나 유효하지 않으면 None을 반환합니다.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        # 만료
        return None
    except jwt.InvalidTokenError:
        # 서명 불일치 등
        return None


# ────────────────────────────────────────────────────────
# 2. 리프레시 토큰
# ────────────────────────────────────────────────────────
def create_refresh_token(data: dict, expires_delta: timedelta = timedelta(days=7)) -> str:
    """
    리프레시 토큰: 만료 기간을 더 길게 잡습니다 (예: 7일).
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_refresh_token(token: str) -> Optional[dict]:
    """
    리프레시 토큰 검증용 디코드 함수.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None