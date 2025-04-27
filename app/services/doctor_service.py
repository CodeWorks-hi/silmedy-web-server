# app/services/doctor_service.py

from firebase_admin import firestore
from fastapi import HTTPException

# 모든 의사 가져오기 (문서 ID를 license_number 필드에 추가)
def get_all_doctors():
    db = firestore.client()
    docs = db.collection("doctors").stream()
    doctors = []
    for doc in docs:
        data = doc.to_dict()
        # Firestore 문서 ID를 license_number 로 포함
        data["license_number"] = doc.id
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

# 새 의사 문서 등록 (문서 ID는 Firestore가 자동 생성)
def register_doctor(payload: dict):
    db = firestore.client()
    db.collection("doctors").add(payload)

# 로그인: 문서 ID로 조회 후 비밀번호 검증
def find_doctor_by_credentials(payload: dict):
    db = firestore.client()
    license_number = payload.get("license_number")
    password = payload.get("password")
    if not (license_number and password):
        return None

    doc_ref = db.collection("doctors").document(license_number)
    snapshot = doc_ref.get()
    if not snapshot.exists:
        return None

    data = snapshot.to_dict()
    # 비밀번호 확인
    if data.get("password") != password:
        return None

    # 로그인 성공 시에도 문서 ID를 license_number 필드에 포함
    data["license_number"] = snapshot.id
    return data