from firebase_admin import firestore

def get_all_doctors():
    db = firestore.client()
    collection_doctors = db.collection("doctors")
    docs = collection_doctors.stream()
    return [doc.to_dict() for doc in docs]

def delete_doctor_by_license(license_number):
    db = firestore.client()
    collection_doctors = db.collection("doctors")
    docs = collection_doctors.where("license_number", "==", license_number).stream()
    for doc in docs:
        doc.reference.delete()

def update_doctor_by_license(license_number, payload):
    db = firestore.client()
    collection_doctors = db.collection("doctors")
    docs = collection_doctors.where("license_number", "==", license_number).stream()
    for doc in docs:
        doc.reference.update(payload)

def register_doctor(payload):
    db = firestore.client()
    collection_doctors = db.collection("doctors")
    collection_doctors.add(payload)

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

