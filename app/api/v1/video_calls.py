# app/api/v1/video_calls.py
from firebase_admin import messaging
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


async def start_video_call(payload: dict):
    fs_db      = get_firestore_client()
    call_id    = payload.get("call_id")
    patient_id = payload.get("patient_id")

    # ① Firestore, RTDB 상태 업데이트 (기존 코드)
    fs_db.collection("calls").document(call_id).update({"status": "started"})
    rt_db = get_realtime_db()
    rt_db.reference(f"calls/{call_id}/status").set("started")

    # ② 환자 FCM 토큰 조회 (payload 우선, DB fallback)
    patient_token = payload.get("patient_fcm_token")
    if not patient_token and patient_id:
        doc = fs_db.collection("patients").document(str(patient_id)).get()
        if doc.exists:
            patient_token = doc.to_dict().get("fcm_token")

    # ────────────────────────────────────────────────────
    # ③ FCM 푸시 전송: notification + data 페이로드 구성
    # ────────────────────────────────────────────────────
    if patient_token:
        msg = messaging.Message(
            notification=messaging.Notification(
                title="영상 통화 요청",
                body="통화를 수락하려면 탭하세요."
            ),
            data={
                "callId": call_id,
                "roomId": call_id,
                "type":   "CALL_STARTED",
            },
            token=patient_token,
        )
        # 동기 호출로 메시지 전송
        messaging.send(msg)

    return {"message": "통화 시작 및 알림 전송 완료"}

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