# app/schemas/summary_schema.py

from __future__ import annotations

from typing import List

from pydantic import BaseModel


class SummaryRequest(BaseModel):
    chunks: List[str]


class SummaryResponse(BaseModel):
    summary: str