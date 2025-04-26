from app.core.config import init_dynamodb

dynamodb = init_dynamodb()
table_drugs = dynamodb.Table("drugs")

def get_all_drugs():
    response = table_drugs.scan()
    return response.get("Items", [])