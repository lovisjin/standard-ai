from typing import Dict, Any
from core.prompt_engine import PromptEngine
from core.base_skill import BaseSkill
from config.logger import logger

class Summarizer(BaseSkill):
    skill_name = "summarizer"

    def __init__(self, *args, **kwargs):
        """
        Accept an optional prompt_engine arg, fall back to default PromptEngine.
        """
        super().__init__()  # BaseSkill 초기화
        # 기본 엔진
        self.prompt_engine = PromptEngine()
        # args[0]이 넘어왔다면 덮어쓰기
        if args:
            self.prompt_engine = args[0]

        
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        입력 데이터 유효성 검사
        
        Args:
            input_data: 검사할 입력 데이터
        """
        if "text" not in input_data or not input_data["text"]:
            logger.error("텍스트가 없습니다")
            return False
        return True
        
    async def _process_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        텍스트 요약 처리
        
        Args:
            input_data: 요약할 텍스트가 포함된 입력 데이터
            
        Returns:
            요약 결과
        """
        text = input_data["text"]
        
        prompt = f"""
        다음 텍스트를 명확하고 간결하게 요약해주세요:
        
        {text}
        """
        
        summary = await self.prompt_engine.run_prompt(
            prompt=prompt,
            temperature=0.3  # 더 일관된 요약을 위해 낮은 temperature 사용
        )
        
        return {
            "original_text": text,
            "summary": summary,
            "length_reduction": len(summary) / len(text)
        }
