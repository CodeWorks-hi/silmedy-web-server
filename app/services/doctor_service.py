from app.core.config import init_dynamodb
from boto3.dynamodb.conditions import Attr

dynamodb = init_dynamodb()
table_doctors = dynamodb.Table("doctors")

def get_all_doctors():
    response = table_doctors.scan()
    return response.get("Items", [])

def delete_doctor_by_license(license_number):
    table_doctors.delete_item(
        Key={'license_number': license_number}
    )

def update_doctor_by_license(license_number, payload):
    update_expression = "SET " + ", ".join(f"{k}=:{k}" for k in payload)
    expression_attribute_values = {f":{k}": v for k, v in payload.items()}
    table_doctors.update_item(
        Key={'license_number': license_number},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values
    )

def register_doctor(payload):
    table_doctors.put_item(Item=payload)

def find_doctor_by_credentials(payload):
    license_number = payload.get("license_number")
    password = payload.get("password")
    if not (license_number and password):
        return None
    response = table_doctors.scan(
        FilterExpression=Attr("license_number").eq(license_number) & Attr("password").eq(password)
    )
    items = response.get("Items", [])
    return items[0] if items else None