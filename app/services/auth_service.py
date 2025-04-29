# app/services/auth_service.py

from app.core.config import get_firestore_client
from app.core.security import create_access_token

def login_user(payload: dict):
    role = payload.get("role")
    db = get_firestore_client()  # ✅ 여기 추가!

    if role == "doctor":
        public_health_center = payload.get("public_health_center")
        department = payload.get("department")
        license_number = payload.get("license_number")
        password = payload.get("password")

        doc_ref = db.collection("doctors").document(license_number)
        doc = doc_ref.get()
        if not doc.exists:
            raise Exception("의사를 찾을 수 없습니다.")

        doctor = doc.to_dict()

        if (
            doctor.get("public_health_center") != public_health_center or
            doctor.get("department") != department or
            doctor.get("password") != password
        ):
            raise Exception("의사 인증 실패")

        token_data = {
            "license_number": license_number,
            "hospital_id": doctor.get("hospital_id"),
            "role": "doctor"
        }
        access_token = create_access_token(data=token_data)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "doctor": {
                "name": doctor.get("name"),
                "email": doctor.get("email"),
                "department": doctor.get("department"),
                "hospital_id": doctor.get("hospital_id")
            }
        }

    elif role == "admin":
        public_health_center = payload.get("public_health_center")
        password = payload.get("password")

        docs = get_firestore_client.collection("admins").where(
            "public_health_center", "==", public_health_center
        ).stream()

        admin = None
        for doc in docs:
            admin_candidate = doc.to_dict()
            if admin_candidate.get("password") == password:
                admin = admin_candidate
                admin["admin_id"] = doc.id
                break

        if admin is None:
            raise Exception("관리자 인증 실패")

        token_data = {
            "admin_id": admin.get("admin_id"),
            "hospital_id": admin.get("hospital_id"),
            "role": "admin"
        }
        access_token = create_access_token(data=token_data)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "admin": {
                "name": admin.get("name"),
                "email": admin.get("email"),
                "hospital_id": admin.get("hospital_id")
            }
        }

    else:
        raise Exception("role이 잘못되었습니다.")