# app/services/quiz_service.py

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

from app.schemas.quiz_schema import (
    QuizType,
    DifficultyLevel,
    MCQQuiz,
    CodeErrorQuiz,
    CodeFillBlankQuiz,
    OXQuiz
)


class QuizService:
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        self.client = OpenAI(api_key=api_key)

    def generate_quizzes(
        self,
        chunks: List[str],
        quiz_types: List[QuizType],
        count_per_type: int = 3,
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    ) -> List[Dict[str, Any]]:
        """
        청크 목록을 입력받아 지정된 유형의 퀴즈를 생성합니다.
        """
        if not chunks:
            return []

        # 청크들을 하나의 텍스트로 결합
        combined_text = "\n\n".join(chunks)

        quizzes = []

        for quiz_type in quiz_types:
            for _ in range(count_per_type):
                quiz = self._generate_single_quiz(combined_text, quiz_type, difficulty)
                if quiz:
                    quizzes.append(quiz)

        return quizzes

    def _generate_single_quiz(
        self,
        text: str,
        quiz_type: QuizType,
        difficulty: DifficultyLevel
    ) -> Dict[str, Any]:
        """
        단일 퀴즈를 생성합니다.
        """
        prompts = {
            QuizType.MCQ: self._get_mcq_prompt(text, difficulty),
            QuizType.CODE_ERROR: self._get_code_error_prompt(text, difficulty),
            QuizType.CODE_FILL_BLANK: self._get_code_fill_blank_prompt(text, difficulty),
            QuizType.OX: self._get_ox_prompt(text, difficulty),
        }

        prompt = prompts.get(quiz_type)
        if not prompt:
            return None

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "당신은 전문적인 퀴즈 생성자입니다. JSON 형식으로만 응답하세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )

            result = response.choices[0].message.content.strip()

            # JSON 파싱
            quiz_data = json.loads(result)

            # 스키마에 맞게 변환
            if quiz_type == QuizType.MCQ:
                return MCQQuiz(**quiz_data).dict()
            elif quiz_type == QuizType.CODE_ERROR:
                return CodeErrorQuiz(**quiz_data).dict()
            elif quiz_type == QuizType.CODE_FILL_BLANK:
                return CodeFillBlankQuiz(**quiz_data).dict()
            elif quiz_type == QuizType.OX:
                return OXQuiz(**quiz_data).dict()

        except Exception as e:
            print(f"퀴즈 생성 중 오류: {e}")
            return None

    def _get_mcq_prompt(self, text: str, difficulty: DifficultyLevel) -> str:
        return f"""
다음 텍스트를 기반으로 객관식 퀴즈를 하나 생성하세요.

난이도: {difficulty.value}

텍스트:
{text}

응답 형식 (JSON):
{{
    "question": "질문 내용",
    "options": ["선택지1", "선택지2", "선택지3", "선택지4"],
    "correct_option_index": 0,
    "explanation": "정답 설명"
}}
"""

    def _get_code_error_prompt(self, text: str, difficulty: DifficultyLevel) -> str:
        return f"""
다음 텍스트를 기반으로 코드 오류 찾기 퀴즈를 하나 생성하세요.

난이도: {difficulty.value}

텍스트:
{text}

응답 형식 (JSON):
{{
    "question": "문제 설명",
    "code": "코드 내용",
    "error_description": "오류 설명",
    "error_line_number": 5,
    "hint": "힌트",
    "explanation": "해설"
}}
"""

    def _get_code_fill_blank_prompt(self, text: str, difficulty: DifficultyLevel) -> str:
        return f"""
다음 텍스트를 기반으로 코드 빈칸 채우기 퀴즈를 하나 생성하세요.

난이도: {difficulty.value}

텍스트:
{text}

응답 형식 (JSON):
{{
    "question": "문제 설명",
    "code_with_blanks": "빈칸이 있는 코드 (___로 표시)",
    "solutions": ["답1", "답2"],
    "language": "python",
    "hint": "힌트",
    "explanation": "해설"
}}
"""

    def _get_ox_prompt(self, text: str, difficulty: DifficultyLevel) -> str:
        return f"""
다음 텍스트를 기반으로 O/X 퀴즈를 하나 생성하세요.

난이도: {difficulty.value}

텍스트:
{text}

응답 형식 (JSON):
{{
    "statement": "참/거짓 명제",
    "is_correct": true,
    "explanation": "설명"
}}
"""