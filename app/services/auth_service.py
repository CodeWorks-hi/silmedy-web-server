# app/services/auth_service.py

from app.services.doctor_service import find_doctor_by_credentials
from app.services.admin_service import find_admin_by_credentials
from app.core.security import create_access_token

def doctor_login(payload: dict):
    doctor = find_doctor_by_credentials(payload)
    if doctor is None:
        raise Exception("의사 로그인 실패")

    token_data = {
        "doctor_id": doctor.get("license_number"),
        "hospital_id": doctor.get("hospital_id"),
        "role": "doctor"
    }
    access_token = create_access_token(data=token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "name": doctor.get("name"),
            "email": doctor.get("email"),
            "department": doctor.get("department"),
            "hospital_id": doctor.get("hospital_id")
        }
    }

def admin_login(payload: dict):
    admin = find_admin_by_credentials(payload)
    if admin is None:
        raise Exception("관리자 로그인 실패")

    token_data = {
        "admin_id": admin.get("admin_id"),
        "hospital_id": admin.get("hospital_id"),
        "role": "admin"
    }
    access_token = create_access_token(data=token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "name": admin.get("name"),
            "email": admin.get("email"),
            "hospital_id": admin.get("hospital_id")
        }
    }