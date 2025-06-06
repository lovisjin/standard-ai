import os
from typing import Dict, Any, Optional
import openai
import asyncio
from config.logger import logger
from tenacity import retry, stop_after_attempt, wait_exponential

class PromptEngine:
    def __init__(self, model: str = "gpt-4"):
        self.model = model
        self.prompt_templates: Dict[str, str] = {}
        self.default_params: Dict[str, Any] = {}
        
        # OpenAI API 키 확인
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")

    def register_prompt(self, skill_name: str, template: str, default_params: Optional[Dict[str, Any]] = None):
        """프롬프트 템플릿을 등록합니다."""
        self.prompt_templates[skill_name] = template
        if default_params:
            self.default_params[skill_name] = default_params

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def run_prompt(self, 
                        prompt: str, 
                        temperature: float = 1.0,
                        max_tokens: Optional[int] = None) -> str:
        """
        프롬프트를 실행하고 응답을 반환합니다.
        
        Args:
            prompt: 실행할 프롬프트
            temperature: 응답의 창의성 정도 (0.0 ~ 2.0)
            max_tokens: 최대 토큰 수 (None인 경우 기본값 사용)
            
        Returns:
            AI 모델의 응답
            
        Raises:
            Exception: API 호출 중 오류 발생 시
        """
        try:
            params: Dict[str, Any] = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature
            }
            
            if max_tokens:
                params["max_tokens"] = max_tokens
                
            response = await openai.ChatCompletion.acreate(**params)
            
            if not response.choices:
                raise Exception("응답에 선택지가 없습니다.")
                
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"프롬프트 실행 중 오류 발생: {str(e)}")
            logger.debug(f"프롬프트: {prompt[:200]}...")
            raise

    async def generate_prompt(self, skill_name: str, params: Optional[Dict[str, Any]] = None) -> str:
        """주어진 스킬과 매개변수로 프롬프트를 생성합니다."""
        if skill_name not in self.prompt_templates:
            raise KeyError(f"Unknown skill: {skill_name}")

        template = self.prompt_templates[skill_name]
        final_params = self.default_params.get(skill_name, {}).copy()
        if params:
            final_params.update(params)

        return template.format(**final_params)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

async def run_gpt_summary(text: str) -> str:
    prompt = f"""
    아래 글을 간결하게 요약해줘:

    """
    {text.strip()}
    """
    """

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 전문 요약 비서입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(f"요약 실패: {str(e)}")
