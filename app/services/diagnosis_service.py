# app/services/diagnosis_service.py

from app.core.config import dynamodb
from fastapi import HTTPException
from boto3.dynamodb.conditions import Attr
from datetime import datetime, timezone, timedelta

# 한국 시간대 설정
KST = timezone(timedelta(hours=9))

# 전체 진단 기록 조회
def get_all_diagnosis_records():
    try:
        table = dynamodb.Table("diagnosis_records")
        response = table.scan()
        return response.get("Items", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 특정 환자의 진단 이력 조회
def get_diagnosis_by_patient_id(patient_id: str):
    try:
        table = dynamodb.Table("diagnosis_records")
        response = table.scan(
            FilterExpression=Attr("patient_id").eq(patient_id) 
        )
        return response.get("Items", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 진단 기록 생성
def create_diagnosis(payload: dict):
    try:
        # 현재 시간 가져오기 (요청 시각)
        now = datetime.now(KST)
        diagnosed_at = now.strftime("%Y-%m-%d %H:%M:%S")

        # 1️⃣ counters 테이블에서 diagnosis_id 증가
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

        # 2️⃣ diagnosis_records 테이블에 진단 기록 저장
        diagnosis_table = dynamodb.Table("diagnosis_records")
        item = {
            "diagnosis_id": diagnosis_id,
            "doctor_id": payload.get("doctor_id"),
            "patient_id": int(payload.get("patient_id")),
            "disease_code": payload.get("disease_code"),
            "diagnosis_text": payload.get("diagnosis_text", ""),
            "prescription": payload.get("prescription", []),  # 처방 리스트 저장
            "diagnosed_at": diagnosed_at
        }

        diagnosis_table.put_item(Item=item)

        return {
            "message": "진단 기록 저장 완료",
            "diagnosis_id": diagnosis_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))