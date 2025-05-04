# app/api/v1/video_calls.py

from fastapi import APIRouter, Depends
from app.services.video_call_service import (
    create_video_call,
    start_video_call,
    end_video_call,
    save_text_message,
    save_answer,
    reject_call
)
from app.core.dependencies import get_current_user

router = APIRouter()

@router.post("/create")
async def create_call_room(payload: dict, user=Depends(get_current_user)):
    return create_video_call(payload)

@router.post("/start")
async def start_call(payload: dict, user=Depends(get_current_user)):
    try:
        return start_video_call(payload)
    except Exception as e:
        import traceback; traceback.print_exc()
        raise  # or HTTPException(500, detail=str(e))

@router.post("/answer")
async def post_answer(payload: dict, user=Depends(get_current_user)):
    # payload = { "call_id": "...", "sdp": { ... } }
    return save_answer(payload)

@router.post("/reject")
async def post_reject(payload: dict, user=Depends(get_current_user)):
    # payload = { "call_id": "...", "reason": "busy" }
    return reject_call(payload)

@router.post("/end")
async def end_call(payload: dict, user=Depends(get_current_user)):
    return end_video_call(payload)

@router.post("/text")
async def save_call_text(payload: dict, user=Depends(get_current_user)):
    return save_text_message(payload)