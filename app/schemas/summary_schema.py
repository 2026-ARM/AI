# app/schemas/summary_schema.py

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common_schema import BaseResponse, Metadata


class SummaryRequest(BaseModel):
    chunks: List[str] = Field(..., description="처리할 텍스트 청크 목록")


class SummaryContent(BaseModel):
    """요약 내용"""
    text: str = Field(..., description="요약 텍스트")
    key_points: List[str] = Field(..., description="주요 포인트 (최대 5개)")
    original_length: int = Field(..., description="원본 문자 수")
    summary_length: int = Field(..., description="요약 문자 수")
    compression_ratio: float = Field(..., description="압축률 (%)")


class SummaryResponse(BaseResponse):
    """요약 API 응답"""
    summary: SummaryContent = Field(..., description="요약 내용")

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "550e8400-e29b-41d4-a716-446655440000",
                "created_at": "2024-03-28T12:00:00Z",
                "metadata": {
                    "processing_time": 2.5,
                    "model_name": "gpt-4",
                    "language": "ko",
                    "chunks_used": 10
                },
                "summary": {
                    "text": "이 문서는...",
                    "key_points": ["포인트 1", "포인트 2"],
                    "original_length": 5000,
                    "summary_length": 500,
                    "compression_ratio": 90
                },
                "extra": {}
            }
        }