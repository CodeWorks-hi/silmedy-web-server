from app.core.config import table_hospitals

def get_all_hospitals():
    response = table_hospitals.scan()
    return response.get("Items", [])