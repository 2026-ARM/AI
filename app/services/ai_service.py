from __future__ import annotations

import json
import os
from typing import List

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None


class AIServiceError(Exception):
    pass


class LLMService:
    def __init__(self) -> None:
        self.provider = os.getenv("AI_PROVIDER", "openai").lower()
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        if self.provider != "openai":
            raise AIServiceError(
                "현재 구현은 OpenAI 기반입니다. Gemini를 사용하려면 `google-generativeai` 패키지를 추가하고 `AI_PROVIDER=gemini` 로 구성하세요."
            )

        if OpenAI is None:
            raise AIServiceError(
                "openai 패키지가 설치되어 있지 않습니다. requirements.txt에 openai를 추가하세요."
            )

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise AIServiceError("OPENAI_API_KEY가 설정되어 있지 않습니다.")

        self.client = OpenAI(api_key=api_key)

    def _flatten_response(self, response) -> str:
        if hasattr(response, "output_text"):
            return response.output_text
        if getattr(response, "choices", None):
            first_choice = response.choices[0]
            if getattr(first_choice, "message", None):
                return first_choice.message.get("content", "")
            if getattr(first_choice, "text", None):
                return first_choice.text
        return str(response)

    def _complete(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.2) -> str:
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        return self._flatten_response(response).strip()

    def _clean_json(self, text: str) -> str:
        if "{" not in text and "[" not in text:
            return text

        start = min((text.find("{"), text.find("["))) if text.find("{") != -1 else text.find("[")
        end = max((text.rfind("}"), text.rfind("]")))
        if start != -1 and end != -1:
            return text[start : end + 1]

        return text

    def _parse_json(self, raw: str):
        try:
            cleaned = self._clean_json(raw)
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise AIServiceError(f"LLM 응답 JSON 파싱에 실패했습니다: {exc}\n응답 내용:\n{raw}")

    def _make_context(self, chunks: List[dict], max_chars: int = 6000) -> str:
        text_blocks = []
        length = 0
        for item in chunks:
            block = f"[Chunk {item['chunk_index']}]:\n{item['text']}\n\n"
            if length + len(block) > max_chars:
                break
            text_blocks.append(block)
            length += len(block)
        return "".join(text_blocks)

    def create_summary(self, chunks: List[dict], options: dict) -> str:
        context = self._make_context(chunks)
        prompt = (
            "아래 텍스트를 한국어로 요약해 주세요."
            f"\n- 난이도: {options.get('difficulty', 'medium')}"
            f"\n- 언어: {options.get('language', 'ko')}"
            "\n- 최대 3개의 단락으로 간결하게 정리하세요.\n\n"
            f"{context}"
        )
        return self._complete(prompt, max_tokens=1000)

    def create_quiz(self, chunks: List[dict], options: dict) -> List[dict]:
        context = self._make_context(chunks)
        quiz_types = options.get("quizTypes", ["mcq", "ox"])
        count = options.get("countPerType", 3)
        prompt = (
            "다음 텍스트를 바탕으로 퀴즈를 생성하세요."
            f"\n- 유형: {', '.join(quiz_types)}"
            f"\n- 개수: {count}개씩"
            f"\n- 난이도: {options.get('difficulty', 'medium')}"
            f"\n- 언어: {options.get('language', 'ko')}"
            "\n- 결과는 JSON 배열로 반환하세요."
            "\n- 각 항목은 question, options(필요한 경우), correct_answer, explanation 형태여야 합니다.\n\n"
            f"{context}"
        )
        raw = self._complete(prompt, max_tokens=1200)
        quizzes = self._parse_json(raw)
        if not isinstance(quizzes, list):
            raise AIServiceError("퀴즈 생성 결과가 배열이 아닙니다.")
        return quizzes

    def create_flashcards(self, chunks: List[dict], options: dict) -> List[dict]:
        context = self._make_context(chunks)
        card_types = options.get("cardTypes", ["concept", "definition"])
        count = options.get("countPerType", 3)
        prompt = (
            "다음 텍스트를 바탕으로 플래시카드를 생성하세요."
            f"\n- 유형: {', '.join(card_types)}"
            f"\n- 개수: {count}개씩"
            f"\n- 난이도: {options.get('difficulty', 'medium')}"
            f"\n- 언어: {options.get('language', 'ko')}"
            "\n- 결과는 JSON 배열로 반환하세요."
            "\n- 각 항목은 front, back, type 형태여야 합니다.\n\n"
            f"{context}"
        )
        raw = self._complete(prompt, max_tokens=1200)
        cards = self._parse_json(raw)
        if not isinstance(cards, list):
            raise AIServiceError("플래시카드 생성 결과가 배열이 아닙니다.")
        return cards
