# app/api/routes_summary.py

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.schemas.summary_schema import SummaryRequest, SummaryResponse
from app.services.summary_service import SummaryService

router = APIRouter()

# summary_service = SummaryService()  # Lazy initialization


@router.post(
    "/summarize",
    response_model=SummaryResponse,
    status_code=status.HTTP_200_OK
)
async def summarize_document(request: SummaryRequest):
    """
    청크 목록을 입력받아 GPT 기반 요약을 생성합니다.
    """
    try:
        summary_service = SummaryService()  # Initialize here
        summary = summary_service.summarize_chunks(request.chunks)
        return SummaryResponse(summary=summary)
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