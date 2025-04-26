from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import load_env, init_firebase
from app.api.v1.common import router as common_router
from app.api.v1.auth import router as auth_router
from app.api.v1.hospitals import router as hospitals_router
from app.api.v1.doctors import router as doctors_router
from app.api.v1.admins import router as admins_router
from app.api.v1.diseases import router as diseases_router
from app.api.v1.video_calls import router as video_calls_router
from app.api.v1.patients import router as patients_router
from app.api.v1.care_requests import router as care_requests_router
from app.api.v1.drugs import router as drugs_router
from app.api.v1.prescriptions import router as prescriptions_router
from app.api.v1.diagnosis import router as diagnosis_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

load_env()
init_firebase()

app.include_router(common_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(hospitals_router, prefix="/api/v1")
app.include_router(doctors_router, prefix="/api/v1")
app.include_router(admins_router, prefix="/api/v1")
app.include_router(diseases_router, prefix="/api/v1")
app.include_router(video_calls_router, prefix="/api/v1")
app.include_router(patients_router, prefix="/api/v1")
app.include_router(care_requests_router, prefix="/api/v1")
app.include_router(drugs_router, prefix="/api/v1")
app.include_router(prescriptions_router, prefix="/api/v1")
app.include_router(diagnosis_router, prefix="/api/v1")