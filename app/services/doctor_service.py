# app/services/doctor_service.py

from app.core.config import get_firestore_client, upload_profile_image, set_profile_url
from botocore.exceptions import ClientError


def get_doctors_by_hospital(hospital_id: str):
    db = get_firestore_client()
    docs = db.collection("doctors").where("hospital_id", "==", hospital_id).stream()
    result = []
    for doc in docs:
        data = doc.to_dict()
        data["license_number"] = doc.id
        result.append(data)
    return result

def create_doctor(payload: dict):
    db = get_firestore_client()
    license_number = payload.get("license_number")
    if not license_number:
        raise Exception("license_number는 필수입니다.")
    data = payload.copy()
    data.pop("license_number", None)
    doc_ref = db.collection("doctors").document(license_number)
    if doc_ref.get().exists:
        raise Exception("이미 존재하는 license_number입니다.")
    doc_ref.set(data)
    return {"message": "의사 등록 완료", "license_number": license_number}

def update_doctor(license_number: str, payload: dict):
    db = get_firestore_client()
    doc_ref = db.collection("doctors").document(license_number)
    if not doc_ref.get().exists:
        raise Exception("해당 의사를 찾을 수 없습니다.")
    doc_ref.update(payload)
    return {"message": "의사 수정 완료", "license_number": license_number}

def delete_doctor(license_number: str):
    db = get_firestore_client()
    doc_ref = db.collection("doctors").document(license_number)
    if not doc_ref.get().exists:
        raise Exception("해당 의사를 찾을 수 없습니다.")
    doc_ref.delete()
    return {"message": "의사 삭제 완료", "license_number": license_number}

def upload_doctor_profile_service(
    license_number: str, file_bytes: bytes, content_type: str
) -> str:
    """
    기존 사진 삭제 → 새 사진 업로드 → Firestore 갱신 → URL 반환
    """
    try:
        return set_profile_url(license_number, file_bytes, content_type)
    except ClientError as e:
        # S3 오류 로깅
        raise
    except Exception:
        raise