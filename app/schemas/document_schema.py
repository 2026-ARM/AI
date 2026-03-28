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