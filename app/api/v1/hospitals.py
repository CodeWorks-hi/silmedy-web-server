from fastapi import APIRouter
from app.services.hospital_service import get_all_hospitals

router = APIRouter()

@router.get("/hospitals")
async def get_hospitals():
    return {"hospitals": get_all_hospitals()}