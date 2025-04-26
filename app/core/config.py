import os
from dotenv import load_dotenv
import boto3
import firebase_admin
from firebase_admin import credentials

def load_env():
    load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))

def init_firebase():
    firebase_credential_path = os.getenv("FIREBASE_CREDENTIAL_PATH")
    firebase_db_url = os.getenv("FIREBASE_DB_URL")
    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_credential_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': firebase_db_url
        })

def init_dynamodb():
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_REGION", "ap-northeast-2")
    dynamodb = boto3.resource(
        "dynamodb",
        region_name=aws_region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    return dynamodb