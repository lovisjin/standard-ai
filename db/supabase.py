import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from supabase import create_client, Client
from dotenv import load_dotenv
from config.logger import logger
from models.feedback import FeedbackCreate, FeedbackInDB, UserCreate, UserInDB

load_dotenv()

class SupabaseClient:
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase 환경 변수가 설정되지 않았습니다.")
        
        self.client: Client = create_client(supabase_url, supabase_key)
        logger.info("Supabase 클라이언트 초기화 완료")

    async def create_user(self, user: UserCreate) -> UserInDB:
        """새로운 사용자를 생성합니다."""
        try:
            result = self.client.table("users").insert({
                "name": user.name
            }).execute()
            
            if len(result.data) == 0:
                raise Exception("사용자 생성 실패")
                
            logger.info(f"새로운 사용자 생성 완료: name={user.name}")
            return UserInDB(**result.data[0])
            
        except Exception as e:
            logger.error(f"사용자 생성 중 오류 발생: {str(e)}")
            raise

    async def get_user(self, user_id: UUID) -> Optional[UserInDB]:
        """사용자 정보를 조회합니다."""
        try:
            result = self.client.table("users").select("*").eq("id", str(user_id)).execute()
            
            if len(result.data) > 0:
                return UserInDB(**result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"사용자 조회 중 오류 발생: {str(e)}")
            raise

    async def create_feedback(self, feedback: FeedbackCreate) -> FeedbackInDB:
        """새로운 피드백을 생성합니다."""
        try:
            # 사용자 존재 여부 확인
            user = await self.get_user(feedback.user_id)
            if not user:
                raise ValueError("존재하지 않는 사용자입니다.")

            # 피드백 저장
            data = {
                "user_id": str(feedback.user_id),
                "content": feedback.content,
                "skill": feedback.skill,
                "emotion": feedback.emotion,
                "keywords": feedback.keywords,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("feedbacks").insert(data).execute()
            
            if len(result.data) == 0:
                raise Exception("피드백 저장 실패")
                
            logger.info(f"새로운 피드백 저장 완료: user_id={feedback.user_id}")
            return FeedbackInDB(**result.data[0])
            
        except Exception as e:
            logger.error(f"피드백 저장 중 오류 발생: {str(e)}")
            raise

    async def get_user_feedbacks(self, user_id: UUID) -> List[FeedbackInDB]:
        """특정 사용자의 모든 피드백을 조회합니다."""
        try:
            result = self.client.table("feedbacks").select("*").eq("user_id", str(user_id)).order("created_at", desc=True).execute()
            return [FeedbackInDB(**item) for item in result.data]
            
        except Exception as e:
            logger.error(f"사용자 피드백 목록 조회 중 오류 발생: {str(e)}")
            raise

    async def get_feedback_stats(self, 
                               start_date: datetime, 
                               end_date: datetime, 
                               user_id: Optional[UUID] = None) -> Dict[str, Any]:
        """주어진 기간 동안의 피드백 통계를 조회합니다."""
        try:
            # 기본 쿼리 설정
            query = self.client.table("feedbacks").select("*")
            
            # 날짜 범위 필터 적용
            query = query.gte("created_at", start_date.isoformat())
            query = query.lte("created_at", end_date.isoformat())
            
            # 사용자 ID 필터 적용 (있는 경우)
            if user_id:
                query = query.eq("user_id", str(user_id))
            
            # 쿼리 실행
            result = query.execute()
            feedbacks = result.data
            
            # 통계 계산
            total_count = len(feedbacks)
            emotion_counts = {}
            skill_counts = {}
            keyword_counts = {}
            
            for feedback in feedbacks:
                # 감정 집계
                if feedback["emotion"]:
                    emotion_counts[feedback["emotion"]] = emotion_counts.get(feedback["emotion"], 0) + 1
                
                # 스킬 집계
                if feedback["skill"]:
                    skill_counts[feedback["skill"]] = skill_counts.get(feedback["skill"], 0) + 1
                
                # 키워드 집계
                if feedback["keywords"]:
                    for keyword in feedback["keywords"]:
                        keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            
            # 최근 피드백 5개 추출
            recent_feedbacks = sorted(
                feedbacks, 
                key=lambda x: x["created_at"], 
                reverse=True
            )[:5]
            
            return {
                "total_count": total_count,
                "emotion_stats": emotion_counts,
                "skill_stats": skill_counts,
                "keyword_stats": keyword_counts,
                "recent_feedbacks": recent_feedbacks
            }
            
        except Exception as e:
            logger.error(f"피드백 통계 조회 중 오류 발생: {str(e)}")
            raise

# 전역 Supabase 클라이언트
supabase = SupabaseClient()
