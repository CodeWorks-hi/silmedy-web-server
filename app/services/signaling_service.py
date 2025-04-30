from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.services.signaling_service import save_offer, save_answer, add_ice_candidate

router = APIRouter()

@router.post("/video-call/offer")
async def post_offer(room_id: str, sdp: dict, user=Depends(get_current_user)):
    return save_offer(room_id, sdp)

@router.post("/video-call/answer")
async def post_answer(room_id: str, sdp: dict, user=Depends(get_current_user)):
    return save_answer(room_id, sdp)

@router.post("/video-call/candidate")
async def post_candidate(room_id: str, role: str, candidate: dict, user=Depends(get_current_user)):
    return add_ice_candidate(room_id, role, candidate)