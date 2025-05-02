# app/services/video_call_service.py

from uuid import uuid4
from app.core.config import (
    get_firestore_client,
    get_realtime_db,
    init_firebase,
    get_fcm_client  # Firebase Admin SDK 메시징 클라이언트 반환 함수
)

# 🛠 앱 시작 시 Firebase 초기화 한 번 해두기
init_firebase()


def create_video_call(payload: dict):
    """
    1) Firestore에 새 문서 ID 자동 생성 → payload 에 포함해 저장
    2) RTDB에 signaling 초기 구조 생성
    """
    # Firestore 클라이언트
    fs_db = get_firestore_client()
    calls_col = fs_db.collection("calls")

    # Auto ID 생성
    doc_ref = calls_col.document()
    call_id = doc_ref.id

    # payload에 id 필드 포함
    payload_with_id = {**payload, "id": call_id}
    doc_ref.set(payload_with_id)

    # Realtime DB에 빈 signaling 노드 생성
    rt_db = get_realtime_db()
    rt_ref = rt_db.reference(f"calls/{call_id}")
    rt_ref.set({
        "offer": None,
        "answer": None,
        "callerCandidates": {},
        "calleeCandidates": {}
    })

    return {"id": call_id}


def start_video_call(payload: dict):
    """
    1) Firestore 상태 업데이트 → started
    2) RTDB status 필드도 started로 설정 (옵션)
    3) FCM으로 환자에게 CALL_STARTED 알림 전송
    """
    call_id = payload.get("call_id")
    patient_token = payload.get("patient_fcm_token")

    if not call_id:
        return {"error": "call_id is required"}, 400

    # Firestore 상태 업데이트
    fs_db = get_firestore_client()
    fs_db.collection("calls").document(call_id).update({"status": "started"})

    # RTDB status 필드 업데이트
    rt_db = get_realtime_db()
    rt_db.reference(f"calls/{call_id}/status").set("started")

    # FCM 푸시 전송
    if patient_token:
        fcm = get_fcm_client()
        message = {
            "data": {
                "type":       "CALL_STARTED",
                "callId":     call_id,       # roomId
                "roomId":     call_id,       # <-- 여기에 roomId
                "offerSdp":   offer_sdp,     # (옵션)
            },
            "token": patient_token,
        }
        fcm.send(message)

    return {"message": "통화 시작 및 알림 전송 완료"}


def end_video_call(payload: dict):
    """
    1) Firestore 상태 업데이트 → ended
    2) RTDB status 필드 ended로 설정
    3) (옵션) FCM으로 종료 알림 전송
    """
    call_id = payload.get("call_id")
    if call_id:
        # Firestore
        fs_db = get_firestore_client()
        fs_db.collection("calls").document(call_id).update({"status": "ended"})
        # RTDB
        rt_db = get_realtime_db()
        rt_db.reference(f"calls/{call_id}/status").set("ended")

    return {"message": "통화 종료"}


def save_text_message(payload: dict):
    """
    Firestore 하위 컬렉션에 텍스트 메시지 저장
    """
    call_id = payload.get("call_id")
    text = payload.get("text", "")

    if call_id:
        fs_db = get_firestore_client()
        fs_db.collection("calls") \
             .document(call_id) \
             .collection("messages") \
             .add({"text": text})

    return {"message": "메시지 저장 완료"}