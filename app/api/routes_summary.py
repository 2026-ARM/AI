# app/api/routes_summary.py

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status

from app.schemas.summary_schema import SummaryRequest, SummaryResponse, SummaryContent
from app.schemas.common_schema import Metadata
from app.services.summary_service import SummaryService

router = APIRouter()


@router.post(
    "/summarize",
    response_model=SummaryResponse,
    status_code=status.HTTP_200_OK
)
async def summarize_document(request: SummaryRequest, document_id: str = None):
    """
    청크 목록을 입력받아 GPT 기반 요약을 생성합니다.
    
    Args:
        request: 청크 목록
        document_id: 문서 ID (UUID 문자열)
    
    Returns:
        요약 결과 (metadata 포함)
    """
    try:
        if not document_id:
            document_id = str(uuid4())
        
        summary_service = SummaryService()
        start_time = datetime.utcnow()
        
        # 요약 생성
        summary_text = summary_service.summarize_chunks(request.chunks)
        
        # 주요 포인트 추출 (간단한 구현)
        key_points = extract_key_points(summary_text)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # 메타데이터 생성
        metadata = Metadata(
            processing_time=processing_time,
            model_name="gpt-4",
            language="ko",
            chunks_used=len(request.chunks)
        )
        
        # 요약 컨텐츠
        original_text = "".join(request.chunks)
        summary_content = SummaryContent(
            text=summary_text,
            key_points=key_points,
            original_length=len(original_text),
            summary_length=len(summary_text),
            compression_ratio=round((len(summary_text) / len(original_text) * 100), 2) if original_text else 0
        )
        
        return SummaryResponse(
            document_id=UUID(document_id),
            metadata=metadata,
            summary=summary_content
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


def extract_key_points(text: str, max_points: int = 5) -> list[str]:
    """
    요약 텍스트에서 주요 포인트를 추출합니다.
    
    현재는 간단한 구현입니다.
    추후 NLP 기반 추출로 개선 예정.
    
    Args:
        text: 요약 텍스트
        max_points: 최대 포인트 수
    
    Returns:
        주요 포인트 목록
    """
    # 마침표로 구분된 문장들을 포인트로 변환
    sentences = [s.strip() for s in text.split("。") if s.strip()]
    sentences = sentences[:max_points]
    return sentences if sentences else [text[:100]]