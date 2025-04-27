from firebase_admin import firestore

def get_all_admins():
    db = firestore.client()
    collection_admins = db.collection("admins")
    docs = collection_admins.stream()
    return [doc.to_dict() for doc in docs]

def delete_admin_by_id(admin_id):
    db = firestore.client()
    collection_admins = db.collection("admins")
    docs = collection_admins.where("admin_id", "==", admin_id).stream()
    for doc in docs:
        doc.reference.delete()

def update_admin_by_id(admin_id, payload):
    db = firestore.client()
    collection_admins = db.collection("admins")
    docs = collection_admins.where("admin_id", "==", admin_id).stream()
    for doc in docs:
        doc.reference.update(payload)

def register_admin(payload):
    db = firestore.client()
    collection_admins = db.collection("admins")
    collection_admins.add(payload)

def find_admin_by_credentials(payload):
    db = firestore.client()
    collection_admins = db.collection("admins")

    admin_id = payload.get("admin_id")
    password = payload.get("password")
    if not (admin_id and password):
        return None

    docs = collection_admins.where("admin_id", "==", admin_id).where("password", "==", password).stream()
    items = [doc.to_dict() for doc in docs]
    return items[0] if items else None