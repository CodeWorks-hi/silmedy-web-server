from app.services.doctor_service import find_doctor_by_credentials
from app.services.admin_service import find_admin_by_credentials

def doctor_login(payload: dict):
    doctor = find_doctor_by_credentials(payload)
    if doctor is None:
        raise Exception("의사 로그인 실패")
    return doctor

def admin_login(payload: dict):
    admin = find_admin_by_credentials(payload)
    if admin is None:
        raise Exception("관리자 로그인 실패")
    return admin