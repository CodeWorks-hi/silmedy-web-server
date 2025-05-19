# app/api/v1/prescriptions.py

from fastapi import APIRouter, Depends, HTTPException, Path, Body
from app.services.prescription_service import create_prescription, update_prescription_url
from app.core.dependencies import get_current_user

router = APIRouter()

# 처방전 등록 API
@router.post(
    "/prescriptions",
    tags=["의사 - 처방 관리"],
    summary="처방전을 등록합니다.",
    description="특정 진단 ID에 대한 처방전을 생성하는 기능입니다."
)
async def register_prescription(payload: dict, user=Depends(get_current_user)):
    try:
        return create_prescription(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # ★ 추가: URL 업데이트용 PATCH 엔드포인트
@router.patch(
    "/prescriptions/{prescription_id}/url",
    tags=["의사 - 처방 관리"],
    summary="처방전 이미지를 업데이트합니다.",
    description="기존에 생성된 처방전의 prescription_url 필드를 수정하는 기능입니다.",
)
async def patch_prescription_url(
    prescription_id: int = Path(..., description="처방전 ID"),
    body: dict = Body(..., example={"prescription_url": "https://.../123.png"}),
    user=Depends(get_current_user),
):
    url = body.get("prescription_url")
    if not url:
        raise HTTPException(status_code=400, detail="prescription_url is required")

    try:
        return update_prescription_url(prescription_id, url)
    except KeyError:
        raise HTTPException(status_code=404, detail="Prescription not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))