# app/schemas/document_schema.py

from pydantic import BaseModel
from typing import List


class PageText(BaseModel):
    page_number: int
    text: str


class DocumentExtractResponse(BaseModel):
    filename: str
    page_count: int
    pages: List[PageText]
    full_text: str


# 기존 DocumentExtractResponse에 cleaned_text를 추가합니다.
class PageText(BaseModel):
    page_number: int
    text: str


class DocumentExtractResponse(BaseModel):
    filename: str
    page_count: int
    pages: List[PageText]
    full_text: str
    cleaned_text: str