from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.schemas.process_schema import ProcessRequest, ProcessResponse
from app.services.process_service import process_document
from app.services.pdf_downloader import PDFDownloadError

router = APIRouter()


@router.post(
    "/process",
    response_model=ProcessResponse,
    status_code=status.HTTP_200_OK,
)
async def process_document_route(request: ProcessRequest) -> ProcessResponse:
    try:
        return process_document(request)
    except PDFDownloadError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 처리 중 오류가 발생했습니다: {exc}",
        )
