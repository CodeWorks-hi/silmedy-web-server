# app/services/doctor_service.py

from app.core.config import get_firestore_client

def get_all_doctors():
    db = get_firestore_client()  # ✅ 함수 호출
    doctors = db.collection("doctors").stream()
    result = []
    for doc in doctors:
        data = doc.to_dict()
        data["license_number"] = doc.id
        result.append(data)
    return result

def create_doctor(payload: dict):
    db = get_firestore_client()  # ✅ 함수 호출
    license_number = payload.get("license_number")
    if not license_number:
        raise Exception("license_number는 필수입니다.")

    doc_ref = db.collection("doctors").document(license_number)
    if doc_ref.get().exists:
        raise Exception("이미 존재하는 license_number입니다.")

    doc_ref.set(payload)
    return {"message": "의사 등록 완료", "license_number": license_number}

def update_doctor(license_number: str, payload: dict):
    db = get_firestore_client()  # ✅ 함수 호출
    doc_ref = db.collection("doctors").document(license_number)
    if not doc_ref.get().exists:
        raise Exception("해당 의사를 찾을 수 없습니다.")

    doc_ref.update(payload)
    return {"message": "의사 수정 완료", "license_number": license_number}

def delete_doctor(license_number: str):
    db = get_firestore_client()  # ✅ 함수 호출
    doc_ref = db.collection("doctors").document(license_number)
    if not doc_ref.get().exists:
        raise Exception("해당 의사를 찾을 수 없습니다.")

    doc_ref.delete()
    return {"message": "의사 삭제 완료", "license_number": license_number}