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

    summary = None
    quizzes = None
    flashcards = None

    if "summary" in request.options.generate:
        summary = llm.create_summary(chunks, request.options.model_dump())

    if "quiz" in request.options.generate:
        quizzes = llm.create_quiz(chunks, request.options.model_dump())

    if "flashcard" in request.options.generate:
        flashcards = llm.create_flashcards(chunks, request.options.model_dump())

    return ProcessResponse(
        document_id=request.documentId,
        file_url=request.fileUrl,
        page_count=extraction["page_count"],
        chunk_count=len(chunks),
        summary=summary,
        quizzes=quizzes,
        flashcards=flashcards,
        generated_language=request.options.language,
        difficulty=request.options.difficulty,
    )
