# app/services/prescription_service.py

from app.core.config import dynamodb
from fastapi import HTTPException
from datetime import datetime, timezone, timedelta
from boto3.dynamodb.conditions import Key
import random

# 한국 시간대 설정
KST = timezone(timedelta(hours=9))
now = datetime.now(KST)

# 🔵 처방전 전체 조회
def get_all_prescription_records():
    try:
        table = dynamodb.Table("prescription_records")
        response = table.scan()
        return response.get("Items", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🔵 처방전 등록
def create_prescription(payload: dict):
    try:
        # 1️⃣ 카운터 테이블에서 prescription_id 증가
        counter_table = dynamodb.Table("counters")
        counter_response = counter_table.update_item(
            Key={"counter_name": "prescription_id"},
            UpdateExpression="SET current_id = if_not_exists(current_id, :start) + :inc",
            ExpressionAttributeValues={
                ":start": 1,
                ":inc": 1
            },
            ReturnValues="UPDATED_NEW"
        )

        prescription_id = int(counter_response["Attributes"]["current_id"])
        prescribed_at = now.strftime("%Y-%m-%d %H:%M:%S")

        # 2️⃣ 테이블에 저장
        table = dynamodb.Table("prescription_records")
        item = {
            "prescription_id": prescription_id,
            "diagnosis_id": payload.get("diagnosis_id"),
            "doctor_id": payload.get("doctor_id"),
            "patient_id": payload.get("patient_id"),
            "medication_days": payload.get("medication_days"),
            "medication_list": payload.get("medication_list"),  # 복수의 약품 객체들
            "prescribed_at": prescribed_at
        }

        table.put_item(Item=item)
        return {
            "message": "처방전 저장 완료",
            "prescription_id": prescription_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🔵 특정 환자의 처방전만 조회 (옵션)
def get_prescription_records_by_patient_id(patient_id: str):
    try:
        table = dynamodb.Table("prescription_records")
        response = table.scan(
            FilterExpression=Key("patient_id").eq(patient_id)
        )
        return response.get("Items", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
