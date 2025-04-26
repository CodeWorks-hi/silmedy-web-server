from app.core.config import init_dynamodb

dynamodb = init_dynamodb()
table_hospitals = dynamodb.Table("hospitals")

def get_all_hospitals():
    response = table_hospitals.scan()
    return response.get("Items", [])