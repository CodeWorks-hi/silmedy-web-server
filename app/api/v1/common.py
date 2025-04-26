from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def read_root():
    return {"message": "테스트 성공"}