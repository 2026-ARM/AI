from __future__ import annotations

import tempfile
from pathlib import Path

import requests
from requests.exceptions import RequestException


class PDFDownloadError(Exception):
    pass


def download_pdf(file_url: str) -> str:
    """fileUrl로 PDF를 다운로드하고 임시 파일 경로를 반환합니다."""
    try:
        response = requests.get(file_url, stream=True, timeout=30)
        response.raise_for_status()
    except RequestException as exc:
        raise PDFDownloadError(f"PDF 다운로드에 실패했습니다: {exc}")

    content_type = response.headers.get("Content-Type", "")
    if "pdf" not in content_type.lower() and not file_url.lower().endswith(".pdf"):
        raise PDFDownloadError(
            "다운로드한 파일이 PDF가 아닙니다. URL 또는 HTTP 응답 헤더를 확인하세요."
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                temp_file.write(chunk)
        return temp_file.name
