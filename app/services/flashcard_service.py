# app/services/flashcard_service.py

from __future__ import annotations

import importlib
import json
import os
from typing import List, Dict, Any

load_dotenv = None
if importlib.util.find_spec("dotenv") is not None:
    dotenv = importlib.import_module("dotenv")
    load_dotenv = getattr(dotenv, "load_dotenv", None)

if load_dotenv is not None:
    load_dotenv()

from openai import OpenAI

from app.schemas.flashcard_schema import (
    CardType,
    DifficultyLevel,
    Flashcard
)


class FlashcardService:
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        self.client = OpenAI(api_key=api_key)

    def generate_flashcards(
        self,
        chunks: List[str],
        card_types: List[CardType],
        count_per_type: int = 5,
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    ) -> List[Dict[str, Any]]:
        """
        청크 목록을 입력받아 지정된 유형의 플래시카드를 생성합니다.
        """
        if not chunks:
            return []

        # 청크들을 하나의 텍스트로 결합
        combined_text = "\n\n".join(chunks)

        flashcards = []

        for card_type in card_types:
            for _ in range(count_per_type):
                card = self._generate_single_flashcard(combined_text, card_type, difficulty)
                if card:
                    flashcards.append(card)

        return flashcards

    def _generate_single_flashcard(
        self,
        text: str,
        card_type: CardType,
        difficulty: DifficultyLevel
    ) -> Dict[str, Any]:
        """
        단일 플래시카드를 생성합니다.
        """
        prompts = {
            CardType.CONCEPT: self._get_concept_prompt(text, difficulty),
            CardType.DEFINITION: self._get_definition_prompt(text, difficulty),
            CardType.EXAMPLE: self._get_example_prompt(text, difficulty),
            CardType.Q_AND_A: self._get_q_and_a_prompt(text, difficulty),
        }

        prompt = prompts.get(card_type)
        if not prompt:
            return None

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "당신은 전문적인 플래시카드 생성자입니다. JSON 형식으로만 응답하세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )

            result = response.choices[0].message.content.strip()

            # JSON 파싱
            card_data = json.loads(result)

            # 스키마에 맞게 변환
            return Flashcard(**card_data).dict()

        except Exception as e:
            print(f"플래시카드 생성 중 오류: {e}")
            return None

    def _get_concept_prompt(self, text: str, difficulty: DifficultyLevel) -> str:
        return f"""
다음 텍스트를 기반으로 개념 설명 플래시카드를 하나 생성하세요.

난이도: {difficulty.value}

텍스트:
{text}

응답 형식 (JSON):
{{
    "front": "개념 이름이나 질문",
    "back": "개념 설명",
    "card_type": "concept",
    "tags": ["태그1", "태그2"],
    "difficulty": "{difficulty.value}",
    "hint": "힌트 (선택사항)",
    "related_page": 1,
    "related_section": "섹션명"
}}
"""

    def _get_definition_prompt(self, text: str, difficulty: DifficultyLevel) -> str:
        return f"""
다음 텍스트를 기반으로 정의 플래시카드를 하나 생성하세요.

난이도: {difficulty.value}

텍스트:
{text}

응답 형식 (JSON):
{{
    "front": "용어",
    "back": "정의",
    "card_type": "definition",
    "tags": ["태그1", "태그2"],
    "difficulty": "{difficulty.value}",
    "hint": "힌트 (선택사항)",
    "related_page": 1,
    "related_section": "섹션명"
}}
"""

    def _get_example_prompt(self, text: str, difficulty: DifficultyLevel) -> str:
        return f"""
다음 텍스트를 기반으로 예시 플래시카드를 하나 생성하세요.

난이도: {difficulty.value}

텍스트:
{text}

응답 형식 (JSON):
{{
    "front": "예시 설명이나 질문",
    "back": "예시 내용",
    "card_type": "example",
    "tags": ["태그1", "태그2"],
    "difficulty": "{difficulty.value}",
    "hint": "힌트 (선택사항)",
    "related_page": 1,
    "related_section": "섹션명"
}}
"""

    def _get_q_and_a_prompt(self, text: str, difficulty: DifficultyLevel) -> str:
        return f"""
다음 텍스트를 기반으로 질문-답변 플래시카드를 하나 생성하세요.

난이도: {difficulty.value}

텍스트:
{text}

응답 형식 (JSON):
{{
    "front": "질문",
    "back": "답변",
    "card_type": "q_and_a",
    "tags": ["태그1", "태그2"],
    "difficulty": "{difficulty.value}",
    "hint": "힌트 (선택사항)",
    "related_page": 1,
    "related_section": "섹션명"
}}
"""