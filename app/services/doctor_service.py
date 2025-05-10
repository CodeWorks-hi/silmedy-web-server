# app/services/doctor_service.py

from app.core.config import get_firestore_client, upload_profile_image


# 의사 목록 조회 
def get_all_doctors():
    db = get_firestore_client()  # 함수 호출
    doctors = db.collection("doctors").stream()
    result = []
    for doc in doctors:
        data = doc.to_dict()
        data["license_number"] = doc.id
        result.append(data)
    return result

# 의사 등록
def create_doctor(payload: dict):
    db = get_firestore_client()
    license_number = payload.get("license_number")
    if not license_number:
        raise Exception("license_number는 필수입니다.")

    # 1) 원본 payload 수정하지 않도록 복사
    data = payload.copy()

    # 2) Firestore 필드에서는 license_number 삭제
    data.pop("license_number", None)

    # 3) 문서 ID로만 license_number 사용
    doc_ref = db.collection("doctors").document(license_number)
    if doc_ref.get().exists:
        raise Exception("이미 존재하는 license_number입니다.")

    # 4) 필드에는 data만 저장
    doc_ref.set(data)

    return {"message": "의사 등록 완료", "license_number": license_number}

# 의사 정보 수정 
def update_doctor(license_number: str, payload: dict):
    db = get_firestore_client()  # 함수 호출
    doc_ref = db.collection("doctors").document(license_number)
    if not doc_ref.get().exists:
        raise Exception("해당 의사를 찾을 수 없습니다.")

    doc_ref.update(payload)
    return {"message": "의사 수정 완료", "license_number": license_number}

# 의사 삭제
def delete_doctor(license_number: str):
    db = get_firestore_client()  # 함수 호출
    doc_ref = db.collection("doctors").document(license_number)
    if not doc_ref.get().exists:
        raise Exception("해당 의사를 찾을 수 없습니다.")

    doc_ref.delete()
    return {"message": "의사 삭제 완료", "license_number": license_number}

# 프로필 사진 등록
def set_profile_url(license_number: str, file_bytes: bytes, content_type: str) -> str:
    """
    의사 프로필 사진을 S3에 업로드하고, 해당 URL을 Firestore 문서에 저장한 뒤 반환합니다.

    Args:
      license_number (str): 프로필을 업로드할 의사의 고유 라이센스 번호 (Firestore 문서 ID).
      file_bytes     (bytes): 클라이언트로부터 전달된 이미지 파일의 바이트 스트림.
      content_type   (str): 업로드할 파일의 MIME 타입 (예: "image/jpeg", "image/png").

    Returns:
      str: S3에 업로드된 프로필 사진의 퍼블릭 URL.

    Raises:
      Exception: 해당 라이센스 번호의 의사 문서가 Firestore에 존재하지 않을 경우.
    """

    # 1. Firestore 클라이언트 가져오기
    db = get_firestore_client()

    # 2. 해당 license_number로 doctors 컬렉션 내 문서 참조 생성
    doc_ref = db.collection("doctors").document(license_number)

    # 3. 문서 존재 여부 검사: 없으면 예외 발생
    if not doc_ref.get().exists:
        raise Exception("해당 license_number 의사를 찾을 수 없습니다.")

    # 4. S3에 실제 업로드 처리:
    #    upload_profile_image 함수 내부에서
    #      • 파일명/경로(key) 생성
    #      • boto3 클라이언트를 이용해 S3에 업로드
    #      • 업로드 후 퍼블릭 URL 구성
    #    -> 업로드된 이미지의 URL을 반환받음
    url = upload_profile_image(file_bytes, content_type)

    # 5. Firestore 문서의 profile_url 필드에 방금 생성된 URL 저장 또는 갱신
    doc_ref.update({"profile_url": url})

    # 6. 최종적으로 클라이언트가 사용할 수 있도록 URL을 반환
    return url