# app/main.py

from fastapi import FastAPI
from app.api.routes_document import router as document_router

app = FastAPI(title="ARM AI Service")

app.include_router(document_router, prefix="/document", tags=["document"])


@app.get("/")
def read_root():
    return {"message": "ARM AI service is running"}