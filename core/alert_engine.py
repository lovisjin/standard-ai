from typing import Any, Dict
from datetime import datetime, timedelta
from utils.slack import slack
from config.logger import logger

class AlertEngine:
    def __init__(self):
        # 알림 조건 설정
        self.conditions = {
            "summarizer": {
                "max_length": 1000,  # 요약 최대 길이
                "min_length": 50,    # 요약 최소 길이
            },
            "ppt_writer": {
                "min_slides": 3,     # 최소 슬라이드 수
                "max_slides": 20,    # 최대 슬라이드 수
            },
            "voice_memo_summarizer": {
                "max_duration": 600,  # 최대 음성 길이 (초)
            },
            "feedback_stats": {
                "min_positive_rate": 0.3,  # 최소 긍정 비율
            }
        }
        
        # 알림 기록 (중복 방지)
        self._alert_history = {}

    async def check_conditions(self, skill_name: str, result: Dict[str, Any]) -> None:
        """스킬 실행 결과가 알림 조건에 해당하는지 확인"""
        if skill_name not in self.conditions:
            return

        alerts = []
        conditions = self.conditions[skill_name]

        try:
            # 스킬별 조건 체크
            if skill_name == "summarizer":
                summary = result if isinstance(result, str) else result.get("summary", "")
                if len(summary) > conditions["max_length"]:
                    alerts.append(f"요약이 너무 깁니다 ({len(summary)} 자)")
                elif len(summary) < conditions["min_length"]:
                    alerts.append(f"요약이 너무 짧습니다 ({len(summary)} 자)")

            elif skill_name == "ppt_writer":
                if isinstance(result, dict) and "slide_count" in result:
                    slides = result["slide_count"]
                    if slides < conditions["min_slides"]:
                        alerts.append(f"슬라이드 수가 너무 적습니다 ({slides}장)")
                    elif slides > conditions["max_slides"]:
                        alerts.append(f"슬라이드 수가 너무 많습니다 ({slides}장)")

            elif skill_name == "voice_memo_summarizer":
                if isinstance(result, dict) and "duration" in result:
                    duration = result["duration"]
                    if duration > conditions["max_duration"]:
                        alerts.append(f"음성이 너무 깁니다 ({duration:.1f}초)")

            elif skill_name == "feedback_stats":
                if isinstance(result, dict) and "positive_rate" in result:
                    pos_rate = result["positive_rate"]
                    if pos_rate < conditions["min_positive_rate"]:
                        alerts.append(f"긍정 비율이 낮습니다 ({pos_rate:.1%})")

            # 알림 전송 (중복 방지)
            if alerts:
                alert_key = f"{skill_name}_{datetime.utcnow().strftime('%Y%m%d')}"
                if alert_key not in self._alert_history:
                    await self._send_alerts(skill_name, alerts, result)
                    self._alert_history[alert_key] = datetime.utcnow()
                    self._cleanup_history()

        except Exception as e:
            logger.error(f"알림 조건 체크 중 오류 발생: {str(e)}")

    async def _send_alerts(self, skill_name: str, alerts: list, result: Dict[str, Any]) -> None:
        """알림 메시지 전송"""
        message = f"⚠️ *{skill_name}* 실행 결과 주의 필요\n"
        message += "\n".join([f"- {alert}" for alert in alerts])
        
        if isinstance(result, dict):
            message += f"\n\n실행 결과:\n```{str(result)[:500]}```"
        
        await slack.send_message(
            text=message,
            channel="#alerts",
            username="StandardAI Monitor",
            emoji=":warning:"
        )

    def _cleanup_history(self) -> None:
        """24시간 이상 지난 알림 기록 삭제"""
        now = datetime.utcnow()
        self._alert_history = {
            k: v for k, v in self._alert_history.items()
            if now - v < timedelta(days=1)
        }

# 전역 AlertEngine 인스턴스
alert_engine = AlertEngine()

async def check_alert_conditions(skill_name: str, result: Dict[str, Any]) -> None:
    """스킬 실행 결과의 알림 조건 체크 (전역 함수)"""
    await alert_engine.check_conditions(skill_name, result)
