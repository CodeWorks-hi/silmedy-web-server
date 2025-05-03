from fastapi import APIRouter, Depends, HTTPException, Path, Body
from pydantic import BaseModel
from app.core.dependencies import get_current_user
from app.services.patient_service import save_patient_fcm_token

router = APIRouter()

class FcmTokenPayload(BaseModel):
    fcm_token: str

@router.post("/patients/{patient_id}/fcm-token")
async def register_fcm_token(
    patient_id: str = Path(..., description="Firestore 환자 문서 ID"),
    payload: FcmTokenPayload = Body(...),
    user=Depends(get_current_user)
):
    """
    환자 로그인 후 클라이언트에서 받은 FCM 토큰을
    Firestore 'patients/{patient_id}' 문서에 fcm_token 필드로 저장합니다.
    """
    success = save_patient_fcm_token(patient_id, payload.fcm_token)
    if not success:
        raise HTTPException(status_code=500, detail="FCM 토큰 저장 실패")
    return {"message": "FCM 토큰 저장 완료"}