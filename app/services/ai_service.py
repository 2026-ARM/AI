from __future__ import annotations

import os
import json
from typing import Any, List

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

        starts = [idx for idx in (text.find("{"), text.find("[")) if idx != -1]
        start = min(starts) if starts else -1
        end = max((text.rfind("}"), text.rfind("]")))
        if start != -1 and end != -1:
            return text[start : end + 1]

        return text

    def _parse_json(self, raw: str) -> Any:
        try:
            cleaned = self._clean_json(raw)
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise AIServiceError(f"LLM 응답 JSON 파싱에 실패했습니다: {exc}\n응답 내용:\n{raw}")

    def _parse_json_object(self, raw: str, response_type: str) -> dict:
        parsed = self._parse_json(raw)
        if not isinstance(parsed, dict):
            raise AIServiceError(f"{response_type} 생성 결과가 JSON 객체가 아닙니다.")
        return parsed

    def _finalize_response(
        self,
        payload: dict,
        document_id: int,
        response_type: str,
        extra_fields: dict | None = None,
    ) -> dict:
        payload["documentId"] = document_id
        payload["type"] = response_type
        if extra_fields:
            payload.update(extra_fields)
        return payload

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

    def create_summary(self, chunks: List[dict], options: dict, document_id: int) -> dict:
        context = self._make_context(chunks)
        prompt = (
            "아래 텍스트를 바탕으로 요약 응답을 생성하세요."
            f"\n- 난이도: {options.get('difficulty', 'medium')}"
            f"\n- 언어: {options.get('language', 'ko')}"
            f"\n- documentId: {document_id}"
            "\n- 반드시 JSON 객체만 반환하고, 마크다운 코드블록이나 설명 문장을 붙이지 마세요."
            "\n- JSON 구조는 정확히 다음 형태를 따르세요:"
            "\n{"
            '\n  "documentId": number,'
            '\n  "type": "summary",'
            '\n  "generatedLanguage": "ko",'
            '\n  "summary": {'
            '\n    "coreSummary": ["핵심 요약 1", "핵심 요약 2", "핵심 요약 3"],'
            '\n    "sections": ['
            '\n      {"sectionId": 1, "title": "섹션 제목", "pageRange": "p.1-3", "content": "섹션 요약"}'
            "\n    ]"
            "\n  }"
            "\n}"
            "\n- coreSummary는 3개 이내로 작성하세요."
            "\n- sections는 문서 흐름에 따라 2~6개로 나누세요."
            "\n- 페이지는 텍스트의 [Page N] 표시를 근거로 추정하고, 불명확하면 가장 가까운 페이지를 사용하세요.\n\n"
            f"{context}"
        )
        raw = self._complete(prompt, max_tokens=1200)
        return self._finalize_response(
            self._parse_json_object(raw, "요약"),
            document_id,
            "summary",
            {"generatedLanguage": options.get("language", "ko")},
        )

    def create_quiz(self, chunks: List[dict], options: dict, document_id: int) -> dict:
        context = self._make_context(chunks)
        quiz_types = options.get("quizTypes", ["mcq", "ox"])
        count = options.get("countPerType", 3)
        prompt = (
            "다음 텍스트를 바탕으로 퀴즈를 생성하세요."
            f"\n- 유형: {', '.join(quiz_types)}"
            f"\n- 개수: {count}개씩"
            f"\n- 난이도: {options.get('difficulty', 'medium')}"
            f"\n- 언어: {options.get('language', 'ko')}"
            f"\n- documentId: {document_id}"
            "\n- 반드시 JSON 객체만 반환하고, 마크다운 코드블록이나 설명 문장을 붙이지 마세요."
            "\n- JSON 구조는 정확히 다음 형태를 따르세요:"
            "\n{"
            '\n  "documentId": number,'
            '\n  "type": "quiz",'
            '\n  "difficulty": "medium",'
            '\n  "quizzes": ['
            '\n    {'
            '\n      "quizId": 1,'
            '\n      "questionType": "multiple_choice",'
            '\n      "question": "문제",'
            '\n      "options": ["선택지 1", "선택지 2", "선택지 3", "선택지 4"],'
            '\n      "answer": 0,'
            '\n      "explanation": "정답 해설"'
            "\n    }"
            "\n  ]"
            "\n}"
            "\n- questionType은 multiple_choice, ox, blank 중 하나만 사용하세요."
            "\n- mcq 요청은 multiple_choice로 변환하세요."
            "\n- answer는 options 배열의 0 기반 정답 index입니다."
            "\n- ox 문제의 options는 [\"O\", \"X\"]로 작성하고 answer는 0 또는 1입니다."
            "\n- blank 문제도 options를 제공하고 answer를 정답 선택지 index로 작성하세요.\n\n"
            f"{context}"
        )
        raw = self._complete(prompt, max_tokens=1200)
        parsed = self._parse_json(raw)
        if isinstance(parsed, list):
            parsed = {"documentId": document_id, "type": "quiz", "quizzes": parsed}
        if not isinstance(parsed, dict):
            raise AIServiceError("퀴즈 생성 결과가 JSON 객체가 아닙니다.")
        return self._finalize_response(
            parsed,
            document_id,
            "quiz",
            {"difficulty": options.get("difficulty", "medium")},
        )

    def create_flashcards(self, chunks: List[dict], options: dict, document_id: int) -> dict:
        context = self._make_context(chunks)
        card_types = options.get("cardTypes", ["concept", "definition"])
        count = options.get("countPerType", 3)
        prompt = (
            "다음 텍스트를 바탕으로 플래시카드를 생성하세요."
            f"\n- 유형: {', '.join(card_types)}"
            f"\n- 개수: {count}개씩"
            f"\n- 난이도: {options.get('difficulty', 'medium')}"
            f"\n- 언어: {options.get('language', 'ko')}"
            f"\n- documentId: {document_id}"
            "\n- 반드시 JSON 객체만 반환하고, 마크다운 코드블록이나 설명 문장을 붙이지 마세요."
            "\n- JSON 구조는 정확히 다음 형태를 따르세요:"
            "\n{"
            '\n  "documentId": number,'
            '\n  "type": "flashcard",'
            '\n  "flashcards": ['
            '\n    {'
            '\n      "cardId": 1,'
            '\n      "front": "카드 앞면",'
            '\n      "back": "카드 뒷면",'
            '\n      "difficulty": "normal"'
            "\n    }"
            "\n  ]"
            "\n}"
            "\n- difficulty는 easy, normal, hard 중 하나만 사용하세요."
            "\n- 입력 난이도 medium은 normal로 변환하세요.\n\n"
            f"{context}"
        )
        raw = self._complete(prompt, max_tokens=1200)
        parsed = self._parse_json(raw)
        if isinstance(parsed, list):
            parsed = {"documentId": document_id, "type": "flashcard", "flashcards": parsed}
        if not isinstance(parsed, dict):
            raise AIServiceError("플래시카드 생성 결과가 JSON 객체가 아닙니다.")
        return self._finalize_response(parsed, document_id, "flashcard")

    def create_chat(self, chunks: List[dict], options: dict, question: str, document_id: int) -> dict:
        context = self._make_context(chunks)
        prompt = (
            "다음 텍스트를 근거로 사용자 질문에 답하세요."
            f"\n- 질문: {question}"
            f"\n- 언어: {options.get('language', 'ko')}"
            f"\n- documentId: {document_id}"
            "\n- 반드시 JSON 객체만 반환하고, 마크다운 코드블록이나 설명 문장을 붙이지 마세요."
            "\n- JSON 구조는 정확히 다음 형태를 따르세요:"
            "\n{"
            '\n  "documentId": number,'
            '\n  "type": "chat",'
            '\n  "answer": "AI 답변",'
            '\n  "references": ['
            '\n    {"page": 1, "text": "문서 근거 텍스트"}'
            "\n  ]"
            "\n}"
            "\n- references는 텍스트의 [Page N] 표시를 근거로 1~3개만 작성하세요."
            "\n- 문서에서 근거를 찾을 수 없으면 answer에 모른다고 답하고 references는 빈 배열로 반환하세요.\n\n"
            f"{context}"
        )
        raw = self._complete(prompt, max_tokens=1000)
        return self._finalize_response(self._parse_json_object(raw, "챗봇"), document_id, "chat")
