# app/services/doctor_service.py

from firebase_admin import firestore
from fastapi import HTTPException
from datetime import datetime
from uuid import uuid4
from app.core.config import table_hospitals  # 🔥 추가
from boto3.dynamodb.conditions import Attr  # 🔥 추가

# 모든 의사 가져오기 (문서 ID를 license_number 필드에 추가)
def get_all_doctors():
    db = firestore.client()
    docs = db.collection("doctors").stream()
    doctors = []
    for doc in docs:
        data = doc.to_dict()
        data["license_number"] = doc.id  # 문서 ID를 license_number로 추가
        doctors.append(data)
    return doctors

# 문서 ID(license_number)로 의사 삭제
def delete_doctor_by_license(license_number: str):
    db = firestore.client()
    doc_ref = db.collection("doctors").document(license_number)
    snapshot = doc_ref.get()
    if not snapshot.exists:
        raise HTTPException(status_code=404, detail="해당 의사를 찾을 수 없습니다.")
    doc_ref.delete()

# 문서 ID(license_number)로 의사 정보 업데이트
def update_doctor_by_license(license_number: str, payload: dict):
    db = firestore.client()
    doc_ref = db.collection("doctors").document(license_number)
    snapshot = doc_ref.get()
    if not snapshot.exists:
        raise HTTPException(status_code=404, detail="해당 의사를 찾을 수 없습니다.")
    doc_ref.update(payload)

# 🔵 수정: 새 의사 문서 등록 (hospital_name → hospital_id 변환)
def register_doctor(payload: dict):
    try:
        db = firestore.client()

        # DynamoDB hospitals 테이블에서 hospital_id 찾기
        hospital_name = payload.get("hospital_name")
        if not hospital_name:
            raise ValueError("hospital_name이 없습니다.")

        response = table_hospitals.scan(
            FilterExpression=Attr("name").eq(hospital_name)
        )
        items = response.get("Items", [])
        if not items:
            raise ValueError("보건소 정보가 없습니다.")

        hospital_id = int(items[0]["hospital_id"])

        # 직접 생성하는 문서 ID
        license_number = str(uuid4().int)[:6]

        # Firestore 문서 등록
        db.collection("doctors").document(license_number).set({
            "hospital_id": hospital_id,
            "name": payload["name"],
            "email": payload["email"],
            "password": payload["password"],
            "department": payload["department"],
            "contact": payload["contact"],
            "gender": payload.get("gender", ""),
            "profile_url": payload.get(
                "profile_url",
                "https://cdn-icons-png.flaticon.com/512/3870/3870822.png"  # 기본 프로필
            ),
            "bio": payload.get("bio", []),
            "availability": payload.get("availability", {}),
            "created_at": datetime.utcnow().isoformat()
        })

        return {
            "message": "의사 등록 완료",
            "license_number": license_number
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 로그인: 문서 ID로 조회 후 비밀번호 + 과(department) 검증
def find_doctor_by_credentials(payload):
    db = firestore.client()
    license_number = payload.get("license_number")
    password = payload.get("password")
    department = payload.get("department")

    if not (license_number and password and department):
        return None

    doc_ref = db.collection("doctors").document(license_number)
    snapshot = doc_ref.get()
    if not snapshot.exists:
        return None

    data = snapshot.to_dict()

    # 비밀번호 검증
    if data.get("password") != password:
        return None

    # 과(department) 검증
    saved_department = data.get("department")
    if not saved_department:
        return None

    # 양쪽 다 소문자/공백제거해서 비교
    if saved_department.strip().lower() != department.strip().lower():
        return None

    data["license_number"] = snapshot.id
    return data