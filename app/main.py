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
from app.api.v1.patients import router as patients_router

# ✅ 2. Firebase 초기화
init_firebase()

# ✅ 3. FastAPI 인스턴스 생성
app = FastAPI()

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
app.include_router(patients_router, prefix="/api/v1")

