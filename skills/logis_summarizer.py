from utils.sheet import save_to_sheet
from utils.slack import send_slack_notification
from config.logger import logger
import os
from typing import Dict, Any
import openai
from dotenv import load_dotenv

load_dotenv()

def call_gpt_summary(text: str) -> str:
    """
    GPT API를 사용하여 텍스트를 요약합니다.
    
    Args:
        text (str): 요약할 텍스트
        
    Returns:
        str: 요약된 텍스트
    """
    logger.debug(f"GPT 요약 시작: {text[:100]}...")
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes text concisely in Korean."},
                {"role": "user", "content": f"다음 텍스트를 한 문장으로 요약해주세요: {text}"}
            ],
            temperature=0.7,
            max_tokens=100
        )
        
        summary = response.choices[0].message.content.strip()
        logger.debug(f"GPT 요약 완료: {summary}")
        return summary
        
    except Exception as e:
        logger.error(f"GPT API 호출 중 오류 발생: {str(e)}")
        raise

def execute(user_id: str, text: str) -> Dict[str, str]:
    """
    스킬 실행 진입점: GPT 요약 → Google Sheets 저장 → Slack 알림 전송
    
    Args:
        user_id (str): 사용자 ID
        text (str): 요약할 텍스트
        
    Returns:
        Dict[str, str]: summary와 sheet_url을 포함한 결과
    """
    logger.info(f"logis_summarizer 스킬 실행 시작 - user_id: {user_id}")
    
    # 1. GPT 요약
    summary = call_gpt_summary(text)
    
    # 2. Google Sheets에 저장
    sheet_url = save_to_sheet(user_id, text, summary)
    
    # 3. Slack 알림 전송
    send_slack_notification(user_id, summary)
    
    logger.info("logis_summarizer 스킬 실행 완료")
    return {
        "summary": summary,
        "sheet_url": sheet_url
    }
