import pytest
from fastapi.testclient import TestClient
from api.main import app
from models.feedback import FeedbackCreate

client = TestClient(app)

@pytest.fixture
def sample_feedback():
    return {
        "user_id": "test_user",
        "summary_id": "test_summary",
        "feedback_text": "매우 정확한 요약이었습니다!",
        "is_positive": True
    }

def test_create_feedback_success(sample_feedback):
    """정상적인 피드백 생성 테스트"""
    response = client.post("/feedback", json=sample_feedback)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == sample_feedback["user_id"]
    assert data["feedback_text"] == sample_feedback["feedback_text"]
    assert "id" in data
    assert "created_at" in data

def test_create_feedback_duplicate(sample_feedback):
    """중복 피드백 제출 테스트"""
    # 첫 번째 제출
    response1 = client.post("/feedback", json=sample_feedback)
    assert response1.status_code == 200

    # 두 번째 제출 (중복)
    response2 = client.post("/feedback", json=sample_feedback)
    assert response2.status_code == 400
    assert "이미 제출된 피드백입니다" in response2.json()["detail"]

def test_create_feedback_invalid_input():
    """잘못된 입력값 테스트"""
    invalid_feedback = {
        "user_id": "",  # 빈 문자열
        "summary_id": "test_summary",
        "feedback_text": "",  # 빈 문자열
        "is_positive": True
    }
    response = client.post("/feedback", json=invalid_feedback)
    assert response.status_code == 422  # Validation Error

@pytest.mark.asyncio
async def test_supabase_feedback_operations(sample_feedback):
    """Supabase 연동 테스트"""
    from db.supabase import supabase
    
    # 피드백 생성
    feedback = FeedbackCreate(**sample_feedback)
    result = await supabase.create_feedback(feedback)
    assert result.user_id == sample_feedback["user_id"]
    
    # 피드백 조회
    saved = await supabase.get_feedback_by_summary(
        sample_feedback["user_id"], 
        sample_feedback["summary_id"]
    )
    assert saved is not None
    assert saved.feedback_text == sample_feedback["feedback_text"]
    
    # 사용자의 모든 피드백 조회
    feedbacks = await supabase.get_user_feedbacks(sample_feedback["user_id"])
    assert len(feedbacks) > 0
    assert any(f.id == result.id for f in feedbacks)
