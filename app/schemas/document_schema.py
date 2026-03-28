# app/schemas/document_schema.py

from typing import List

from pydantic import BaseModel


class PageText(BaseModel):
    page_number: int
    text: str


class ChunkItem(BaseModel):
    chunk_index: int
    text: str
    length: int


class DocumentExtractResponse(BaseModel):
    filename: str
    page_count: int
    pages: List[PageText]
    full_text: str
    cleaned_text: str
    chunks: List[ChunkItem]
