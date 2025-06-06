import os
from typing import Any, Dict, List, Optional
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config.logger import logger

class SheetWriter:
    def __init__(self):
        """Google Sheets API 클라이언트 초기화"""
        try:
            # API 스코프 설정
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # 서비스 계정 인증
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                'google_credentials.json', 
                scope
            )
            
            self.client = gspread.authorize(credentials)
            self.spreadsheet_id = os.getenv("GOOGLE_SHEET_ID")
            
            if not self.spreadsheet_id:
                raise ValueError("GOOGLE_SHEET_ID 환경 변수가 설정되지 않았습니다.")
                
            self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            logger.info("Google Sheets 클라이언트 초기화 완료")
            
        except Exception as e:
            logger.error(f"Google Sheets 클라이언트 초기화 실패: {str(e)}")
            raise

    def _get_or_create_worksheet(self, skill_name: str) -> gspread.Worksheet:
        """스킬명에 해당하는 워크시트를 가져오거나 생성"""
        try:
            # 기존 워크시트 찾기
            worksheet = self.spreadsheet.worksheet(skill_name)
            logger.info(f"기존 워크시트 사용: {skill_name}")
            return worksheet
        except gspread.WorksheetNotFound:
            # 새 워크시트 생성
            worksheet = self.spreadsheet.add_worksheet(
                title=skill_name,
                rows=1000,
                cols=10
            )
            # 헤더 추가
            headers = [
                "Timestamp",
                "User ID",
                "Input Text",
                "Output",
                "Duration (sec)",
                "Status",
                "Error (if any)"
            ]
            worksheet.append_row(headers)
            logger.info(f"새 워크시트 생성 완료: {skill_name}")
            return worksheet

    async def write_result_to_sheet(
        self,
        skill_name: str,
        input_text: str,
        output: Any,
        user_id: Optional[str] = None,
        duration: Optional[float] = None,
        error: Optional[str] = None
    ):
        """스킬 실행 결과를 시트에 기록"""
        try:
            worksheet = self._get_or_create_worksheet(skill_name)
            
            # 결과를 문자열로 변환
            if isinstance(output, (dict, list)):
                output_str = str(output)
            else:
                output_str = output
                
            # 행 데이터 준비
            row_data = [
                datetime.utcnow().isoformat(),  # Timestamp
                user_id or "anonymous",         # User ID
                input_text[:1000],             # Input (최대 1000자)
                output_str[:1000],             # Output (최대 1000자)
                str(duration) if duration else "",  # Duration
                "error" if error else "success",    # Status
                str(error) if error else ""         # Error message
            ]
            
            # 데이터 추가
            worksheet.append_row(row_data)
            logger.info(f"결과 기록 완료 - skill: {skill_name}, user: {user_id}")
            
        except Exception as e:
            logger.error(f"결과 기록 중 오류 발생: {str(e)}")
            # 시트 기록 실패는 크리티컬하지 않으므로 예외를 전파하지 않음
            
    async def get_skill_stats(
        self,
        skill_name: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """특정 스킬의 실행 통계를 조회"""
        try:
            worksheet = self._get_or_create_worksheet(skill_name)
            
            # 모든 데이터 가져오기
            all_data = worksheet.get_all_records()
            
            # 날짜 범위에 해당하는 데이터 필터링
            filtered_data = [
                row for row in all_data
                if start_date <= datetime.fromisoformat(row["Timestamp"]) <= end_date
            ]
            
            # 통계 계산
            total_executions = len(filtered_data)
            error_count = sum(1 for row in filtered_data if row["Status"] == "error")
            success_rate = (total_executions - error_count) / total_executions if total_executions > 0 else 0
            
            # 평균 실행 시간 계산 (duration이 있는 경우만)
            durations = [
                float(row["Duration (sec)"])
                for row in filtered_data
                if row["Duration (sec)"]
            ]
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            return {
                "total_executions": total_executions,
                "success_count": total_executions - error_count,
                "error_count": error_count,
                "success_rate": success_rate,
                "avg_duration": avg_duration,
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"통계 조회 중 오류 발생: {str(e)}")
            raise

# 전역 SheetWriter 인스턴스
sheet_writer = SheetWriter()
