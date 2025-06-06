from typing import Dict, Any, List
import openai
import whisper
from pathlib import Path
import tempfile
from ..core.base_skill import BaseSkill

class VoiceMemoSummarizer(BaseSkill):
    def __init__(self, prompt_engine):
        super().__init__(prompt_engine)
        self.whisper_model = whisper.load_model("base")

    def register_prompts(self):
        summary_template = """다음 음성 메모 내용을 요약해주세요:

메모 내용:
{transcription}

요약 요구사항:
- 핵심 메시지와 주요 포인트 추출
- 시간 순서대로 정리
- 액션 아이템이 있다면 별도로 표시
- {additional_requirements}"""

        self.prompt_engine.register_prompt(
            "summarize_voice_memo",
            summary_template,
            {"additional_requirements": "간단명료하게 작성"}
        )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        audio_path = input_data.get("audio_path")
        if not audio_path:
            raise ValueError("No audio file provided for transcription")

        if not Path(audio_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # 음성을 텍스트로 변환
        result = await self.whisper_model.transcribe(audio_path)
        transcription = result["text"]

        # 텍스트 요약
        additional_requirements = input_data.get("additional_requirements", "간단명료하게 작성")
        prompt = self.prompt_engine.generate_prompt(
            "summarize_voice_memo",
            {
                "transcription": transcription,
                "additional_requirements": additional_requirements
            }
        )

        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional voice memo summarizer."},
                {"role": "user", "content": prompt}
            ]
        )

        summary = response.choices[0].message.content

        return {
            "transcription": transcription,
            "summary": summary,
            "duration": result.get("duration", 0),  # 음성 길이(초)
            "language": result.get("language", "unknown"),  # 감지된 언어
            "action_items": self._extract_action_items(summary)
        }

    def _extract_action_items(self, summary: str) -> List[str]:
        action_items = []
        in_action_section = False

        for line in summary.split("\n"):
            if "액션 아이템" in line or "할 일" in line:
                in_action_section = True
                continue
            
            if in_action_section and line.strip():
                if line.startswith(("- ", "* ", "• ")):
                    action_items.append(line[2:].strip())
                else:
                    break

        return action_items
