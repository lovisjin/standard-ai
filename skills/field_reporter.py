from typing import Dict, Any, List
from core.prompt_engine import PromptEngine
from core.base_skill import BaseSkill
from config.logger import logger

class FieldReporter(BaseSkill):
    skill_name = "field_reporter"
    
    def __init__(self):
        super().__init__()
        self.prompt_engine = PromptEngine()
        
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        if "field_notes" not in input_data or not input_data["field_notes"]:
            logger.error("현장 기록이 없습니다")
            return False
        return True
        
    async def _process_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        현장 기록을 분석하여 보고서 생성
        
        Args:
            input_data: 현장 기록이 포함된 입력 데이터
            
        Returns:
            분석된 보고서와 메타데이터
        """
        field_notes = input_data["field_notes"]
        
        # 주요 내용 추출
        analysis_prompt = f"""
        다음 현장 기록을 분석하여 주요 내용을 추출해주세요:
        1. 주요 발견사항
        2. 문제점
        3. 개선사항
        4. 긴급 조치 필요사항
        
        현장 기록:
        {field_notes}
        """
        
        analysis = await self.prompt_engine.run_prompt(
            prompt=analysis_prompt,
            temperature=0.3
        )
        
        # 요약 생성
        summary_prompt = f"""
        다음 현장 분석 내용을 간단히 요약해주세요 (3-4문장):
        
        {analysis}
        """
        
        summary = await self.prompt_engine.run_prompt(
            prompt=summary_prompt,
            temperature=0.3
        )
        
        # 우선순위 태그 생성
        priority_prompt = f"""
        다음 분석 내용에서 우선순위가 높은 항목들을 태그로 추출해주세요 (쉼표로 구분):
        
        {analysis}
        """
        
        priority_tags = await self.prompt_engine.run_prompt(
            prompt=priority_prompt,
            temperature=0.3
        )
        
        return {
            "original_notes": field_notes,
            "analysis": analysis,
            "summary": summary,
            "priority_tags": [tag.strip() for tag in priority_tags.split(",")],
            "timestamp": input_data.get("timestamp", None)
        }
