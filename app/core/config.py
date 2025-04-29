import os
import json
import boto3
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# ✅ 1. 환경변수 로드
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# ✅ 2. AWS 세션 설정
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region = os.getenv("AWS_REGION", "ap-northeast-2")

session = boto3.session.Session()

# ✅ 3. DynamoDB 리소스
dynamodb = session.resource(
    "dynamodb",
    region_name=aws_region,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

# ✅ 4. DynamoDB 테이블 객체들
table_hospitals = dynamodb.Table("hospitals")
table_diseases = dynamodb.Table("diseases")
table_drugs = dynamodb.Table("drugs")
table_counters = dynamodb.Table("counters")
table_care_requests = dynamodb.Table("care_requests")
table_diagnosis_records = dynamodb.Table("diagnosis_records")
table_prescription_records = dynamodb.Table("prescription_records")

# ✅ 5. Firebase 초기화 함수
def init_firebase():
    if not firebase_admin._apps:
        environment = os.getenv("ENVIRONMENT", "local")  # 기본은 local
        if environment == "local":
            # 🔵 로컬 개발환경 - 'silmedy-web-server/secrets/firebase_service_account.json' 직접 읽기
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            secrets_path = os.path.join(project_root, "secrets", "firebase-service-account.json")
            cred = credentials.Certificate(secrets_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': os.getenv("FIREBASE_DB_URL")
            })
        else:
            # 🔵 배포 환경 (렌더 등) - .env의 JSON 문자열 읽기
            firebase_credential_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
            if not firebase_credential_json:
                raise ValueError("FIREBASE_CREDENTIALS_JSON이 설정되지 않았습니다.")
            
            firebase_credential_json = firebase_credential_json.replace("\\n", "\n")
            cred_info = json.loads(firebase_credential_json)
            cred = credentials.Certificate(cred_info)
            firebase_admin.initialize_app(cred, {
                'databaseURL': os.getenv("FIREBASE_DB_URL")
            })

# ✅ 6. Firestore 클라이언트 반환 함수
def get_firestore_client():
    return firestore.client()