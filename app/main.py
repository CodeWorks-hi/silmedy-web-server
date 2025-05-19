# app/main.py

import os
from dotenv import load_dotenv

# ✅ 1. 환경변수 로드 (.env)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import init_firebase
from app.api.v1.auth import router as auth_router
from app.api.v1.hospitals import router as hospitals_router
from app.api.v1.doctors import router as doctors_router
from app.api.v1.diseases import router as diseases_router
from app.api.v1.video_calls import router as video_calls_router
from app.api.v1.care_requests import router as care_requests_router
from app.api.v1.drugs import router as drugs_router
from app.api.v1.prescriptions import router as prescriptions_router
from app.api.v1.diagnosis import router as diagnosis_router

# ✅ 2. Firebase 초기화
init_firebase()

# ✅ 3. FastAPI 인스턴스 생성
app = FastAPI(
    title="Silmedy-관리자/의료진 통합 웹",
    description="Silmedy 관리자/의사용 통합 웹의 백엔드 REST API 명세서입니다.\n\n의사 관리, 진단, 처방, 진료 요청 등 병원 기능을 포함합니다.\n\n🔐 인증이 필요한 API는 상단의 **Authorize** 버튼을 눌러 JWT 토큰을 입력한 후 사용하세요.\n- 예시: `eyJhbGciOi...`",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "공통 - 로그인",
            "description": "관리자 또는 의사가 로그인하여 JWT 토큰을 발급받는 기능입니다."
        },
        {
            "name": "관리자 - 직원 관리",
            "description": "직원 계정 생성, 수정, 삭제 등 관리자가 사용하는 직원 관리 기능입니다."
        },
        {
            "name": "의사 - 진료 관리",
            "description": "의사가 환자에 대해 진료를 수행하고 진료 내용을 조회/관리하는 기능입니다."
        },
        {
            "name": "의사 - 처방 관리",
            "description": "진료 후 약품 검색 및 처방전 등록 기능입니다."
        },
        {
            "name": "의사 - 영상통화 진행",
            "description": "WebRTC 기반 영상 통화 시작, 수락/거절, 종료 및 메시지 송수신 등 통화 전반을 관리하는 기능입니다."
        }
    ]
)

# ✅ 4. CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://3.36.62.211",
        "https://boohoday.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ✅ 5. 라우터 등록
app.include_router(auth_router, prefix="/api/v1")
app.include_router(hospitals_router, prefix="/api/v1")
app.include_router(doctors_router, prefix="/api/v1")
app.include_router(diseases_router, prefix="/api/v1")
app.include_router(video_calls_router, prefix="/api/v1")
app.include_router(care_requests_router, prefix="/api/v1")
app.include_router(drugs_router, prefix="/api/v1")
app.include_router(prescriptions_router, prefix="/api/v1")
app.include_router(diagnosis_router, prefix="/api/v1")
