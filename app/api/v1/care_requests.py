# app/api/v1/care_requests.py

from fastapi import APIRouter, Depends
from app.services.care_request_service import (
    get_all_care_requests,
    create_care_request,
    update_care_request,
    delete_care_request,
    get_waiting_care_requests
)
from app.core.dependencies import get_current_user

router = APIRouter()

@router.get("/care-requests")
async def read_care_requests(user=Depends(get_current_user)):
    return {"care_requests": get_all_care_requests()}

@router.post("/care-requests")
async def create_care(payload: dict, user=Depends(get_current_user)):
    return create_care_request(payload)

@router.put("/care-requests/{care_request_id}")
async def update_care(care_request_id: str, payload: dict, user=Depends(get_current_user)):
    return update_care_request(care_request_id, payload)

@router.delete("/care-requests/{care_request_id}")
async def delete_care(care_request_id: str, user=Depends(get_current_user)):
    return delete_care_request(care_request_id)

@router.get("/care-requests/waiting")
async def get_waiting_care(user=Depends(get_current_user)):
    return {"waiting_list": get_waiting_care_requests()}