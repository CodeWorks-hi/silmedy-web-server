# 🩺 Silmedy Web Server (의사/관리자용 통합 웹 백엔드)

### 환자 비대면 진료를 위한 영상 통화, 진단, 처방 기능을 제공하는 FastAPI 기반의 백엔드 시스템

---

## 📌 프로젝트 개요

본 프로젝트는 Silmedy 의사/관리자용 웹 프론트엔드의 백엔드 서버입니다. 병원 관리자 및 의료진이 웹 기반으로 환자 진료 요청을 수신하고, WebRTC 영상 통화, 진단 입력, 처방전 생성 및 Firebase 연동 등을 수행할 수 있도록 설계되어 있습니다.

---

## 🛠️ 기술 스택

| 분야             | 사용 기술 |
|------------------|-----------|
| 웹 프레임워크     | FastAPI   |
| 실시간 영상 시그널링 | Firebase RTDB |
| 사용자 인증       | JWT 토큰  |
| DB 및 파일 저장   | AWS DynamoDB, Firebase Firestore, S3 |
| 메신저/알림       | Firebase Cloud Messaging |
| 환경 변수 관리     | python-dotenv |

---

## 🔑 주요 기능

### 👨‍⚕️ 의사 기능
- 진료 요청 수신 및 환자 정보 확인
- WebRTC 영상 진료 및 음성 자막 실시간 송출
- 진단서 입력 및 질병 코드 선택
- 처방전 생성 및 약품 목록 입력

### 🧑‍💼 관리자 기능
- 병원 소속 의사 목록 조회
- 의사 계정 생성, 수정, 삭제
- 의사 프로필 이미지 등록 및 갱신

### 🔐 인증 및 보안
- 로그인 시 JWT 액세스 토큰 + Firebase 커스텀 토큰 발급
- API 별 권한 분리 (의사, 관리자)

---

## 📂 프로젝트 구조

```
📁 silmedy-web-server/
├── app/
│   ├── api/v1/             # API 엔드포인트
│   ├── core/               # 설정, Firebase 초기화, 보안 로직
│   ├── models/             # Pydantic 모델
│   ├── schemas/            # 요청/응답 스키마
│   ├── services/           # 비즈니스 로직
│   └── main.py             # FastAPI 앱 진입점
├── .env                    # 환경변수 파일
├── requirements.txt        # 패키지 종속성
└── README.md               # 프로젝트 설명
```

---

## 🚀 실행 방법

1. `.env` 파일 설정 (예시는 아래 참조)
2. 종속 라이브러리 설치

```bash
pip install -r requirements.txt
```

3. 서버 실행

```bash
uvicorn app.main:app --reload
```

4. Swagger 문서 확인:  
   http://3.34.104.170/docs

---

## 🔐 환경변수 예시 (.env)

```
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_SECONDS=3600
REFRESH_TOKEN_EXPIRE_SECONDS=604800

AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=ap-northeast-2
AWS_S3_BUCKET=your_bucket_name

FIREBASE_DB_URL=https://your-app.firebaseio.com
ENVIRONMENT=local
```