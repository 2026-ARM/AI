# app/api/routes_document.py

from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.schemas.document_schema import DocumentExtractResponse
from app.services.pdf_extractor import PDFExtractionError, extract_text_from_pdf

router = APIRouter()

UPLOAD_DIR = Path("data/raw")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post(
    "/extract",
    response_model=DocumentExtractResponse,
    status_code=status.HTTP_200_OK
)
async def extract_document(file: UploadFile = File(...)):
    # 1. 파일명 검증
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="업로드된 파일 이름이 없습니다."
        )

    # 2. PDF 확장자 검증
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PDF 파일만 업로드할 수 있습니다."
        )

    file_path = UPLOAD_DIR / file.filename

    # 3. 파일 저장
    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="빈 파일은 업로드할 수 없습니다."
            )

        with open(file_path, "wb") as f:
            f.write(contents)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 저장 중 오류가 발생했습니다: {e}"
        )

    # 4. PDF 텍스트 추출
    try:
        result = extract_text_from_pdf(str(file_path))
        return {
            "filename": file.filename,
            "page_count": result["page_count"],
            "pages": result["pages"],
            "full_text": result["full_text"]
        }

    except PDFExtractionError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"알 수 없는 오류가 발생했습니다: {e}"
        )