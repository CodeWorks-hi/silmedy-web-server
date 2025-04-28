from app.core.config import dynamodb, db
from boto3.dynamodb.conditions import Attr
from fastapi import HTTPException
from decimal import Decimal

# 패시보 : Decimal 형식 값 바꾸기
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

# 패시보 : 전체 개발 가져오기 (DynamoDB)
def get_all_care_requests():
    try:
        table = dynamodb.Table("care_requests")
        response = table.scan()
        items = response.get("Items", [])
        return decimal_to_native(items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 패시보 : 대기중개+환자정보 배열 합칠기
def get_waiting_care_requests():
    try:
        table = dynamodb.Table("care_requests")
        response = table.scan(FilterExpression=Attr("is_solved").eq(False))
        care_requests = response.get("Items", [])

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
                "symptom_type": request.get("symptom_type", [])
            }
            result.append(combined)

        return decimal_to_native(result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))