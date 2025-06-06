FROM python:3.11-slim

# 라이브러리 설치
RUN pip install --no-cache-dir uvicorn[standard] fastapi python-multipart \
    supabase python-dotenv

WORKDIR /app

# 프로젝트 전체 구조를 복사
COPY api/ /app/api/
COPY config/ /app/config/
COPY core/ /app/core/
COPY models/ /app/models/
COPY skills/ /app/skills/
COPY db/ /app/db/
COPY utils/ /app/utils/

# PYTHONPATH 설정
ENV PYTHONPATH=/app

# FastAPI 앱 실행
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
