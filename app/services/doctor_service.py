from firebase_admin import firestore

def get_all_doctors():
    db = firestore.client()
    collection_doctors = db.collection("doctors")
    docs = collection_doctors.stream()
    return [doc.to_dict() for doc in docs]

# 의사 문서 삭제
def delete_doctor_by_license(license_number):
    db = firestore.client()
    collection_doctors = db.collection("doctors")
    docs = collection_doctors.where("license_number", "==", license_number).stream()

    for doc in docs:
        doc_id = doc.id
        print(f"Deleting doctor doc ID = {doc_id}")
        doc.reference.delete()

# 의사 정보 업데이트
def update_doctor_by_license(license_number, payload):
    db = firestore.client()
    collection_doctors = db.collection("doctors")
    docs = collection_doctors.where("license_number", "==", license_number).stream()

    for doc in docs:
        doc_id = doc.id
        print(f"Updating doctor doc ID = {doc_id} with {payload}")
        doc.reference.update(payload)

def register_doctor(payload):
    db = firestore.client()
    collection_doctors = db.collection("doctors")
    collection_doctors.add(payload)

# 의사로그인
def find_doctor_by_credentials(payload):
    db = firestore.client()
    license_number = payload.get("license_number")
    password = payload.get("password")
    if not (license_number and password):
        return None

    doc_ref = db.collection("doctors").document(license_number)
    snapshot = doc_ref.get()
    if snapshot.exists:
        data = snapshot.to_dict()
        if data.get("password") == password:
            data["documentId"] = snapshot.id
            return data

    return None