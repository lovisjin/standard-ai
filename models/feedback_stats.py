from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator

class RecentFeedback(BaseModel):
    """최근 피드백 항목 모델"""
    feedback_text: str = Field(..., description="피드백 내용")
    is_positive: bool = Field(..., description="긍정/부정 여부")
    created_at: datetime = Field(..., description="생성 시간")
    user_id: str = Field(..., description="사용자 ID")
    summary_id: Optional[str] = Field(None, description="요약 ID")

class FeedbackStatsResponse(BaseModel):
    """피드백 통계 응답 모델"""
    total_feedbacks: int = Field(..., description="총 피드백 수")
    positive_rate: float = Field(..., ge=0, le=1, description="긍정 비율")
    negative_rate: float = Field(..., ge=0, le=1, description="부정 비율")
    recent_comments: List[RecentFeedback] = Field(..., description="최근 피드백 목록")
    start_date: str = Field(..., description="조회 시작일")
    end_date: str = Field(..., description="조회 종료일")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_feedbacks": 150,
                "positive_rate": 0.75,
                "negative_rate": 0.25,
                "recent_comments": [
                    {
                        "feedback_text": "요약이 정확하고 명확해요",
                        "is_positive": True,
                        "created_at": "2025-06-02T10:00:00Z",
                        "user_id": "user123",
                        "summary_id": "sum_123"
                    }
                ],
                "start_date": "2025-05-03",
                "end_date": "2025-06-02"
            }
        }
