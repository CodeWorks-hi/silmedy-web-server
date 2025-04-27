from firebase_admin import firestore



def get_all_patients():
    db = firestore.client()
    collection_patients = db.collection("patients")
    docs = collection_patients.stream()
    return [doc.to_dict() for doc in docs]