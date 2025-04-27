from firebase_admin import firestore

def get_all_prescription_records():
    db = firestore.client()
    collection = db.collection("prescription_records")
    docs = collection.stream()
    return [doc.to_dict() for doc in docs]

def create_prescription_record(payload: dict):
    db = firestore.client()
    collection = db.collection("prescription_records")
    doc_ref = collection.document()
    doc_ref.set(payload)
    return {"id": doc_ref.id}

def update_prescription_record(prescription_id: str, payload: dict):
    db = firestore.client()
    collection = db.collection("prescription_records")
    collection.document(prescription_id).update(payload)
    return {"message": "처방전 수정 완료"}

def delete_prescription_record(prescription_id: str):
    db = firestore.client()
    collection = db.collection("prescription_records")
    collection.document(prescription_id).delete()
    return {"message": "처방전 삭제 완료"}