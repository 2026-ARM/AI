# app/schemas/quiz_schema.py

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common_schema import BaseResponse, Metadata


class QuizType(str, Enum):
    """퀴즈 유형"""
    MCQ = "mcq"  # Multiple Choice Question
    CODE_ERROR = "code_error"  # 코드 오류 찾기
    CODE_FILL_BLANK = "code_fill_blank"  # 코드 빈칸 채우기
    OX = "ox"  # O/X 퀴즈


class DifficultyLevel(str, Enum):
    """난이도"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


# ============ 개별 퀴즈 유형 ============

class MCQQuiz(BaseModel):
    """객관식 퀴즈"""
    quiz_type: str = Field(default=QuizType.MCQ, description="퀴즈 유형")
    question: str = Field(..., description="질문")
    options: List[str] = Field(..., min_items=2, max_items=5, description="선택지 (2-5개)")
    correct_option_index: int = Field(..., ge=0, description="정답 선택지 인덱스")
    explanation: Optional[str] = Field(default=None, description="해설")


class CodeErrorQuiz(BaseModel):
    """코드 오류 찾기 퀴즈"""
    quiz_type: str = Field(default=QuizType.CODE_ERROR, description="퀴즈 유형")
    question: str = Field(..., description="질문/문제 설명")
    code: str = Field(..., description="코드")
    error_description: str = Field(..., description="오류 설명")
    error_line_number: Optional[int] = Field(default=None, description="오류 줄 번호")
    hint: Optional[str] = Field(default=None, description="힌트")
    explanation: Optional[str] = Field(default=None, description="해설")


class CodeFillBlankQuiz(BaseModel):
    """코드 빈칸 채우기 퀴즈"""
    quiz_type: str = Field(default=QuizType.CODE_FILL_BLANK, description="퀴즈 유형")
    question: str = Field(..., description="질문/문제 설명")
    code_with_blanks: str = Field(..., description="빈칸이 있는 코드 (___로 표시)")
    solutions: List[str] = Field(..., description="정답 (복수 가능)")
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM, description="난이도")
    language: str = Field(default="python", description="프로그래밍 언어")
    hint: Optional[str] = Field(default=None, description="힌트")
    explanation: Optional[str] = Field(default=None, description="해설")


class OXQuiz(BaseModel):
    """O/X 퀴즈"""
    quiz_type: str = Field(default=QuizType.OX, description="퀴즈 유형")
    statement: str = Field(..., description="참/거짓 명제")
    is_correct: bool = Field(..., description="정답 (True=O, False=X)")
    explanation: Optional[str] = Field(default=None, description="해설")


# ============ 통합 퀴즈 타입 ============

UnionQuizType = Union[MCQQuiz, CodeErrorQuiz, CodeFillBlankQuiz, OXQuiz]


class QuizContent(BaseModel):
    """퀴즈 콘텐츠"""
    quiz_id: UUID = Field(default_factory=lambda: UUID('00000000-0000-0000-0000-000000000000'), description="퀴즈 ID")
    quiz_data: UnionQuizType = Field(..., description="퀴즈 데이터 (유형별)")
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM, description="난이도")
    estimated_time: int = Field(default=60, description="예상 풀이 시간 (초)")


class QuizResponse(BaseResponse):
    """퀴즈 API 응답"""
    quizzes: List[QuizContent] = Field(..., description="생성된 퀴즈 목록")
    total_count: int = Field(..., description="전체 퀴즈 수")

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "550e8400-e29b-41d4-a716-446655440000",
                "created_at": "2024-03-28T12:00:00Z",
                "metadata": {
                    "processing_time": 3.2,
                    "model_name": "gpt-4",
                    "language": "ko",
                    "chunks_used": 15
                },
                "quizzes": [
                    {
                        "quiz_id": "550e8400-e29b-41d4-a716-446655440001",
                        "quiz_data": {
                            "quiz_type": "mcq",
                            "question": "다음 중 정답은?",
                            "options": ["옵션 1", "옵션 2", "옵션 3"],
                            "correct_option_index": 1,
                            "explanation": "정답은..."
                        },
                        "difficulty": "medium",
                        "estimated_time": 60
                    }
                ],
                "total_count": 1,
                "extra": {}
            }
        }


# ============ 배치 요청 ============

class QuizBatchRequest(BaseModel):
    """배치 퀴즈 생성 요청"""
    chunks: List[str] = Field(..., description="처리할 텍스트 청크")
    quiz_types: List[QuizType] = Field(
        default=[QuizType.MCQ, QuizType.OX],
        description="생성할 퀴즈 유형"
    )
    count_per_type: int = Field(default=3, ge=1, le=20, description="유형별 생성 개수")
    difficulty: Optional[DifficultyLevel] = Field(
        default=None,
        description="난이도 (지정 시 고정, None이면 혼합)"
    )
