# 베이스 이미지: Python 3.9 슬림 버전
FROM python:3.9-slim

# Python 출력 버퍼링 비활성화 (로그 즉시 출력용)
ENV PYTHONUNBUFFERED=1

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 빌드 툴 설치 (gspread, google-auth 등 빌드 시 필요할 수 있음)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# 의존성 설치를 위해 먼저 requirements.txt만 복사
COPY requirements.txt .

# 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 앱 소스코드 전체 복사
COPY . .

# 기본 ENV 설정 (운영 시에는 LOG_LEVEL=INFO 등으로 오버라이드)
ENV LOG_LEVEL=INFO
ENV DEBUG=false

# FastAPI 앱을 uvicorn으로 실행 (포트 8000)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
