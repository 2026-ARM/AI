# app/main.py

from fastapi import FastAPI
from app.api.routes_document import router as document_router
from app.api.routes_summary import router as summary_router
from app.api.routes_quiz import router as quiz_router
from app.api.routes_flashcard import router as flashcard_router

app = FastAPI(
    title="ARM AI Service",
    description="AI를 활용한 학습 자료 생성 서비스",
    version="1.0.0"
)

# 라우트 등록
app.include_router(document_router, prefix="/document", tags=["document"])
app.include_router(summary_router, prefix="/ai/summary", tags=["summary"])
app.include_router(quiz_router, prefix="/ai/quiz", tags=["quiz"])
app.include_router(flashcard_router, prefix="/ai/flashcards", tags=["flashcards"])


@app.get("/")
def read_root():
    return {
        "message": "ARM AI service is running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}