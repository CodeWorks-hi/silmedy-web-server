from uuid import uuid4
from app.core.config import (
    get_firestore_client,
    get_realtime_db,
    init_firebase,
)
# ★ 여기에 messaging 을 import 합니다.
from firebase_admin import messaging

# 🛠 앱 시작 시 Firebase 초기화 한 번 해두기
init_firebase()


def create_video_call(payload: dict):
    """
    1) Firestore에 새 문서 ID 자동 생성 → payload 에 포함해 저장
    2) RTDB에 signaling 초기 구조 생성
    """
    fs_db = get_firestore_client()
    calls_col = fs_db.collection("calls")

    doc_ref = calls_col.document()
    call_id = doc_ref.id

    payload_with_id = {**payload, "id": call_id}
    doc_ref.set(payload_with_id)

    rt_db = get_realtime_db()
    rt_ref = rt_db.reference(f"calls/{call_id}")
    rt_ref.set({
        "offer": None,
        "answer": None,
        "callerCandidates": {},
        "calleeCandidates": {}
    })

    return {"id": call_id}


async def start_video_call(payload: dict):
    """
    1) Firestore·RTDB 상태 'started'로 업데이트
    2) FCM 메시지 발송 (messaging.Message 인스턴스)
    """
    fs_db     = get_firestore_client()
    call_id   = payload.get("call_id")
    patient_id= payload.get("patient_id")

    # ① Firestore, RTDB 상태 업데이트
    fs_db.collection("calls").document(call_id).update({"status": "started"})
    rt_db = get_realtime_db()
    rt_db.reference(f"calls/{call_id}/status").set("started")

    # ② 환자 FCM 토큰 조회 (payload 우선, DB fallback)
    patient_token = payload.get("patient_fcm_token")
    if not patient_token and patient_id:
        doc = fs_db.collection("patients").document(str(patient_id)).get()
        if doc.exists:
            patient_token = doc.to_dict().get("fcm_token")

    # ③ FCM 푸시 전송: 반드시 messaging.Message 로 생성
    if patient_token:
        msg = messaging.Message(
            data={
                "type":   "CALL_STARTED",
                "callId": call_id,
                "roomId": call_id,
            },
            token=patient_token,
        )
        # send() 는 동기 함수입니다.
        messaging.send(msg)

    return {"message": "통화 시작 및 알림 전송 완료"}


def end_video_call(payload: dict):
    """
    1) Firestore, RTDB 상태 'ended'로 업데이트
    """
    call_id = payload.get("call_id")
    if call_id:
        fs_db = get_firestore_client()
        fs_db.collection("calls").document(call_id).update({"status": "ended"})
        rt_db = get_realtime_db()
        rt_db.reference(f"calls/{call_id}/status").set("ended")

    return {"message": "통화 종료"}


def save_text_message(payload: dict):
    """
    Firestore 하위 컬렉션에 텍스트 메시지 저장
    """
    call_id = payload.get("call_id")
    text    = payload.get("text", "")

    if call_id:
        fs_db = get_firestore_client()
        fs_db.collection("calls") \
             .document(call_id) \
             .collection("messages") \
             .add({"text": text})

    return {"message": "메시지 저장 완료"}


def save_answer(payload: dict):
    fs_db   = get_firestore_client()
    call_id = payload["call_id"]
    answer  = payload["sdp"]
    fs_db.collection("calls").document(call_id).update({"answer": answer})
    return {"message": "Answer 저장 완료"}


def reject_call(payload: dict):
    fs_db   = get_firestore_client()
    call_id = payload["call_id"]
    reason  = payload.get("reason", "rejected")
    fs_db.collection("calls").document(call_id).update({
        "status":        "rejected",
        "reject_reason": reason
    })
    return {"message": "통화 거부 처리 완료"}