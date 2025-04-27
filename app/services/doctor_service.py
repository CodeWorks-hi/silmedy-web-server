from firebase_admin import firestore

# 의사 문서 삭제
def delete_doctor_by_license(license_number):
    db = firestore.client()
    collection_doctors = db.collection("doctors")
    
    # license_number로 의사 검색
    docs = collection_doctors.where("license_number", "==", license_number).stream()
    for doc in docs:
        # 문서 삭제
        doc.reference.delete()

# 의사 정보 업데이트
def update_doctor_by_license(license_number, payload):
    db = firestore.client()
    collection_doctors = db.collection("doctors")
    
    # license_number로 의사 검색
    docs = collection_doctors.where("license_number", "==", license_number).stream()
    for doc in docs:
        # 문서 업데이트
        doc.reference.update(payload)

# 의사 문서 등록
def register_doctor(payload):
    db = firestore.client()
    collection_doctors = db.collection("doctors")
    collection_doctors.add(payload)

# 의사 인증 (license_number와 password로 로그인)
def find_doctor_by_credentials(payload):
    db = firestore.client()
    collection_doctors = db.collection("doctors")
    license_number = payload.get("license_number")
    password = payload.get("password")
    if not (license_number and password):
        return None
    docs = collection_doctors.where("license_number", "==", license_number).where("password", "==", password).stream()
    for doc in docs:
        return doc.to_dict()
    return None