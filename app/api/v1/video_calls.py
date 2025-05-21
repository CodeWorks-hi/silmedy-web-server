# app/api/v1/video_calls.py

from fastapi import APIRouter, Depends, HTTPException, status
from app.services.video_call_service import (
    create_video_call,    # sync 함수: dict 반환
    start_video_call,     # async 함수: coroutine 반환 → await 필요
    end_video_call,       # sync 함수: dict 반환
    save_text_message,    # sync 함수: dict 반환
    save_answer,          # sync 함수: dict 반환
    reject_call           # sync 함수: dict 반환
)
from app.core.dependencies import get_current_user  # JWT 검증용 Dependency

router = APIRouter()


@router.post(
    "/create",
    tags=["의사 - 영상통화 진행"],
    summary="영상 통화 방을 생성합니다.",
    description="Firestore에 메타데이터를 저장하고 RTDB에 signaling 구조를 초기화하여 새로운 영상 통화 방을 생성하는 기능입니다.",
    status_code=status.HTTP_200_OK,
)
async def create_call_room(payload: dict, user=Depends(get_current_user)):
    """
    1) Firestore에 통화 방 메타데이터 저장 (sync)
    2) RTDB에 signaling 초기 구조 생성 (sync)
    3) 생성된 call_id를 {"id": call_id} 형태로 반환
    """
    return create_video_call(payload)


@router.post(
    "/start",
    tags=["의사 - 영상통화 진행"],
    summary="통화를 시작하고 환자에게 푸시 알림을 보냅니다.",
    description="의사가 통화를 시작하며, 환자에게 Firebase Cloud Messaging 푸시 알림을 전송하는 기능입니다.",
    status_code=status.HTTP_200_OK,
)
async def start_call(payload: dict, user=Depends(get_current_user)):
    """
    payload 예시:
    {
      "call_id": "NcuwTCsElAupVGiXfBPi",
      "doctor_id": "123456",
      "patient_id": 13,
      // "patient_fcm_token": "…"  // (선택) 직접 주입 가능
    }
    """
    try:
        # 반드시 await
        result = await start_video_call(payload)
        return result
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/answer",
    tags=["의사 - 영상통화 진행"],
    summary="환자가 보낸 Answer SDP를 저장합니다.",
    description="WebRTC 연결을 위해 환자가 보낸 Answer SDP 정보를 RTDB에 저장하는 기능입니다.",
    status_code=status.HTTP_200_OK,
)
async def post_answer(payload: dict, user=Depends(get_current_user)):
    """
    payload = {
      "call_id": "<문서 ID>",
      "sdp": { ... }       # RTCSessionDescription.toJSON() 형식
    }
    sync 함수 save_answer 호출 → {"message": "..."} 반환
    """
    return save_answer(payload)


# @router.post(
#     "/reject",
#     tags=["의사 - 영상통화 진행"],
#     summary="영상 통화를 거절합니다.",
#     description="의사가 영상 통화를 거절하고 사유를 기록하는 기능입니다.",
#     status_code=status.HTTP_200_OK,
# )
# async def post_reject(payload: dict, user=Depends(get_current_user)):
#     """
#     payload = {
#       "call_id": "<문서 ID>",
#       "reason": "busy"     # 거절 사유 (옵션)
#     }
#     sync 함수 reject_call 호출 → {"message": "..."} 반환
#     """
#     return reject_call(payload)


@router.post(
    "/end",
    tags=["의사 - 영상통화 진행"],
    summary="영상 통화를 종료합니다.",
    description="의사가 통화를 종료하며, 관련 상태를 갱신하는 기능입니다.",
    status_code=status.HTTP_200_OK,
)
async def end_call(payload: dict, user=Depends(get_current_user)):
    """
    payload = { "call_id": "<문서 ID>" }
    sync 함수 end_video_call 호출 → {"message": "..."} 반환
    """
    return end_video_call(payload)


# @router.post(
#     "/text",
#     tags=["의사 - 영상통화 진행"],
#     summary="통화 중 텍스트 메시지를 저장합니다.",
#     description="영상 통화 중 송수신된 텍스트 메시지를 저장하는 기능입니다.",
#     status_code=status.HTTP_200_OK,
# )
# async def save_call_text(payload: dict, user=Depends(get_current_user)):
#     """
#     payload = {
#       "call_id": "<문서 ID>",
#       "text": "안녕하세요!"
#     }
#     """
#     return save_text_message(payload)