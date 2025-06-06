from typing import Dict, Any, List
from core.prompt_engine import PromptEngine
from core.base_skill import BaseSkill
import json
from config.logger import logger

class ChecklistExtractor(BaseSkill):
    skill_name = "checklist_extractor"
    
    def __init__(self):
        super().__init__()
        self.prompt_engine = PromptEngine()
        
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        if "content" not in input_data or not input_data["content"]:
            logger.error("점검 내용이 없습니다")
            return False
        return True
        
    async def _process_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        점검 내용을 체크리스트로 변환
        
        Args:
            input_data: 변환할 점검 내용이 포함된 입력 데이터
            
        Returns:
            구조화된 체크리스트와 메타데이터
        """
        content = input_data["content"]
        
        prompt = f"""
        다음 점검 내용을 체계적인 체크리스트로 변환해주세요.
        JSON 형식으로 반환해주세요:
        
        {{
            "title": "체크리스트 제목",
            "categories": [
                {{
                    "name": "카테고리명",
                    "items": [
                        {{
                            "text": "점검 항목",
                            "status": "완료" or "미완료" or "해당없음",
                            "priority": "상" or "중" or "하",
                            "comment": "특이사항 (있는 경우)"
                        }}
                    ]
                }}
            ]
        }}
        
        점검 내용:
        {content}
        """
        
        response = await self.prompt_engine.run_prompt(
            prompt=prompt,
            temperature=0.3
        )
        
        # JSON 파싱 및 검증
        try:
            checklist = json.loads(response)
            
            # 필수 필드 검증
            if not all(key in checklist for key in ["title", "categories"]):
                raise ValueError("필수 필드가 누락되었습니다")
                
            # 메타데이터 계산
            total_items = sum(len(category["items"]) for category in checklist["categories"])
            completed_items = sum(
                sum(1 for item in category["items"] if item["status"] == "완료")
                for category in checklist["categories"]
            )
            
            high_priority_items = sum(
                sum(1 for item in category["items"] if item["priority"] == "상")
                for category in checklist["categories"]
            )
            
            return {
                "checklist": checklist,
                "metadata": {
                    "total_items": total_items,
                    "completed_items": completed_items,
                    "completion_rate": completed_items / total_items if total_items > 0 else 0,
                    "high_priority_count": high_priority_items
                }
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"체크리스트 처리 중 오류: {str(e)}")
            raise
