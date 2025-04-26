from app.core.config import init_dynamodb

dynamodb = init_dynamodb()
table_diseases = dynamodb.Table("diseases")

def get_all_diseases():
    response = table_diseases.scan()
    return response.get("Items", [])