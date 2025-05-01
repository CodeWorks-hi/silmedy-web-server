# app/services/care_request_service.py

from app.core.config import dynamodb
from firebase_admin import firestore
from boto3.dynamodb.conditions import Attr
from fastapi import HTTPException
from decimal import Decimal
from datetime import datetime, timezone, timedelta

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

def get_waiting_care_requests_by_doctor(current_user: dict):
    try:
        doctor_id = int(current_user.get("license_number"))  # ✅ 숫자로 변환

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
                "symptom_type": request.get("symptom_type", []),
                "patient_id": request.get("patient_id"),
                "doctor_id": request.get("doctor_id")
            }
            result.append(combined)

        return decimal_to_native(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def complete_care_request(request_id: int):
    try:
        table = dynamodb.Table("care_requests")
        now = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
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

def get_care_request_detail(request_id: int):
    try:
        table = dynamodb.Table("care_requests")
        db = firestore.client()

        response = table.get_item(Key={"request_id": request_id})
        item = response.get("Item")
        if not item:
            raise HTTPException(status_code=404, detail="해당 진료 요청을 찾을 수 없습니다.")

        patient_id = item.get("patient_id")
        if not patient_id:
            raise HTTPException(status_code=404, detail="환자 정보가 없습니다.")

        patient_doc = db.collection("patients").document(str(patient_id)).get()
        if not patient_doc.exists:
            raise HTTPException(status_code=404, detail="환자 문서를 찾을 수 없습니다.")

        patient_data = patient_doc.to_dict()

        combined = {
            "request_id": item.get("request_id"),
            "patient_id": patient_id,
            "department": item.get("department"),
            "book_date": item.get("book_date"),
            "book_hour": item.get("book_hour"),
            "symptom_part": item.get("symptom_part", []),
            "symptom_type": item.get("symptom_type", []),
            "is_solved": item.get("is_solved", False),
            "requested_at": item.get("requested_at"),
            "name": patient_data.get("name"),
            "birth_date": patient_data.get("birth_date"),
            "contact": patient_data.get("contact"),
        }

        return decimal_to_native(combined)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
