from app.core.config import table_diseases

def get_all_diseases():
    response = table_diseases.scan()
    return response.get("Items", [])