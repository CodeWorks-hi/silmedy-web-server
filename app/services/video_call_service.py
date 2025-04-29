# app/services/video_call_service.py

from app.core.config import get_firestore_client

# 🔵 영상 통화방 생성
def create_video_call(payload: dict):
    db = get_firestore_client()  # ✅ 수정
    collection_video_calls = db.collection("calls")
    doc_ref = collection_video_calls.document()
    doc_ref.set(payload)
    return {"id": doc_ref.id}

# 🔵 통화 시작 처리
def start_video_call(payload: dict):
    db = get_firestore_client()  # ✅ 수정
    collection_video_calls = db.collection("calls")
    call_id = payload.get("call_id")
    collection_video_calls.document(call_id).update({"status": "started"})
    return {"message": "통화 시작"}

# 🔵 통화 종료 처리
def end_video_call(payload: dict):
    db = get_firestore_client()  # ✅ 수정
    collection_video_calls = db.collection("calls")
    call_id = payload.get("call_id")
    collection_video_calls.document(call_id).update({"status": "ended"})
    return {"message": "통화 종료"}

# 🔵 통화 중 텍스트 메시지 저장
def save_text_message(payload: dict):
    db = get_firestore_client()  # ✅ 수정
    collection_video_calls = db.collection("calls")
    call_id = payload.get("call_id")
    text = payload.get("text")
    collection_video_calls.document(call_id).collection("messages").add({"text": text})
    return {"message": "메시지 저장 완료"}