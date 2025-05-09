# app/core/config.py

import os
import json
import boto3
import firebase_admin
from firebase_admin import credentials, firestore, db, messaging
from dotenv import load_dotenv
from functools import lru_cache

# ────────────────────────────────────────────────────────
# 1. 환경변수 로드 (.env)
# ────────────────────────────────────────────────────────
# 프로젝트 루트의 .env 파일에서 AWS 키, Firebase 설정 등을 읽어옵니다.
load_dotenv(dotenv_path=os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    ".env"
))

# ────────────────────────────────────────────────────────
# 2. AWS (DynamoDB) 클라이언트 초기화
# ────────────────────────────────────────────────────────
aws_access_key_id     = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region            = os.getenv("AWS_REGION", "ap-northeast-2")  # 기본값: 서울 리전

# boto3 세션 생성
session = boto3.session.Session()

# DynamoDB 리소스 생성
dynamodb = session.resource(
    "dynamodb",
    region_name=aws_region,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

# DynamoDB 테이블 객체들
table_hospitals          = dynamodb.Table("hospitals")
table_diseases           = dynamodb.Table("diseases")
table_drugs              = dynamodb.Table("drugs")
table_counters           = dynamodb.Table("counters")
table_care_requests      = dynamodb.Table("care_requests")
table_diagnosis_records  = dynamodb.Table("diagnosis_records")
table_prescription_records = dynamodb.Table("prescription_records")

# ────────────────────────────────────────────────────────
# 3. Firebase 초기화 함수
# ────────────────────────────────────────────────────────
def init_firebase():
    """
    firebase_admin 앱이 아직 초기화되지 않았다면,
    로컬(.json 파일) 또는 환경변수(JSON 문자열)에서
    서비스 계정 자격증명을 읽어와 초기화합니다.
    """
    if not firebase_admin._apps:
        # ENVIRONMENT 변수로 로컬/배포 구분
        environment = os.getenv("ENVIRONMENT", "local")

        if environment == "local":
            # 로컬 개발: secrets/firebase-service-account.json 사용
            project_root      = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            credentials_path  = os.path.join(project_root, "secrets", "firebase-service-account.json")
            cred = credentials.Certificate(credentials_path)
        else:
            # 배포 환경: FIREBASE_CREDENTIALS_JSON 환경변수 사용
            firebase_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
            if not firebase_json:
                raise ValueError("FIREBASE_CREDENTIALS_JSON 환경변수가 비어 있습니다.")
            # 줄바꿈 이스케이프 처리 복원
            firebase_json = firebase_json.replace("\\n", "\n")
            cred_info     = json.loads(firebase_json)
            cred          = credentials.Certificate(cred_info)

        # 실제 초기화 호출: Firestore, RealtimeDB, Messaging 등 모두 활성화
        firebase_admin.initialize_app(cred, {
            "databaseURL": os.getenv("FIREBASE_DB_URL")
        })

# ────────────────────────────────────────────────────────
# 4. Firebase 클라이언트 반환 헬퍼
# ────────────────────────────────────────────────────────
@lru_cache()
def get_firestore_client():
    """
    Firestore 문서 CRUD용 클라이언트 반환.
    """
    init_firebase()
    return firestore.client()

def get_realtime_db():
    """
    Realtime Database용 레퍼런스 반환.
    """
    init_firebase()
    return db

def get_fcm_client():
    """
    Firebase Admin SDK의 Messaging 모듈 반환.
    푸시 메시지 전송 등을 위해 사용합니다.
    """
    init_firebase()
    return messaging