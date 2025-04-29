from app.core.config import dynamodb
from fastapi import HTTPException
from boto3.dynamodb.conditions import Attr
from datetime import datetime, timezone, timedelta
import random

# 한국 시간대
KST = timezone(timedelta(hours=9))
now = datetime.now(KST)
timestamp = now.strftime("%Y%m%d_%H%M%S")
random_suffix = f"{random.randint(0, 999):03d}"

def get_all_diagnosis_records():
    try:
        table = dynamodb.Table("diagnosis_records")
        response = table.scan()
        return response.get("Items", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def create_diagnosis(payload: dict):
    try:
        diagnosis_id = int(f"{timestamp}{random_suffix}")
        diagnosed_at = now.strftime("%Y-%m-%d %H:%M:%S")

        table = dynamodb.Table("diagnosis_records")
        item = {
            "diagnosis_id": diagnosis_id,
            "doctor_id": payload.get("doctor_id"),
            "patient_id": payload.get("patient_id"),
            "disease_code": payload.get("disease_code"),
            "diagnosis_text": payload.get("diagnosis_text", ""),
            "diagnosed_at": diagnosed_at
        }

        table.put_item(Item=item)

        return {
            "message": "진단 기록 저장 완료",
            "diagnosis_id": diagnosis_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_diagnosis_by_patient_id(patient_id: str):
    try:
        table = dynamodb.Table("diagnosis_records")
        response = table.scan(
            FilterExpression=Attr("patient_id").eq(patient_id)
        )
        return response.get("Items", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))