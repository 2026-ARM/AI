from __future__ import annotations

from app.schemas.process_schema import ProcessRequest, ProcessResponse
from app.services.ai_service import LLMService
from app.services.pdf_downloader import download_pdf
from app.services.pdf_extractor import PDFExtractionError, extract_text_from_pdf
from app.services.preprocess_service import clean_text
from app.services.chunk_service import chunk_text


def process_document(request: ProcessRequest) -> ProcessResponse:
    pdf_path = download_pdf(request.fileUrl)

    extraction = extract_text_from_pdf(pdf_path)
    cleaned_text = clean_text(extraction["full_text"])
    chunks = chunk_text(cleaned_text, max_length=1500, overlap=200)

    llm = LLMService()
    generate = request.options.generate

    if generate == "summary":
        return llm.create_summary(chunks, request.options.model_dump(), request.documentId)

    if generate == "quiz":
        return llm.create_quiz(chunks, request.options.model_dump(), request.documentId)

    return llm.create_flashcards(chunks, request.options.model_dump(), request.documentId)
