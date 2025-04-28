from firebase_admin import firestore

def create_video_call(payload: dict):
    db = firestore.client()
    collection_video_calls = db.collection("calls")
    doc_ref = collection_video_calls.document()
    doc_ref.set(payload)
    return {"id": doc_ref.id}

def start_video_call(payload: dict):
    db = firestore.client()
    collection_video_calls = db.collection("calls")
    call_id = payload.get("call_id")
    collection_video_calls.document(call_id).update({"status": "started"})
    return {"message": "통화 시작"}

def end_video_call(payload: dict):
    db = firestore.client()
    collection_video_calls = db.collection("calls")
    call_id = payload.get("call_id")
    collection_video_calls.document(call_id).update({"status": "ended"})
    return {"message": "통화 종료"}

def save_text_message(payload: dict):
    db = firestore.client()
    collection_video_calls = db.collection("calls")
    call_id = payload.get("call_id")
    text = payload.get("text")
    collection_video_calls.document(call_id).collection("messages").add({"text": text})
    return {"message": "메시지 저장 완료"}