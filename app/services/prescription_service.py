from firebase_admin import firestore

db = firestore.client()
collection_prescriptions = db.collection("prescriptions")

def get_all_prescription_records():
    docs = collection_prescriptions.stream()
    return [doc.to_dict() for doc in docs]

def create_prescription(payload: dict):
    doc_ref = collection_prescriptions.document()
    doc_ref.set(payload)
    return {"id": doc_ref.id}