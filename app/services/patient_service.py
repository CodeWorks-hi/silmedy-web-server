# app/services/patient_service.py
from app.core.config import get_firestore_client

def save_patient_fcm_token(patient_id: str, fcm_token: str) -> bool:
    """
    Firestore 'patients/{patient_id}' 문서에
    fcm_token 필드를 추가/업데이트 합니다.
    """
    try:
        db = get_firestore_client()
        # patients 컬렉션 안에 patient_id 문서 업데이트
        db.collection("patients").document(patient_id).update({
            "fcm_token": fcm_token
        })
        return True
    except Exception as e:
        # 로깅 등을 추가하면 디버깅에 도움이 됩니다.
        print("❌ FCM 토큰 저장 에러:", e)
        return False