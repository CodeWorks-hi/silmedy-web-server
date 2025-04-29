# app/services/care_request_service.py

from app.core.config import dynamodb
from firebase_admin import firestore
from boto3.dynamodb.conditions import Attr
from fastapi import HTTPException
from decimal import Decimal

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

def get_all_care_requests():
    try:
        table = dynamodb.Table("care_requests")
        response = table.scan()
        return {"care_requests": decimal_to_native(response.get("Items", []))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_waiting_care_requests():
    try:
        table = dynamodb.Table("care_requests")
        response = table.scan(FilterExpression=Attr("is_solved").eq(False))
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

            # ✅ 원본 care_request 데이터 복사
            combined = dict(request)

            # ✅ 환자 정보 추가
            combined.update({
                "name": patient_data.get("name"),
                "birth_date": patient_data.get("birth_date")
            })

            result.append(combined)

        return {"waiting_list": decimal_to_native(result)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))