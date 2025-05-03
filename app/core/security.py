# app/core/security.py

import jwt
from datetime import datetime, timedelta
from typing import Optional

# ⚠️ 실제 운영 환경에선 .env나 Secret Manager에서 불러오세요.
SECRET_KEY = "your_secret_key"
ALGORITHM  = "HS256"

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