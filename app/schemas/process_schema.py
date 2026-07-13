from __future__ import annotations

from typing import Literal, List, Union

from pydantic import BaseModel, Field, HttpUrl, field_validator


class ProcessOptions(BaseModel):
    generate: Literal["summary", "quiz", "flashcard"] = Field(
        ...,
        description="생성할 기능: summary, quiz, flashcard 중 하나",
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
    def validate_generate_item(cls, value: str | list[str]) -> str:
        allowed = {"summary", "quiz", "flashcard"}
        if isinstance(value, list):
            if len(value) != 1:
                raise ValueError("generate 값은 한 번에 하나만 요청할 수 있습니다.")
            value = value[0]

        if value not in allowed:
            raise ValueError("generate 값은 summary, quiz, flashcard 중 하나여야 합니다.")
        return value


class ProcessRequest(BaseModel):
    documentId: int = Field(..., description="Spring 서버에서 전달되는 문서 ID")
    fileUrl: HttpUrl = Field(..., description="Cloudinary에 저장된 PDF 파일 URL")
    options: ProcessOptions = Field(...)


class SummarySection(BaseModel):
    sectionId: int
    title: str
    pageRange: str
    content: str


class SummaryContent(BaseModel):
    coreSummary: List[str]
    sections: List[SummarySection]


class SummaryAIResponse(BaseModel):
    documentId: int
    type: Literal["summary"]
    generatedLanguage: str
    summary: SummaryContent

    @field_validator("generatedLanguage", mode="before")
    def normalize_language(cls, value: str) -> str:
        return value.lower() if value else "ko"


class QuizItem(BaseModel):
    quizId: int
    questionType: Literal["multiple_choice", "ox", "blank"]
    question: str
    options: List[str]
    answer: int
    explanation: str


class QuizAIResponse(BaseModel):
    documentId: int
    type: Literal["quiz"]
    difficulty: str
    quizzes: List[QuizItem]


class FlashcardItem(BaseModel):
    cardId: int
    front: str
    back: str
    difficulty: Literal["easy", "normal", "hard"]


class FlashcardAIResponse(BaseModel):
    documentId: int
    type: Literal["flashcard"]
    flashcards: List[FlashcardItem]


class ChatReference(BaseModel):
    page: int
    text: str


class ChatAIResponse(BaseModel):
    documentId: int
    type: Literal["chat"]
    answer: str
    references: List[ChatReference]


ProcessResponse = Union[SummaryAIResponse, QuizAIResponse, FlashcardAIResponse]
