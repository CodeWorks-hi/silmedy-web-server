import os
import json
import boto3
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# ✅ 환경변수 로드
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# ✅ AWS 세션
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION", "ap-northeast-2")

session = boto3.session.Session()

# ✅ DynamoDB 리소스
dynamodb = session.resource(
    "dynamodb",
    region_name=aws_region,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

# ✅ 테이블
table_hospitals = dynamodb.Table("hospitals")
table_diseases = dynamodb.Table("diseases")
table_drugs = dynamodb.Table("drugs")
table_counters = dynamodb.Table("counters")
table_care_requests = dynamodb.Table("care_requests")
table_diagnosis_records = dynamodb.Table("diagnosis_records")
table_prescription_records = dynamodb.Table("prescription_records")

# ✅ Firebase 초기화
def init_firebase():
    if not firebase_admin._apps:
        environment = os.getenv("ENVIRONMENT", "local")
        if environment == "local":
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            secrets_path = os.path.join(project_root, "secrets", "firebase-service-account.json")
            cred = credentials.Certificate(secrets_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': os.getenv("FIREBASE_DB_URL")
            })
        else:
            firebase_credential_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
            if not firebase_credential_json:
                raise ValueError("FIREBASE_CREDENTIALS_JSON이 설정되지 않았습니다.")

            # 🔥 필수: \n 이스케이프 복원
            firebase_credential_json = firebase_credential_json.replace("\\n", "\n")
            cred_info = json.loads(firebase_credential_json)
            cred = credentials.Certificate(cred_info)
            firebase_admin.initialize_app(cred, {
                'databaseURL': os.getenv("FIREBASE_DB_URL")
            })

# ✅ Firestore 클라이언트 반환
def get_firestore_client():
    return firestore.client()