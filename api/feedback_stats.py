from fastapi import APIRouter, Query, HTTPException
from datetime import datetime
from typing import Optional
from db.supabase import supabase
from pydantic import BaseModel

router = APIRouter()

class FeedbackStatsResponse(BaseModel):
    total_feedbacks: int
    positive_rate: float
    negative_rate: float
    recent_comments: list[dict]
    start_date: str
    end_date: str

@router.get("/stats", response_model=FeedbackStatsResponse)
async def get_feedback_stats(
    start_date: str = Query(..., description="시작일 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="종료일 (YYYY-MM-DD)"),
    user_id: Optional[str] = Query(None, description="사용자 ID (선택)")
) -> FeedbackStatsResponse:
    """
    피드백 통계를 조회합니다.
    """
    try:
        # 날짜 형식 검증 및 변환
        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="잘못된 날짜 형식")

        # 통계 조회
        stats = await supabase.get_feedback_stats(
            start_date=start,
            end_date=end,
            user_id=user_id
        )

        # 프론트엔드 형식에 맞게 데이터 변환
        recent_comments = [
            {
                "text": feedback["feedback_text"],
                "is_positive": feedback["is_positive"],
                "created_at": feedback["created_at"]
            }
            for feedback in stats["recent_feedbacks"]
        ]

        return FeedbackStatsResponse(
            total_feedbacks=stats["total_count"],
            positive_rate=stats["positive_rate"],
            negative_rate=stats["negative_rate"],
            recent_comments=recent_comments,
            start_date=start_date,
            end_date=end_date
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
