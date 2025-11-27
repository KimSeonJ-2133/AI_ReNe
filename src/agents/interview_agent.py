"""
면접 진행을 위한 Core AI Logic (Evaluator + Persona)
"""

import os
import json
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from core.config import settings


class InterviewAgent:
    def __init__(self):
        # prompts 폴더 경로 설정 (상대 경로)
        self.prompt_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../prompts")
        )

        # LLM 초기화 (JSON 출력을 위해 모델 분리 기능)
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7,  # 확인 필요
            openai_api_key=settings.OPENAI_API_KEY,
        )
        self.json_llm = ChatOpenAI(
            model="gpt-4o", temperature=0.1, response_format={"type": "json_object"}
        )

    def _load_prompt(self, filename: str) -> str:
        """Mark Down 프롬프트 파일 로드"""
        path = os.path.join(self.prompt_dir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"프롬프트 파일을 찾을 수 없습니다. : {path}")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    async def run_evaluator(
        self, context_type: str, question: str, answer: str
    ) -> Dict[str, Any]:
        """
        [Evaluator] Universal_Evaluator.md 사용
        """
        # 범용 Evaluator 프롬프트 로드
        raw_prompt = self._load_prompt("Universal_Evaluator.md")

        # 변수 주입 (Langchain Template 대신 단순 치환 사용 - 마크다운 호환성 위함)
        system_content = (
            raw_prompt.replace("{context_type}", str(context_type))
            .replace("{question_text}", str(question))
            .replace("{answer_text}", str(answer))
        )

        # JSON 모드로 호출
        response = await self.json_llm.ainvoke([SystemMessage(content=system_prompt)])
        return json.loads(response.content)

    async def generate_reply(
        self,
        persona_file: str,
        user_text: str,
        input_vars: Dict[str, str],
        chat_history: List[Any] = [],
    ) -> str:
        """
        [Persona] 면접관 답변 생성
        """

        # 페르소나 파일 로드
        raw_prompt = self._load_prompt(persona_file)

        # 동적 변수 주입
        system_content = raw_prompt
        for key, value in input_vars.items():
            # 안전한 치환을 위해 str로 변환
            system_content = system_content.replace(f"{{{key}}}", str(value))

        # 답변 생성
        messages = (
            [SystemMessage(content=system_content)]
            + chat_history
            + [HumanMessage(content=user_text)]
        )

        response = await self.llm.ainvoke(messages)
        return response.content


# 싱글톤 인스턴스 (Service 에서 import 해서 사용)
interview_agent = InterviewAgent()
