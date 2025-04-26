from firebase_admin import firestore

db = firestore.client()
collection_patients = db.collection("patients")

def get_all_patients():
    docs = collection_patients.stream()
    return [doc.to_dict() for doc in docs]