# app/api/routes_flashcard.py

from __future__ import annotations

from datetime import datetime
from uuid import uuid4, UUID

from fastapi import APIRouter, HTTPException, status

from app.schemas.flashcard_schema import (
    FlashcardRequest,
    FlashcardBatchRequest,
    FlashcardResponse,
    FlashcardContent,
    Flashcard,
    CardType,
    DifficultyLevel
)
from app.schemas.common_schema import Metadata
from app.services.flashcard_service import FlashcardService

router = APIRouter()


@router.post(
    "/flashcards/generate",
    response_model=FlashcardResponse,
    status_code=status.HTTP_200_OK
)
async def generate_flashcards(
    request: FlashcardRequest,
    document_id: str = None
) -> FlashcardResponse:
    """
    청크 목록으로부터 플래시카드를 생성합니다.
    
    지원 카드 유형:
    - concept: 개념 설명
    - definition: 정의
    - example: 예시
    - q_and_a: 질문-답변
    
    Args:
        request: 청크 목록, 카드 유형, 난이도 등
        document_id: 문서 ID (UUID 문자열)
    
    Returns:
        생성된 플래시카드 세트
    """
    try:
        if not document_id:
            document_id = str(uuid4())
        
        flashcard_service = FlashcardService()
        start_time = datetime.utcnow()
        
        # 플래시카드 생성
        card_data_list = flashcard_service.generate_flashcards(
            chunks=request.chunks,
            card_types=request.card_types,
            count_per_type=request.count_per_type,
            difficulty=request.difficulty
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # 메타데이터
        metadata = Metadata(
            processing_time=processing_time,
            model_name="gpt-4",
            language="ko",
            chunks_used=len(request.chunks)
        )
        
        # 카테고리별 통계
        categories = {}
        for card in card_data_list:
            for tag in card.get("tags", []):
                categories[tag] = categories.get(tag, 0) + 1
        
        # FlashcardContent 생성
        flashcard_set = FlashcardContent(
            flashcard_id=uuid4(),
            cards=[Flashcard(**card) for card in card_data_list],
            total_cards=len(card_data_list),
            categories=categories
        )
        
        return FlashcardResponse(
            document_id=UUID(document_id),
            metadata=metadata,
            flashcard_set=flashcard_set
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/flashcards/batch",
    response_model=list[FlashcardResponse],
    status_code=status.HTTP_200_OK
)
async def generate_flashcards_batch(
    request: FlashcardBatchRequest,
    document_id: str = None
) -> list[FlashcardResponse]:
    """
    여러 청크에 대해 플래시카드를 배치 생성합니다.
    
    Args:
        request: 청크 목록, 덱 이름, 카드 유형 등
        document_id: 문서 ID (UUID 문자열)
    
    Returns:
        생성된 플래시카드 응답 목록
    """
    try:
        if not document_id:
            document_id = str(uuid4())
        
        # 배치 생성은 하나의 응답으로 통합
        base_request = FlashcardRequest(
            chunks=request.chunks,
            card_types=request.card_types,
            count=request.count,
            difficulty=None if request.include_difficulty_mix else None
        )
        
        response = await generate_flashcards(base_request, document_id)
        return [response]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
