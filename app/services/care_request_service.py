from firebase_admin import firestore

db = firestore.client()
collection_care_requests = db.collection("care_requests")

def get_all_care_requests():
    docs = collection_care_requests.stream()
    return [doc.to_dict() for doc in docs]

def get_waiting_care_requests():
    docs = collection_care_requests.where("status", "==", "waiting").stream()
    return [doc.to_dict() for doc in docs]