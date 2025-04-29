# app/api/v1/video_calls.py

from fastapi import APIRouter, Depends
from app.services.video_call_service import (
    create_video_call_room,
    start_video_call,
    end_video_call,
    save_video_text
)
from app.core.dependencies import get_current_user

router = APIRouter()

# 영상 통화방 생성
@router.post("/video-call/create")
async def create_call_room(payload: dict, user=Depends(get_current_user)):
    return create_video_call_room(payload)

# 영상 통화 시작
@router.post("/video-call/start")
async def start_call(payload: dict, user=Depends(get_current_user)):
    return start_video_call(payload)

# 영상 통화 종료
@router.post("/video-call/end")
async def end_call(payload: dict, user=Depends(get_current_user)):
    return end_video_call(payload)

# 영상 통화 중 텍스트 저장
@router.post("/video-call/text")
async def save_call_text(payload: dict, user=Depends(get_current_user)):
    return save_video_text(payload)