from fastapi import APIRouter, HTTPException
from app.schemas.auth       import LoginPayload
from app.services.auth_service import login_user

router = APIRouter()

@router.post(
    "/login",
    tags=["공통 - 로그인"],
    summary="로그인 요청을 처리합니다.",
    description="관리자 또는 의사가 로그인하기 위한 API입니다. 이메일과 비밀번호를 입력받아 JWT 토큰을 반환합니다.",
    response_model_exclude_none=True
)
async def login(payload: LoginPayload):
    try:
        return login_user(payload.dict())
    except ValueError as e:
        # 400 Bad Request: 필수 필드 누락 등
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        # 401 Unauthorized: ID/PW 불일치
        raise HTTPException(status_code=401, detail=str(e))
    except Exception:
        # 500 Internal Server Error
        raise HTTPException(
            status_code=500,
            detail="로그인 처리 중 알 수 없는 오류가 발생했습니다."
        )

