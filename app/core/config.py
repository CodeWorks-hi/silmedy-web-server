# app/core/config.py

import os
import json
import uuid
import boto3
from botocore.exceptions import ClientError
import firebase_admin
from firebase_admin import credentials, firestore, db, messaging
from dotenv import load_dotenv
from functools import lru_cache

# ────────────────────────────────────────────────────────
# 1. 환경변수 로드 (.env)
# ────────────────────────────────────────────────────────
load_dotenv(dotenv_path=os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    ".env"
))

# ────────────────────────────────────────────────────────
# 2. AWS (DynamoDB) 클라이언트 초기화
# ────────────────────────────────────────────────────────
aws_access_key_id     = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region            = os.getenv("AWS_REGION", "ap-northeast-2")

session = boto3.session.Session()
dynamodb = session.resource(
    "dynamodb",
    region_name=aws_region,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

table_hospitals            = dynamodb.Table("hospitals")
table_diseases             = dynamodb.Table("diseases")
table_drugs                = dynamodb.Table("drugs")
table_counters             = dynamodb.Table("counters")
table_care_requests        = dynamodb.Table("care_requests")
table_diagnosis_records    = dynamodb.Table("diagnosis_records")
table_prescription_records = dynamodb.Table("prescription_records")

# ────────────────────────────────────────────────────────
# 3. Firebase 초기화 함수
# ────────────────────────────────────────────────────────
def init_firebase():
    """
    firebase_admin 앱이 초기화되지 않았다면,
    로컬 JSON 파일 또는 ENV의 JSON 문자열로 인증 설정 후 초기화합니다.
    """
    if not firebase_admin._apps:
        environment = os.getenv("ENVIRONMENT", "local")
        if environment == "local":
            project_root     = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            cred_path        = os.path.join(project_root, "secrets", "firebase-service-account.json")
            cred             = credentials.Certificate(cred_path)
        else:
            firebase_json    = os.getenv("FIREBASE_CREDENTIALS_JSON", "")
            firebase_json    = firebase_json.replace("\\n", "\n")
            cred_info        = json.loads(firebase_json)
            cred             = credentials.Certificate(cred_info)
        firebase_admin.initialize_app(cred, {
            "databaseURL": os.getenv("FIREBASE_DB_URL")
        })

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
    """
    init_firebase()
    return messaging

# ────────────────────────────────────────────────────────
# 4. S3 클라이언트 & 업로드 헬퍼
# ────────────────────────────────────────────────────────
s3_client = session.client("s3", region_name=aws_region)

def upload_profile_image(file_bytes: bytes, content_type: str) -> str:
    """
    바이너리 형태의 프로필 이미지를 S3에 업로드하고,
    업로드된 객체의 퍼블릭 URL을 반환합니다.
    """
    bucket = os.getenv("AWS_S3_BUCKET")
    unique_filename = uuid.uuid4().hex
    key = f"profiles/{unique_filename}"

    try:
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=file_bytes,
            ContentType=content_type,
            ACL="public-read"
        )
    except ClientError as e:
        print(f"🚨 S3 업로드 실패: {e}")
        raise

    return f"https://{bucket}.s3.{aws_region}.amazonaws.com/{key}"

def set_profile_url(license_number: str, file_bytes: bytes, content_type: str) -> str:
    """
    1) 기존 프로필 이미지를 S3에서 삭제 (있다면)
    2) 새 이미지를 S3에 업로드
    3) Firestore 문서(profile_url 필드) 업데이트
    4) 업로드된 URL 반환
    """
    db_client = get_firestore_client()
    doc_ref = db_client.collection("doctors").document(license_number)

    if not doc_ref.get().exists:
        raise Exception("해당 license_number 의사를 찾을 수 없습니다.")

    existing = doc_ref.get().to_dict().get("profile_url")
    if existing:
        try:
            prefix = f"https://{os.getenv('AWS_S3_BUCKET')}.s3.{aws_region}.amazonaws.com/"
            old_key = existing.split(prefix, 1)[-1]
            s3_client.delete_object(Bucket=os.getenv("AWS_S3_BUCKET"), Key=old_key)
        except ClientError as e:
            print(f"⚠️ 기존 프로필 이미지 삭제 실패: {e}")

    new_url = upload_profile_image(file_bytes, content_type)
    doc_ref.update({"profile_url": new_url})
    return new_url