import os
import json
import requests
from dotenv import load_dotenv
from config.logger import logger

load_dotenv()

def send_slack_notification(user_id: str, summary: str) -> None:
    """
    Slack 웹후크를 통해 요약 결과를 알림으로 전송합니다.
    
    Args:
        user_id (str): 사용자 ID
        summary (str): 요약된 텍스트
    """
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if not webhook_url:
        logger.warning("SLACK_WEBHOOK_URL이 설정되지 않아 알림을 전송하지 않습니다")
        return

    logger.debug(f"Slack 알림 전송 시작 - user_id: {user_id}")
    payload = {"text": f"유저: {user_id}\n요약 결과: {summary}"}
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
        if response.status_code != 200:
            logger.error(f"Slack 전송 오류: {response.status_code}, 응답: {response.text}")
        else:
            logger.debug("Slack 알림 전송 완료")
    except Exception as e:
        logger.error(f"Slack 전송 중 예외 발생: {str(e)}")
