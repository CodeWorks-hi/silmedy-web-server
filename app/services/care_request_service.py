# app/services/care_request_service.py

from app.core.config import dynamodb
from firebase_admin import firestore
from boto3.dynamodb.conditions import Attr
from fastapi import HTTPException
from decimal import Decimal
from datetime import datetime, timezone, timedelta




# 한국 시간대 설정
KST = timezone(timedelta(hours=9))



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

def get_waiting_care_requests_by_doctor(doctor_id: int):
    try:
        db = firestore.client()
        table = dynamodb.Table("care_requests")

        response = table.scan(
            FilterExpression=Attr("is_solved").eq(False) & Attr("doctor_id").eq(doctor_id)
        )
        care_requests = response.get("Items", [])
        result = []

        for request in care_requests:
            patient_id = request.get("patient_id")
            if not patient_id:
                continue

            patient_doc = db.collection("patients").document(str(patient_id)).get()
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
                "symptom_type": request.get("symptom_type", [])
            }
            result.append(combined)

        return decimal_to_native(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# 🔵 진료 완료 처리 함수
def complete_care_request(request_id: int):
    try:
        table = dynamodb.Table("care_requests")
        now = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")

        # request_id로 항목 업데이트
        table.update_item(
            Key={"request_id": request_id},
            UpdateExpression="SET is_solved = :true_val, solved_at = :now_time",
            ExpressionAttributeValues={
                ":true_val": True,
                ":now_time": now
            }
        )

        return {"message": "진료 완료 처리되었습니다.", "request_id": request_id, "solved_at": now}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))