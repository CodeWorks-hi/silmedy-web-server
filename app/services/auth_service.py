# app/services/auth_service.py

from app.core.config import get_firestore_client, init_firebase
from app.core.security import create_access_token
from firebase_admin import auth

# Firebase initialize (1회만)
init_firebase()

# ❁ Firebase Custom Token 발급 함수
def issue_firebase_token(uid: str) -> str:
    custom_token = auth.create_custom_token(uid)
    return custom_token.decode("utf-8")


def login_user(payload: dict):
    role = payload.get("role")
    hospital_id = payload.get("hospital_id")
    password = payload.get("password")
    db = get_firestore_client()
    print("🚀 받은 payload:", payload)

    if role == "doctor":
        license_number = payload.get("license_number")
        department     = payload.get("department")
        # string → int 변환
        try:
            hospital_id = int(payload.get("hospital_id"))
        except:
            raise ValueError("올바른 병원 ID를 입력하세요.")

        doc_ref = db.collection("doctors").document(license_number)
        doc     = doc_ref.get()
        if not doc.exists:
            raise PermissionError("등록된 의사가 아닙니다.")

        doctor = doc.to_dict()

        # (1) 병원 ID 비교: both int
        if doctor.get("hospital_id") != hospital_id:
            raise PermissionError("의사 인증 실패 (병원 불일치)")

        # (2) department 체크 필요 없으면 제거
        # if doctor.get("department") != department:
        #     raise PermissionError("의사 인증 실패 (과 불일치)")

        # (3) 비밀번호만 비교
        if doctor.get("password") != password:
            raise PermissionError("의사 인증 실패 (비밀번호 불일치)")

        token_data = {
            "license_number": license_number,
            "hospital_id": doctor.get("hospital_id"),
            "role": "doctor"
        }
        access_token = create_access_token(data=token_data)
        firebase_token = issue_firebase_token(license_number)

        return {
            "access_token": access_token,
            "firebase_token": firebase_token,
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
        firebase_token = issue_firebase_token(f"admin_{hospital_id}")

        return {
            "access_token": access_token,
            "firebase_token": firebase_token,
            "token_type": "bearer",
            "admin": {
                "hospital_id": hospital_id
            }
        }

    else:
        raise Exception("잘못된 role입니다.")
