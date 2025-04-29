# app/services/prescription_service.py

from app.core.config import dynamodb
from fastapi import HTTPException
from boto3.dynamodb.conditions import Attr
from datetime import datetime, timezone, timedelta
import random

# 한국 시간
KST = timezone(timedelta(hours=9))
now = datetime.now(KST)
timestamp = now.strftime("%Y%m%d_%H%M%S")
random_suffix = f"{random.randint(0, 999):03d}"

def get_all_prescription_records():
    try:
        table = dynamodb.Table("prescription_records")
        response = table.scan()
        return response.get("Items", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def create_prescription_record(payload: dict):
    try:
        prescription_id = int(f"{timestamp}{random_suffix}")
        prescribed_at = now.strftime("%Y-%m-%d %H:%M:%S")

        item = {
            "prescription_id": prescription_id,
            "diagnosis_id": payload.get("diagnosis_id"),
            "doctor_id": payload.get("doctor_id"),
            "medication_days": payload.get("medication_days"),
            "medication_list": payload.get("medication_list", []),
            "prescribed_at": prescribed_at
        }

        table = dynamodb.Table("prescription_records")
        table.put_item(Item=item)

        return {"message": "처방전 저장 완료", "prescription_id": prescription_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def update_prescription_record(prescription_id: str, payload: dict):
    try:
        table = dynamodb.Table("prescription_records")
        update_expression = "SET " + ", ".join(f"#{k}=:{k}" for k in payload.keys())
        expression_attribute_names = {f"#{k}": k for k in payload.keys()}
        expression_attribute_values = {f":{k}": v for k, v in payload.items()}

        table.update_item(
            Key={"prescription_id": int(prescription_id)},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values
        )
        return {"message": "처방전 수정 완료"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def delete_prescription_record(prescription_id: str):
    try:
        table = dynamodb.Table("prescription_records")
        table.delete_item(Key={"prescription_id": int(prescription_id)})
        return {"message": "처방전 삭제 완료"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))