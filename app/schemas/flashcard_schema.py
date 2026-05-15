# app/schemas/flashcard_schema.py

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common_schema import BaseResponse, Metadata


class CardType(str, Enum):
    """카드 유형"""
    CONCEPT = "concept"  # 개념 설명
    DEFINITION = "definition"  # 정의
    EXAMPLE = "example"  # 예시
    Q_AND_A = "q_and_a"  # 질문-답변


class DifficultyLevel(str, Enum):
    """난이도"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Flashcard(BaseModel):
    """플래시카드"""
    front: str = Field(..., description="앞면 (질문/단어)")
    back: str = Field(..., description="뒷면 (답변/정의)")
    card_type: CardType = Field(default=CardType.CONCEPT, description="카드 유형")
    tags: List[str] = Field(default_factory=list, description="태그")
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM, description="난이도")
    hint: Optional[str] = Field(default=None, description="힌트")
    related_page: Optional[int] = Field(default=None, description="관련 페이지")
    related_section: Optional[str] = Field(default=None, description="관련 섹션")


class FlashcardContent(BaseModel):
    """플래시카드 컬렉션"""
    flashcard_id: UUID = Field(default_factory=lambda: UUID('00000000-0000-0000-0000-000000000000'), description="플래시카드 세트 ID")
    cards: List[Flashcard] = Field(..., description="플래시카드 목록")
    total_cards: int = Field(..., description="전체 카드 수")
    categories: Dict[str, int] = Field(default_factory=dict, description="카테고리별 카드 수")


class FlashcardResponse(BaseResponse):
    """플래시카드 API 응답"""
    flashcard_set: FlashcardContent = Field(..., description="플래시카드 세트")

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "550e8400-e29b-41d4-a716-446655440000",
                "created_at": "2024-03-28T12:00:00Z",
                "metadata": {
                    "processing_time": 2.8,
                    "model_name": "gpt-4",
                    "language": "ko",
                    "chunks_used": 12
                },
                "flashcard_set": {
                    "flashcard_id": "550e8400-e29b-41d4-a716-446655440002",
                    "cards": [
                        {
                            "front": "Python의 리스트란?",
                            "back": "순서가 있는 변경 가능한 컬렉션",
                            "card_type": "definition",
                            "tags": ["python", "자료구조"],
                            "difficulty": "easy",
                            "hint": "배열과 비슷합니다",
                            "related_page": 15,
                            "related_section": "자료구조"
                        }
                    ],
                    "total_cards": 1,
                    "categories": {"자료구조": 1}
                },
                "extra": {}
            }
        }


# ============ 요청 모델 ============

class FlashcardRequest(BaseModel):
    """플래시카드 생성 요청"""
    chunks: List[str] = Field(..., description="처리할 텍스트 청크")
    card_types: List[CardType] = Field(
        default=[CardType.CONCEPT, CardType.DEFINITION],
        description="생성할 카드 유형"
    )
    count: int = Field(default=20, ge=5, le=100, description="생성할 카드 수")
    difficulty: Optional[DifficultyLevel] = Field(
        default=None,
        description="난이도 (지정 시 고정, None이면 혼합)"
    )


class FlashcardRequest(BaseModel):
    """플래시카드 생성 요청"""
    chunks: List[str] = Field(..., description="처리할 텍스트 청크")
    card_types: List[CardType] = Field(
        default=[CardType.CONCEPT],
        description="생성할 카드 유형"
    )
    count_per_type: int = Field(default=5, ge=1, le=50, description="유형별 생성 개수")
    difficulty: Optional[DifficultyLevel] = Field(
        default=None,
        description="난이도 (지정 시 고정, None이면 혼합)"
    )


class FlashcardBatchRequest(BaseModel):
    """배치 플래시카드 생성 요청"""
    chunks: List[str] = Field(..., description="처리할 텍스트 청크")
    deck_name: str = Field(..., description="덱 이름")
    card_types: List[CardType] = Field(
        default=[CardType.CONCEPT, CardType.DEFINITION, CardType.EXAMPLE],
        description="생성할 카드 유형"
    )
    count_per_type: int = Field(default=5, ge=1, le=50, description="유형별 생성 개수")
    difficulty: Optional[DifficultyLevel] = Field(
        default=None,
        description="난이도 (지정 시 고정, None이면 혼합)"
    )
