# app/core/config.py

import os
import boto3
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv

# ✅ 1. 서버가 시작될 때 무조건 환경변수 먼저 로드
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# ✅ 2. DynamoDB 설정 (환경변수 읽은 후)
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION", "ap-northeast-2")

dynamodb = boto3.resource(
    "dynamodb",
    region_name=aws_region,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

# ✅ 3. DynamoDB 테이블 객체
table_hospitals = dynamodb.Table("hospitals")
table_diseases = dynamodb.Table("diseases")
table_drugs = dynamodb.Table("drugs")

# ✅ 4. Firebase 초기화 함수 (부팅할 때 호출)
def init_firebase():
    firebase_credential_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
    firebase_db_url = os.getenv("FIREBASE_DB_URL")
    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_credential_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': firebase_db_url
        })