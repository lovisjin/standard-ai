from datetime import datetime
from pydantic import BaseModel, Field, UUID4
from typing import List, Optional
from enum import Enum
import random

class EmotionEnum(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

class SkillEnum(str, Enum):
    SUMMARIZE = "summarize"
    PPT = "ppt"
    VOICE = "voice"
    CHECKLIST = "checklist"
    FIELD = "field"

class FeedbackBase(BaseModel):
    """피드백 기본 모델"""
    user_id: UUID4 = Field(..., description="사용자 ID")
    content: str = Field(..., min_length=1, max_length=1000, description="피드백 내용")
    skill: Optional[str] = Field(None, description="기술 태그")
    emotion: Optional[str] = Field(None, description="감정 태그")
    keywords: Optional[List[str]] = Field(None, description="키워드 목록")

class FeedbackCreate(FeedbackBase):
    """피드백 생성 요청 모델"""
    user_id: UUID4
    content: str = Field(..., min_length=1)
    skill: Optional[SkillEnum] = None
    emotion: Optional[EmotionEnum] = None
    keywords: Optional[List[str]] = Field(default_factory=list)

class FeedbackResponse(FeedbackBase):
    """피드백 응답 모델"""
    id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True

class FeedbackInDB(FeedbackBase):
    """DB에 저장되는 피드백 모델"""
    id: UUID4
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    """사용자 생성을 위한 모델"""
    name: str

class UserInDB(BaseModel):
    """데이터베이스의 사용자 모델"""
    id: UUID4
    name: str

def generate_sample_feedback(user_id: UUID4) -> FeedbackCreate:
    """샘플 피드백 데이터를 생성합니다."""
    sample_contents = [
        "문서 요약이 정확하고 핵심을 잘 캡처했어요!",
        "PPT 자동 생성 기능이 업무 효율을 크게 높여줬습니다.",
        "음성 메모 변환이 회의록 작성에 큰 도움이 됩니다.",
        "체크리스트 추출 기능이 정확도가 조금 아쉽네요.",
        "현장 보고서 요약이 실제 상황을 잘 반영하고 있어요."
    ]

    sample_keywords = [
        ["정확성", "요약", "핵심"],
        ["자동화", "효율", "PPT"],
        ["음성인식", "회의록", "편리성"],
        ["체크리스트", "정확도", "개선필요"],
        ["현장", "보고서", "실용성"]
    ]

    content_idx = random.randint(0, len(sample_contents) - 1)
    
    return FeedbackCreate(
        user_id=user_id,
        content=sample_contents[content_idx],
        skill=list(SkillEnum)[content_idx],
        emotion=EmotionEnum.POSITIVE if random.random() > 0.3 else EmotionEnum.NEGATIVE,
        keywords=sample_keywords[content_idx]
    )

def generate_sample_feedbacks(user_id: UUID4, count: int = 5) -> List[FeedbackCreate]:
    """여러 개의 샘플 피드백을 생성합니다."""
    return [generate_sample_feedback(user_id) for _ in range(count)]
