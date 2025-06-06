from typing import Dict, Any, Optional
from core.base_skill import BaseSkill
from datetime import datetime, timedelta
from db.supabase import supabase
from config.logger import logger

class FeedbackStatsSkill(BaseSkill):
    """피드백 통계 스킬"""
    
    skill_name = "feedback_stats"
    
    def register_prompts(self):
        pass  # 이 스킬은 프롬프트를 사용하지 않음
        
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        if "start_date" not in input_data or "end_date" not in input_data:
            logger.error("시작일 또는 종료일이 없습니다")
            return False
            
        try:
            start_date = datetime.fromisoformat(input_data["start_date"])
            end_date = datetime.fromisoformat(input_data["end_date"])
            
            if end_date < start_date:
                logger.error("종료일이 시작일보다 앞섭니다")
                return False
                
            if end_date - start_date > timedelta(days=365):
                logger.error("조회 기간이 1년을 초과합니다")
                return False
                
        except ValueError as e:
            logger.error(f"날짜 형식이 잘못되었습니다: {str(e)}")
            return False
            
        return True
        
    async def _process_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        피드백 통계 처리
        
        Args:
            input_data: 통계 조회 조건이 포함된 입력 데이터
            
        Returns:
            처리된 통계 결과
        """
        start_date = datetime.fromisoformat(input_data["start_date"])
        end_date = datetime.fromisoformat(input_data["end_date"])
        user_id = input_data.get("user_id")
        
        # Supabase에서 통계 조회
        stats = await supabase.get_feedback_stats(
            start_date=start_date,
            end_date=end_date,
            user_id=user_id
        )
        
        # 추가 메타데이터 계산
        period_days = (end_date - start_date).days
        daily_average = stats["total_count"] / period_days if period_days > 0 else 0
        
        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "user_id": user_id or "전체",
            "total_count": stats["total_count"],
            "positive_rate": stats["positive_rate"],
            "negative_rate": stats["negative_rate"],
            "recent_feedbacks": stats["recent_feedbacks"],
            "metadata": {
                "period_days": period_days,
                "daily_average": daily_average,
                "generated_at": datetime.utcnow().isoformat()
            }
        }
