from app.core.config import get_firestore_client

async def register_fcm_token(patient_id: str, token: str):
    fs = get_firestore_client()
    # 환자 문서에 fcm_token 필드 업데이트
    fs.collection("patients").document(patient_id).update({
        "fcm_token": token
    })