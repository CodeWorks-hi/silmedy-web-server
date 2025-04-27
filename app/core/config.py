import os
import json
import boto3
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv

# ✅ 환경변수 로드
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# ✅ AWS 자격증명 명시적 선언
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION", "ap-northeast-2")

session = boto3.session.Session()

dynamodb = session.resource(
    "dynamodb",
    region_name=aws_region,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

# ✅ DynamoDB 테이블 객체
table_hospitals = dynamodb.Table("hospitals")
table_diseases = dynamodb.Table("diseases")
table_drugs = dynamodb.Table("drugs")

# ✅ Firebase 초기화 함수 (🔥 수정한 부분)
def init_firebase():
    firebase_credential_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
    firebase_db_url = os.getenv("FIREBASE_DB_URL")
    if not firebase_admin._apps:
        cred_info = json.loads(firebase_credential_json)
        cred = credentials.Certificate(cred_info)
        firebase_admin.initialize_app(cred, {
            'databaseURL': firebase_db_url
        })