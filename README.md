# STANDARD-AI

AI 기반 문서 처리 및 피드백 분석 플랫폼

## 🌟 주요 기능

### 📊 피드백 대시보드
- 실시간 피드백 통계 시각화
- 기간별 피드백 분석
- 긍정/부정 비율 도넛 차트
- 최근 피드백 목록 표시

### 🤖 AI 문서 처리
- 문서 자동 요약
- PPT 자동 생성
- 음성 메모 텍스트 변환
- 체크리스트 추출

### 📈 통계 및 분석
- 사용자별 피드백 추적
- 기간별 통계 리포트
- 요약 품질 분석

## ⚡️ 빠른 시작

### 요구사항
- Python 3.9+
- Node.js 18+
- Supabase 계정

### 설치

1. 저장소 클론
```bash
git clone https://github.com/your-org/standard-ai.git
cd standard-ai
```

2. 백엔드 설정
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. 프론트엔드 설정
```bash
cd frontend
npm install
```

4. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 편집하여 필요한 값 설정
```

### 실행

1. 백엔드 서버
```bash
uvicorn api.main:app --reload
```

2. 프론트엔드 개발 서버
```bash
cd frontend
npm run dev
```

## 📚 API 문서

### 피드백 API
- `GET /feedback/stats`: 피드백 통계 조회
  - `start_date`: 시작일 (YYYY-MM-DD)
  - `end_date`: 종료일 (YYYY-MM-DD)
  - `user_id`: 사용자 ID (선택)

- `GET /feedback/sample`: 샘플 데이터 조회
  - 신규 사용자를 위한 데모 데이터 제공

- `POST /feedback/submit`: 새 피드백 제출
  - `feedback_text`: 피드백 내용
  - `is_positive`: 긍정/부정 여부
  - `summary_id`: 요약 ID

자세한 API 문서는 서버 실행 후 `/docs` 에서 확인할 수 있습니다.

## 🔧 기술 스택

### 백엔드
- FastAPI
- Supabase
- OpenAI GPT-4
- Whisper

### 프론트엔드
- React + Vite
- TypeScript
- TailwindCSS
- Recharts

## 💡 기능 하이라이트

### 초기 사용자 온보딩
- 샘플 데이터 기반 빠른 체험
- 직관적인 UI/UX
- 실시간 피드백 수집

### 데이터 시각화
- 도넛 차트 통계
- 반응형 레이아웃
- 실시간 업데이트

### 통합 기능
- Slack 알림
- Google Sheets 연동
- 이메일 리포트

## 🤝 기여하기

1. 이슈 생성 또는 확인
2. 브랜치 생성 (`feature/issue-description`)
3. 변경사항 커밋
4. PR 생성

## 📄 라이선스

MIT License
