# app/schemas/common_schema.py

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class Metadata(BaseModel):
    """AI 처리 결과 메타데이터"""
    processing_time: float = Field(..., description="처리 시간 (초)")
    model_name: Optional[str] = Field(default=None, description="사용된 AI 모델명")
    language: Optional[str] = Field(default="ko", description="문서 언어")
    chunks_used: Optional[int] = Field(default=None, description="처리에 사용된 청크 수")


class BaseResponse(BaseModel):
    """모든 AI 응답의 기본 구조"""
    document_id: UUID = Field(..., description="문서 ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성 시간")
    metadata: Metadata = Field(..., description="처리 메타데이터")
    extra: Dict[str, Any] = Field(default_factory=dict, description="추가 정보")

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
                "extra": {}
            }
        }
