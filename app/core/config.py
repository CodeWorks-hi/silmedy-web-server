# app/core/config.py

import os
import json
import boto3
import firebase_admin
from firebase_admin import credentials, firestore, db, messaging
from dotenv import load_dotenv
from functools import lru_cache
import uuid

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

# ────────────────────────────────────────────────────────
# 5. S3 클라이언트 & 업로드 헬퍼
# ────────────────────────────────────────────────────────
# boto3 세션을 기반으로 S3 클라이언트 생성
# IAM Role을 사용해 권한을 부여받는 환경에서는 aws_access_key_id, aws_secret_access_key 생략 가능
s3_client = session.client(
    "s3",
    region_name=aws_region,
)

def upload_profile_image(file_bytes: bytes, content_type: str) -> str:
    """
    바이너리 형태의 프로필 이미지를 S3에 업로드하고,
    업로드된 객체의 퍼블릭 URL을 반환합니다.

    Args:
      file_bytes   (bytes): 업로드할 이미지의 raw 바이트 데이터
      content_type (str):   이미지의 MIME 타입 (예: "image/jpeg", "image/png")

    Returns:
      str: S3에 저장된 이미지의 퍼블릭 URL

    Raises:
      botocore.exceptions.ClientError: 업로드 실패 시 예외 발생
    """

    # --- 1) 대상 버킷 이름 가져오기 ---
    bucket = os.getenv("AWS_S3_BUCKET")
    # 환경변수에 설정된 S3 버킷 이름 (예: "silmedy-doctor")

    # --- 2) S3 객체 키(key) 생성 ---
    # "profiles/" 디렉토리 아래에 UUID 기반의 고유 파일명 사용
    unique_filename = uuid.uuid4().hex
    key = f"profiles/{unique_filename}"

    # --- 3) S3에 객체 업로드 ---
    # put_object 파라미터:
    #   Bucket      : 업로드 대상 버킷 이름
    #   Key         : 버킷 내 객체 경로 (profiles/xxxx...)
    #   Body        : 실제 파일 바이트
    #   ContentType : 파일 MIME 타입
    #   ACL         : "public-read"로 설정하여 퍼블릭 접근 허용
    s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=file_bytes,
        ContentType=content_type,
        ACL="public-read"
    )

    # --- 4) 업로드된 객체의 퍼블릭 URL 구성 ---
    # S3 퍼블릭 URL 형식: 
    #   https://{버킷}.s3.{리전}.amazonaws.com/{키}
    region = aws_region
    url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"

    # 최종 URL 반환
    return url