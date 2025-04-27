from app.core.config import table_drugs

def get_all_drugs():
    response = table_drugs.scan()
    return response.get("Items", [])