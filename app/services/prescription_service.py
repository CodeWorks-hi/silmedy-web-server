from app.core.config import dynamodb
from fastapi import HTTPException
from datetime import datetime, timezone, timedelta
from boto3.dynamodb.conditions import Attr

# 한국 시간대
KST = timezone(timedelta(hours=9))
now = datetime.now(KST)
timestamp = now.strftime("%Y%m%d_%H%M%S")

def get_all_prescription_records():
    try:
        table = dynamodb.Table("prescription_records")
        response = table.scan()
        return response.get("Items", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def create_prescription_record(payload: dict):
    try:
        # 1️⃣ counters 테이블에서 prescription_id 카운터 값 증가
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

        item = {
            "prescription_id": prescription_id,
            "diagnosis_id": payload.get("diagnosis_id"),
            "doctor_id": payload.get("doctor_id"),
            "patient_id": payload.get("patient_id"),  # ✅ 추가!!
            "medication_days": payload.get("medication_days"),
            "medication_list": payload.get("medication_list", []),
            "prescribed_at": prescribed_at
        }

        table = dynamodb.Table("prescription_records")
        table.put_item(Item=item)

        return {
            "message": "처방전 저장 완료",
            "prescription_id": prescription_id
        }
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


def get_prescription_records_by_patient_id(patient_id: str):
    try:
        table = dynamodb.Table("prescription_records")
        response = table.scan(
            FilterExpression=Attr("patient_id").eq(patient_id)
        )
        return response.get("Items", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))