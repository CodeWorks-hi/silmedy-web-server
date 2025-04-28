# app/api/v1/care_requests.py

from fastapi import APIRouter
from app.services.care_request_service import (
    get_all_care_requests,
    get_waiting_care_requests
)

router = APIRouter()

@router.get("/care-requests")
async def list_care_requests():
    return {"care_requests": get_all_care_requests()}

@router.get("/care-requests/waiting")
async def list_waiting_care_requests():
    return {"waiting_list": get_waiting_care_requests()}