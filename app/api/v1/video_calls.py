from fastapi import APIRouter
from app.services.video_call_service import (
    create_video_call,
    start_video_call,
    end_video_call,
    save_text_message
)

router = APIRouter()

@router.post("/video-call/create")
async def create_call(payload: dict):
    return create_video_call(payload)

@router.post("/video-call/start")
async def start_call(payload: dict):
    return start_video_call(payload)

@router.post("/video-call/end")
async def end_call(payload: dict):
    return end_video_call(payload)

@router.post("/video-call/text")
async def send_text(payload: dict):
    return save_text_message(payload)