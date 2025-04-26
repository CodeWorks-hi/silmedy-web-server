from app.core.config import init_dynamodb
from boto3.dynamodb.conditions import Attr

dynamodb = init_dynamodb()
table_admins = dynamodb.Table("admins")

def get_all_admins():
    response = table_admins.scan()
    return response.get("Items", [])

def delete_admin_by_id(admin_id):
    table_admins.delete_item(
        Key={'admin_id': admin_id}
    )

def update_admin_by_id(admin_id, payload):
    update_expression = "SET " + ", ".join(f"{k}=:{k}" for k in payload)
    expression_attribute_values = {f":{k}": v for k, v in payload.items()}
    table_admins.update_item(
        Key={'admin_id': admin_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values
    )

def register_admin(payload):
    table_admins.put_item(Item=payload)

def find_admin_by_credentials(payload):
    admin_id = payload.get("admin_id")
    password = payload.get("password")
    if not (admin_id and password):
        return None
    response = table_admins.scan(
        FilterExpression=Attr("admin_id").eq(admin_id) & Attr("password").eq(password)
    )
    items = response.get("Items", [])
    return items[0] if items else None