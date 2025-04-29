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
        # 1️⃣ counters 테이블에서 diagnosis_id 카운터 값 증가
        counter_table = dynamodb.Table("counters")
        counter_response = counter_table.update_item(
            Key={"counter_name": "diagnosis_id"},
            UpdateExpression="SET current_id = if_not_exists(current_id, :start) + :inc",
            ExpressionAttributeValues={
                ":start": 1,
                ":inc": 1
            },
            ReturnValues="UPDATED_NEW"
        )

        diagnosis_id = int(counter_response["Attributes"]["current_id"])
        diagnosed_at = now.strftime("%Y-%m-%d %H:%M:%S")

        # 2️⃣ diagnosis_records 테이블에 새로운 진단 기록 저장
        diagnosis_table = dynamodb.Table("diagnosis_records")
        item = {
            "diagnosis_id": diagnosis_id,
            "doctor_id": payload.get("doctor_id"),
            "patient_id": payload.get("patient_id"),
            "disease_code": payload.get("disease_code"),
            "diagnosis_text": payload.get("diagnosis_text", ""),
            "diagnosed_at": diagnosed_at
        }

        diagnosis_table.put_item(Item=item)

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