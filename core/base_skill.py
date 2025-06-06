from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime
from utils.sheet_writer import SheetWriter
from utils.slack import SlackNotifier
from core.alert_engine import AlertEngine
from config.logger import logger

class BaseSkill(ABC):
    skill_name: str = None
    
    def __init__(self):
        if not self.skill_name:
            raise ValueError("skill_name이 설정되지 않았습니다.")
            
        self.sheet_writer = SheetWriter()
        self.slack = SlackNotifier()
        self.alert_engine = AlertEngine()
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        스킬을 실행하고 결과를 처리합니다.
        
        Args:
            input_data: 입력 데이터
            
        Returns:
            처리된 결과
        """
        try:
            # 실행 시작 로깅
            logger.info(f"{self.skill_name} 실행 시작")
            start_time = datetime.utcnow()
            
            # 입력 데이터 검증
            if not await self.validate_input(input_data):
                raise ValueError("잘못된 입력 데이터")
            
            # 메인 프로세스 실행
            result = await self._process_internal(input_data)
            
            # 결과 후처리
            processed_result = await self._post_process(result)
            
            # 실행 완료 처리
            await self.on_after_run(processed_result, start_time)
            
            return processed_result
            
        except Exception as e:
            error_msg = f"{self.skill_name} 실행 중 오류 발생: {str(e)}"
            logger.error(error_msg)
            
            # 오류 알림 전송
            await self._handle_error(error_msg, input_data)
            raise
            
    @abstractmethod
    async def _process_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        스킬의 핵심 처리 로직을 구현합니다.
        
        Args:
            input_data: 처리할 입력 데이터
            
        Returns:
            처리 결과
        """
        pass
        
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        입력 데이터의 유효성을 검사합니다.
        
        Args:
            input_data: 검사할 입력 데이터
            
        Returns:
            검사 결과
        """
        return True
        
    async def _post_process(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        결과를 후처리합니다.
        
        Args:
            result: 처리할 결과 데이터
            
        Returns:
            후처리된 결과
        """
        return result
        
    async def on_after_run(self, result: Dict[str, Any], start_time: datetime) -> None:
        """
        실행 완료 후 처리를 수행합니다.
        
        Args:
            result: 처리 결과
            start_time: 실행 시작 시간
        """
        # 스프레드시트에 결과 기록
        await self.sheet_writer.write_result(
            skill_name=self.skill_name,
            start_time=start_time,
            result=result
        )
        
        # Slack 알림 전송
        preview = self._get_result_preview(result)
        message = f"✅ *{self.skill_name}* 실행 완료\n```{preview}```"
        await self.slack.send_message(message)
        
        # 모니터링 조건 체크
        await self.alert_engine.check_conditions(
            skill_name=self.skill_name,
            result=result
        )
        
    def _get_result_preview(self, result: Dict[str, Any]) -> str:
        """
        결과의 미리보기를 생성합니다.
        
        Args:
            result: 처리 결과
            
        Returns:
            미리보기 텍스트
        """
        if isinstance(result, dict):
            preview = result.get("summary") or str(result)
        else:
            preview = str(result)
        return preview[:500]
        
    async def _handle_error(self, error_msg: str, input_data: Optional[Dict[str, Any]] = None) -> None:
        """
        오류를 처리합니다.
        
        Args:
            error_msg: 오류 메시지
            input_data: 오류 발생 시의 입력 데이터
        """
        context = {
            "skill_name": self.skill_name,
            "error": error_msg,
            "input_data": input_data
        }
        
        await self.alert_engine.send_alert(
            level="error",
            message=error_msg,
            context=context
        )
        
        await self.slack.send_error_notification(
            skill_name=self.skill_name,
            error_message=error_msg,
            context=context
        )
