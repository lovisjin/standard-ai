import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
from datetime import datetime
from config.logger import logger

load_dotenv()

def save_to_sheet(user_id: str, text: str, summary: str) -> str:
    """
    텍스트 요약 결과를 Google Sheet에 저장합니다.
    
    Args:
        user_id (str): 사용자 ID
        text (str): 원본 텍스트
        summary (str): 요약된 텍스트
        
    Returns:
        str: 저장된 Google Sheet의 URL
    """
    logger.debug("Google Sheets 저장 시작")
    
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    creds = Credentials.from_service_account_file(
        os.getenv('GOOGLE_SERVICE_ACCOUNT_PATH'),
        scopes=SCOPES
    )
    
    client = gspread.authorize(creds)
    
    SHEET_KEY = os.getenv('GOOGLE_SHEET_KEY')
    try:
        sheet = client.open_by_key(SHEET_KEY)
        logger.debug(f"기존 시트 열기 성공: {SHEET_KEY}")
    except Exception:
        logger.info("기존 시트가 없어 새로 생성합니다")
        sheet = client.create('Text Summary Results')
        sheet.share('anyone', perm_type='user', role='reader')
    
    worksheet = sheet.get_worksheet(0) or sheet.add_worksheet('Summaries', 1000, 4)
    
    if worksheet.row_values(1) == []:
        logger.debug("헤더 행 추가")
        worksheet.append_row(['Timestamp', 'User ID', 'Original Text', 'Summary'])
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    worksheet.append_row([timestamp, user_id, text, summary])
    logger.debug(f"새로운 행 추가 완료: {user_id}")
    
    return sheet.url
