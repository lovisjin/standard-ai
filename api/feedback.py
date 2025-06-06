from fastapi import APIRouter, Query, HTTPException, Body
from datetime import datetime, timedelta
from typing import Optional
from db.supabase import supabase
from models.feedback import FeedbackCreate
from models.feedback_stats import FeedbackStatsResponse
import json

router = APIRouter()

# 피드백 제출 엔드포인트
@router.post("/submit")
async def submit_feedback(
    feedback: FeedbackCreate = Body(..., description="피드백 데이터")
) -> dict:
    """새로운 피드백을 제출합니다."""
    try:
        result = await supabase.create_feedback(feedback)
        return {
            "status": "success", 
            "message": "피드백이 성공적으로 저장되었습니다."
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail="피드백 저장 중 오류가 발생했습니다."
        )

# 피드백 통계 조회 엔드포인트
@router.get("/stats", response_model=FeedbackStatsResponse)
async def get_feedback_stats(
    start_date: str = Query(..., description="시작일 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="종료일 (YYYY-MM-DD)"),
    user_id: Optional[str] = Query(None, description="사용자 ID (선택)")
) -> FeedbackStatsResponse:
    """피드백 통계를 조회합니다."""
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
                "feedback_text": feedback["feedback_text"],
                "is_positive": feedback["is_positive"],
                "created_at": feedback["created_at"],
                "user_id": feedback["user_id"],
                "summary_id": feedback.get("summary_id")
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

# 샘플 데이터 조회 엔드포인트
@router.get("/sample", response_model=FeedbackStatsResponse)
async def get_sample_stats() -> FeedbackStatsResponse:
    """샘플 피드백 통계를 반환합니다."""
    current_date = datetime.now()
    
    return FeedbackStatsResponse(
        total_feedbacks=42,
        positive_rate=0.8,
        negative_rate=0.2,
        recent_comments=[
            {
                "feedback_text": "문서 요약이 매우 정확하고 핵심을 잘 캡처했어요!",
                "is_positive": True,
                "created_at": current_date,
                "user_id": "sample_user_1",
                "summary_id": "sample_1"
            },
            {
                "feedback_text": "PPT 자동 생성 기능이 업무 효율을 크게 높여줬습니다.",
                "is_positive": True,
                "created_at": current_date,
                "user_id": "sample_user_2",
                "summary_id": "sample_2"
            },
            {
                "feedback_text": "음성 메모 요약 기능이 회의록 작성에 큰 도움이 됩니다.",
                "is_positive": True,
                "created_at": current_date,
                "user_id": "sample_user_3",
                "summary_id": "sample_3"
            }
        ],
        start_date=(current_date - timedelta(days=30)).strftime("%Y-%m-%d"),
        end_date=current_date.strftime("%Y-%m-%d")
    )
