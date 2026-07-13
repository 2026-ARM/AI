# app/services/pdf_extractor.py

from __future__ import annotations

import fitz  # PyMuPDF


class PDFExtractionError(Exception):
    """PDF 텍스트 추출 중 발생하는 사용자 정의 예외"""
    pass


def extract_text_from_pdf(pdf_path: str) -> dict:
    """
    PDF 파일에서 페이지별 텍스트를 추출하고,
    전체 텍스트를 하나로 합쳐 반환합니다.

    Returns:
        {
            "page_count": int,
            "pages": [
                {"page_number": 1, "text": "..."},
                ...
            ],
            "full_text": "..."
        }
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise PDFExtractionError(f"PDF 파일을 열 수 없습니다: {e}")

    try:
        pages = []
        full_text_parts = []

        for i, page in enumerate(doc):
            text = page.get_text("text") or ""
            text = text.strip()

            pages.append({
                "page_number": i + 1,
                "text": text
            })

            if text:
                full_text_parts.append(f"[Page {i + 1}]\n{text}")

        full_text = "\n\n".join(full_text_parts)

        return {
            "page_count": len(doc),
            "pages": pages,
            "full_text": full_text
        }

    except Exception as e:
        raise PDFExtractionError(f"PDF 텍스트 추출 중 오류가 발생했습니다: {e}")

    finally:
        doc.close()