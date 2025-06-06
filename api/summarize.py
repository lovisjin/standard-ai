from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime
from core.prompt_engine import run_gpt_summary
from db.supabase import supabase

router = APIRouter()

class SummarizeRequest(BaseModel):
    user_id: str | None = None  # 비회원이면 None
    text: str

class SummarizeResponse(BaseModel):
    summary: str
    saved: bool
    summary_id: str | None = None

@router.post("/summarize", response_model=SummarizeResponse)
async def summarize(req: SummarizeRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="요약할 텍스트가 필요합니다.")

    try:
        summary = await run_gpt_summary(req.text)

        # DB 저장
        result = supabase.table("summaries").insert({
            "user_id": req.user_id,
            "input_text": req.text,
            "summary": summary,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        return SummarizeResponse(
            summary=summary,
            saved=True,
            summary_id=result.data[0]["id"] if result.data else None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
