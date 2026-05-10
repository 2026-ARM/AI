# app/main.py

from fastapi import FastAPI
from app.api.routes_document import router as document_router
from app.api.routes_summary import router as summary_router

app = FastAPI(title="ARM AI Service")

app.include_router(document_router, prefix="/document", tags=["document"])
app.include_router(summary_router, prefix="/ai/summary", tags=["summary"])


@app.get("/")
def read_root():
    return {"message": "ARM AI service is running"}