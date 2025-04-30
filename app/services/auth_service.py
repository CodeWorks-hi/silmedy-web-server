# ✅ app/services/auth_service.py

from app.core.config import get_firestore_client
from app.core.security import create_access_token

# 🔸 로그인 처리 (의사 / 관리자)
def login_user(payload: dict):
    role = payload.get("role")
    hospital_id = payload.get("hospital_id")
    password = payload.get("password")
    db = get_firestore_client()
    print("🚀 받은 payload:", payload)

    if role == "doctor":
        license_number = payload.get("license_number")
        department = payload.get("department")

        doc_ref = db.collection("doctors").document(license_number)
        doc = doc_ref.get()
        if not doc.exists:
            raise Exception("의사를 찾을 수 없습니다.")

        doctor = doc.to_dict()

        if (
            doctor.get("hospital_id") != hospital_id or
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
        doc_ref = db.collection("admins").document(str(hospital_id))
        doc = doc_ref.get()
        if not doc.exists:
            raise Exception("관리자를 찾을 수 없습니다.")

        admin = doc.to_dict()

        if admin.get("password") != password:
            raise Exception("관리자 인증 실패")

        token_data = {
            "admin_id": hospital_id,
            "hospital_id": hospital_id,
            "role": "admin"
        }
        access_token = create_access_token(data=token_data)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "admin": {
                "hospital_id": hospital_id
            }
        }

    else:
        raise Exception("잘못된 role입니다.")