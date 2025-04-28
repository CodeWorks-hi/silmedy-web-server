from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from decimal import Decimal
from app.core.firebase import db  # 너희 프로젝트에 맞게 import
import boto3
from boto3.dynamodb.conditions import Attr

router = APIRouter()

# 🔵 DynamoDB 연결 (이미 되어 있다면 이건 생략)
dynamodb = boto3.resource("dynamodb")

# 🔵 Decimal 변환 함수
def decimal_to_native(obj):
    if isinstance(obj, list):
        return [decimal_to_native(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: decimal_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj

# 🔵 진료신청 전체 목록 조회
@router.get("/care-requests")
async def list_care_requests():
    table = dynamodb.Table("care_requests")
    response = table.scan()
    items = response.get("Items", [])
    return {"care_requests": decimal_to_native(items)}

# 🔵 진료 대기자(대기 중 + 환자정보까지 합치기)
@router.get("/care-requests/waiting")
async def list_waiting_care_requests():
    table = dynamodb.Table("care_requests")
    response = table.scan(FilterExpression=Attr("is_solved").eq(False))
    care_requests = response.get("Items", [])

    result = []
    for request in care_requests:
        patient_id = request.get("patient_id")
        if not patient_id:
            continue

        # 🔵 Firestore에서 환자정보 조회
        patient_doc = db.collection("patients").document(patient_id).get()
        if not patient_doc.exists:
            continue

        patient_data = patient_doc.to_dict()

        # 🔵 병합 데이터 만들기
        combined = {
            "request_id": request.get("request_id"),
            "name": patient_data.get("name"),
            "sign_language_needed": request.get("sign_language_needed", False),
            "birth_date": patient_data.get("birth_date", None),
            "department": request.get("department"),
            "book_date": request.get("book_date"),
            "book_hour": request.get("book_hour"),
            "symptom_part": request.get("symptom_part", []),
            "symptom_type": request.get("symptom_type", [])
        }
        result.append(combined)

    return {"waiting_list": decimal_to_native(result)}