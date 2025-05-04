from firebase_admin import db

# 🔵 Offer 저장
def save_offer(room_id: str, sdp: dict):
    db.reference(f"signaling/{room_id}/offer").set(sdp)
    return {"message": "offer 저장 완료"}

# 🔵 Answer 저장
def save_answer(room_id: str, sdp: dict):
    db.reference(f"signaling/{room_id}/answer").set(sdp)
    return {"message": "answer 저장 완료"}

# 🔵 ICE 후보 추가 
def add_ice_candidate(room_id: str, role: str, candidate: dict):
    db.reference(f"signaling/{room_id}/{role}Candidates").push(candidate)
    return {"message": "ICE candidate 저장 완료"}