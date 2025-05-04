from uuid import uuid4
from app.core.config import (
    get_firestore_client,
    get_realtime_db,
    init_firebase,
)
# ★ 여기에 messaging 을 import 합니다.
from firebase_admin import messaging
import datetime


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
        "offer": "",
        "answer": "",
        "callerCandidates": {},
        "calleeCandidates": {}
    })

    return {"id": call_id}




async def start_video_call(payload: dict) -> dict:
    """
    1) Firestore·RTDB 상태 'started'로 업데이트  
    2) FCM 메시지 전송 (messaging.Message 인스턴스)  
    """
    # 1) 받은 payload 로깅
    print(f"🚀 start_video_call payload: {payload}")

    # 2) Firestore/RTDB 업데이트
    fs_db   = get_firestore_client()
    call_id = payload.get("call_id")
    patient_id = payload.get("patient_id")

    print(f"→ Firestore 상태 변경 준비 call_id={call_id}")
    fs_db.collection("calls").document(call_id).update({"status": "started"})
    print("✅ Firestore status=started")

    rt_db = get_realtime_db()
    rt_ref = rt_db.reference(f"calls/{call_id}/status")
    rt_ref.set("started")
    print("✅ RTDB status=started")

    # 3) FCM 토큰 확보 (payload 우선, DB fallback)
    patient_token = payload.get("patient_fcm_token")
    print(f"→ payload.patient_fcm_token: {patient_token!r}")

    if not patient_token and patient_id:
        print(f"→ DB fallback 으로 환자({patient_id}) 문서 조회")
        doc = fs_db.collection("patients").document(str(patient_id)).get()
        if doc.exists:
            patient_token = doc.to_dict().get("fcm_token")
            print(f"→ Firestore 에서 조회된 fcm_token: {patient_token!r}")
        else:
            print("❌ Firestore 환자 문서가 없습니다.")

    # 4) FCM 메시지 생성 & 전송
    if patient_token:
        msg = messaging.Message(
            notification=messaging.Notification(
                title="영상 통화 요청",
                body="수락하려면 탭하세요."
            ),
            data={
                "type":   "CALL_STARTED",
                "callId": call_id,
                "roomId": call_id,
                "timestamp": datetime.datetime.utcnow().isoformat(),
            },
            token=patient_token,
        )
        print(f"▶ FCM data payload: {msg.data}")
        try:
            message_id = messaging.send(msg)
            print(f"✅ FCM 전송 성공, message_id={message_id}")
        except Exception as send_err:
            print(f"❌ FCM 전송 실패: {send_err}")
            # 필요 시 여기서 다시 raise 해도 됩니다.
    else:
        print("⚠️ FCM 토큰이 없어서 전송을 건너뜁니다.")

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