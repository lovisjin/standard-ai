from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from config.logger import logger
from api.feedback import router as feedback_router
from api.feedback_stats import router as feedback_stats_router
from api.summarize import router as summarize_router
from core.prompt_engine import PromptEngine
from skills.summarizer import Summarizer
from skills.ppt_writer import PPTWriter
from skills.field_reporter import FieldReporter
from skills.checklist_extractor import ChecklistExtractor
from skills.voice_memo_summarizer import VoiceMemoSummarizer
from skills.logis_summarizer import execute as logis_execute

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 실제 프론트엔드 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 추가
app.include_router(feedback_router, prefix="/feedback", tags=["feedback"])
app.include_router(feedback_stats_router, prefix="/feedback", tags=["feedback"])
app.include_router(summarize_router, tags=["summarize"])

# PromptEngine 및 스킬 초기화
prompt_engine = PromptEngine()
skills = {
    "summarizer": Summarizer(prompt_engine),
    "ppt_writer": PPTWriter(prompt_engine),
    "field_reporter": FieldReporter(prompt_engine),
    "checklist_extractor": ChecklistExtractor(prompt_engine),
    "voice_memo_summarizer": VoiceMemoSummarizer(prompt_engine),
    "logis_summarizer": None  # 기존 스킬은 별도로 처리
}

class ExecuteRequest(BaseModel):
    skill: str
    user_id: str
    text: Optional[str] = None
    additional_params: Optional[Dict[str, Any]] = None

class ExecuteResponse(BaseModel):
    result: Dict[str, Any]
    status: str = "success"

@app.post("/execute", response_model=ExecuteResponse)
async def execute_skill(req: ExecuteRequest):
    """
    스킬 실행 엔드포인트

    지원하는 스킬:
    - summarizer: 텍스트 요약
    - ppt_writer: PPT 생성
    - field_reporter: 현장 보고서 작성
    - checklist_extractor: 체크리스트 추출
    - voice_memo_summarizer: 음성 메모 요약
    - logis_summarizer: 물류 요약 (레거시)

    API 문서:
    - Swagger UI: /docs
    - ReDoc: /redoc
    """
    logger.info(f"스킬 실행 요청 - skill: {req.skill}, user_id: {req.user_id}")
    
    try:
        if req.skill == "logis_summarizer":
            # 기존 물류 요약 스킬 처리
            result = logis_execute(req.user_id, req.text)
            return ExecuteResponse(
                result={
                    "summary": result["summary"],
                    "sheet_url": result["sheet_url"]
                }
            )
        
        skill_instance = skills.get(req.skill)
        if not skill_instance:
            logger.warning(f"알 수 없는 스킬: {req.skill}")
            raise HTTPException(
                status_code=400,
                detail=f"Unknown skill: {req.skill}"
            )

        # 스킬별 입력 데이터 준비
        input_data = {"user_id": req.user_id}
        if req.text:
            input_data["text"] = req.text
        if req.additional_params:
            input_data.update(req.additional_params)

        # 스킬 실행
        result = await skill_instance.process(input_data)
        logger.info("스킬 실행 완료")
        return ExecuteResponse(result=result)
            
    except Exception as e:
        logger.error(f"스킬 실행 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error executing skill: {str(e)}"
        )

@app.post("/upload_voice_memo")
async def upload_voice_memo(
    file: UploadFile = File(...),
    user_id: str = None
):
    """음성 메모 파일을 업로드하고 처리하는 엔드포인트"""
    try:
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # 음성 메모 처리
        skill_instance = skills["voice_memo_summarizer"]
        result = await skill_instance.process({
            "audio_path": temp_file_path,
            "user_id": user_id
        })

        # 임시 파일 삭제
        Path(temp_file_path).unlink()

        return ExecuteResponse(result=result)

    except Exception as e:
        logger.error(f"음성 메모 처리 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing voice memo: {str(e)}"
        )
