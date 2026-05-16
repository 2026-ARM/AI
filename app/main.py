# app/main.py

from fastapi import FastAPI
from app.api.routes_document import router as document_router
from app.api.routes_process import router as process_router

app = FastAPI(title="ARM AI Service")

app.include_router(document_router, prefix="/document", tags=["document"])
app.include_router(process_router, tags=["process"])


@app.get("/")
def read_root():
    return {"message": "ARM AI service is running"}