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

router = APIRouter(prefix="/video_calls", tags=["video_calls"])


@router.post(
    "/create",
    summary="새 영상 통화 방 생성",
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
    summary="통화 시작 처리 및 환자에게 FCM 푸시 전송",
    status_code=status.HTTP_200_OK,
)
async def start_call(payload: dict, user=Depends(get_current_user)):
    """
    1) payload에서 call_id, patient_id, 환자 FCM 토큰 조회
    2) Firestore/RTDB 상태를 'started'로 업데이트 (sync 부분)
    3) FCM 푸시 전송 (async)
    4) {"message": "..."} 형태로 결과 반환
    """
    try:
        # start_video_call은 async 함수이므로 반드시 await
        result = await start_video_call(payload)
        return result
    except Exception as e:
        # traceback 찍고 500 에러로 변환해서 클라이언트에 전달
        import traceback; traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"통화 시작 중 서버 오류: {e}"
        )


@router.post(
    "/answer",
    summary="환자가 보낸 Answer(SDP) 저장",
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


@router.post(
    "/reject",
    summary="통화 거절 처리",
    status_code=status.HTTP_200_OK,
)
async def post_reject(payload: dict, user=Depends(get_current_user)):
    """
    payload = {
      "call_id": "<문서 ID>",
      "reason": "busy"     # 거절 사유 (옵션)
    }
    sync 함수 reject_call 호출 → {"message": "..."} 반환
    """
    return reject_call(payload)


@router.post(
    "/end",
    summary="통화 종료 처리",
    status_code=status.HTTP_200_OK,
)
async def end_call(payload: dict, user=Depends(get_current_user)):
    """
    payload = { "call_id": "<문서 ID>" }
    sync 함수 end_video_call 호출 → {"message": "..."} 반환
    """
    return end_video_call(payload)


@router.post(
    "/text",
    summary="통화 중 텍스트 메시지 저장",
    status_code=status.HTTP_200_OK,
)
async def save_call_text(payload: dict, user=Depends(get_current_user)):
    """
    payload = {
      "call_id": "<문서 ID>",
      "text": "안녕하세요!"
    }
    sync 함수 save_text_message 호출 → {"message": "..."} 반환
    """
    return save_text_message(payload)