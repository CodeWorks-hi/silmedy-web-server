from firebase_admin import firestore

db = firestore.client()
collection_diagnosis = db.collection("diagnosis")

def get_all_diagnosis_records():
    docs = collection_diagnosis.stream()
    return [doc.to_dict() for doc in docs]

def create_diagnosis(payload: dict):
    doc_ref = collection_diagnosis.document()
    doc_ref.set(payload)
    return {"id": doc_ref.id}

def get_diagnosis_by_patient_id(patient_id):
    docs = collection_diagnosis.where("patient_id", "==", patient_id).stream()
    return [doc.to_dict() for doc in docs]