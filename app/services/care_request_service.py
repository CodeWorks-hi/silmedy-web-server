# app/services/care_request_service.py

from firebase_admin import firestore
from app.core.config import dynamodb
from boto3.dynamodb.conditions import Attr
from fastapi import HTTPException

# 🔵 전체 케어 요청 가져오기 (그대로 사용)
def get_all_care_requests():
    db = firestore.client()
    collection_care_requests = db.collection("care_requests")
    docs = collection_care_requests.stream()
    return [doc.to_dict() for doc in docs]

# 🆕 대기중인 케어 요청 + 환자 정보 병합해서 가져오기
def get_waiting_care_requests():
    try:
        table_care_requests = dynamodb.Table("care_requests")
        response = table_care_requests.scan(
            FilterExpression=Attr("is_solved").eq(False)
        )
        care_requests = response.get("Items", [])

        db = firestore.client()
        result = []

        for request in care_requests:
            patient_id = request.get("patient_id")
            if not patient_id:
                continue

            patient_doc = db.collection("patients").document(patient_id).get()
            if not patient_doc.exists:
                continue

            patient_data = patient_doc.to_dict()

            combined = {
                "request_id": request.get("request_id"),
                "name": patient_data.get("name"),
                "sign_language_needed": request.get("sign_language_needed", False),
                "birth_date": patient_data.get("birth_date"),
                "department": request.get("department"),
                "book_date": request.get("book_date"),
                "book_hour": request.get("book_hour"),
                "symptom_part": request.get("symptom_part", []),
                "symptom_type": request.get("symptom_type", []),
            }
            result.append(combined)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    