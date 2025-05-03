from fastapi import APIRouter, Body, HTTPException
from app.services.patient_service import register_fcm_token

router = APIRouter(prefix="/api/v1/patients")

@router.post("/{patient_id}/fcm-token")
async def register_token(patient_id: str, payload: dict = Body(...)):
    token = payload.get("fcm_token")
    if not token:
        raise HTTPException(status_code=400, detail="fcm_token is required")
    await register_fcm_token(patient_id, token)
    return {"message": "FCM 토큰 등록 완료"}
