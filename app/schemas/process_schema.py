from __future__ import annotations

import re
from typing import List, Optional

from pydantic import BaseModel, Field, FieldValidationInfo, HttpUrl, field_validator


class ProcessOptions(BaseModel):
    generate: List[str] = Field(
        ...,
        description="요약(summary), 퀴즈(quiz), 플래시카드(flashcard) 중 하나 이상",
    )
    quizTypes: List[str] = Field(
        default_factory=list,
        description="생성할 퀴즈 유형, 예: ['mcq', 'ox']",
    )
    cardTypes: List[str] = Field(
        default_factory=list,
        description="생성할 플래시카드 유형, 예: ['concept', 'definition']",
    )
    countPerType: int = Field(
        default=3,
        ge=1,
        le=20,
        description="각 유형마다 생성할 개수",
    )
    difficulty: str = Field(default="medium", description="난이도: easy, medium, hard")
    language: str = Field(default="ko", description="결과 언어")

    @field_validator("generate", mode="before")
    def validate_generate_item(cls, value: list[str]) -> list[str]:
        allowed = {"summary", "quiz", "flashcard"}
        if not isinstance(value, list):
            raise ValueError("generate 필드는 문자열 목록이어야 합니다.")

        for item in value:
            if item not in allowed:
                raise ValueError("generate 값은 summary, quiz, flashcard 중 하나여야 합니다.")
        return value


class ProcessRequest(BaseModel):
    documentId: int = Field(..., description="Spring 서버에서 전달되는 문서 ID")
    fileUrl: HttpUrl = Field(..., description="Cloudinary에 저장된 PDF 파일 URL")
    options: ProcessOptions = Field(...)


class QuizItem(BaseModel):
    question: str
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: Optional[str] = None


class FlashcardItem(BaseModel):
    front: str
    back: str
    type: Optional[str] = None


class ProcessResponse(BaseModel):
    document_id: int
    file_url: HttpUrl
    page_count: int
    chunk_count: int
    summary: Optional[str] = None
    quizzes: Optional[List[QuizItem]] = None
    flashcards: Optional[List[FlashcardItem]] = None
    generated_language: str
    difficulty: str
    note: str = Field(default="AI 서버가 처리한 결과입니다.")

    class Config:
        schema_extra = {
            "example": {
                "document_id": 1,
                "file_url": "https://res.cloudinary.com/.../lecture.pdf",
                "page_count": 12,
                "chunk_count": 8,
                "summary": "...",
                "quizzes": [
                    {
                        "question": "다음 중 ...?",
                        "options": ["A", "B", "C", "D"],
                        "correct_answer": "A",
                        "explanation": "정답 해설"
                    }
                ],
                "flashcards": [
                    {
                        "front": "개념 설명",
                        "back": "정의 내용",
                        "type": "concept"
                    }
                ],
                "generated_language": "ko",
                "difficulty": "medium",
            }
        }

    @field_validator("generated_language", mode="before")
    def normalize_language(cls, value: str) -> str:
        return value.lower() if value else "ko"
