from fastapi import APIRouter
from app.services.disease_service import get_all_diseases

router = APIRouter()

@router.get("/diseases")
async def list_diseases():
    return {"diseases": get_all_diseases()}