"""
OCR Service – FastAPI microservice độc lập.
Nhận file PDF, trả về văn bản và cấu trúc dữ liệu đã trích xuất.
Các service khác gọi qua HTTP REST, KHÔNG import trực tiếp.
"""

import os
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.ocr_service.documentai_handler import DocumentAIHandler


# ── Khởi tạo handler một lần duy nhất khi service khởi động ──────────────────
_ocr_handler: Optional[DocumentAIHandler] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _ocr_handler
    _ocr_handler = DocumentAIHandler(
        project_id=os.environ["GCP_PROJECT_ID"],
        location=os.environ.get("DOCUMENT_AI_LOCATION", "us"),
        processor_id=os.environ["DOCUMENT_AI_PROCESSOR_ID"],
    )
    yield


app = FastAPI(
    title="RAWIQ OCR Service",
    description="Microservice trích xuất văn bản và bảng biểu từ PDF",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Response models ────────────────────────────────────────────────────────────
class OCRResponse(BaseModel):
    success: bool
    structured_data: Optional[Dict[str, Any]] = None
    raw_text: Optional[str] = None
    error: Optional[str] = None


# ── Endpoints ──────────────────────────────────────────────────────────────────
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ocr-service"}


@app.post("/extract/fields", response_model=OCRResponse)
async def extract_fields(file: UploadFile = File(...)):
    """
    Trích xuất các fields có cấu trúc từ form/bảng biểu kế toán.
    Dùng Google Document AI để nhận diện từng ô trong bảng.
    """
    if _ocr_handler is None:
        raise HTTPException(status_code=503, detail="OCR handler chưa được khởi tạo.")

    try:
        content = await file.read()
        result = _ocr_handler.extract_fields_from_bytes(
            content=content,
            mime_type=file.content_type or "application/pdf",
        )
        return OCRResponse(success=True, structured_data=result)
    except Exception as e:
        return OCRResponse(success=False, error=str(e))


@app.post("/extract/text", response_model=OCRResponse)
async def extract_text(file: UploadFile = File(...)):
    """
    Trích xuất toàn bộ văn bản thô từ tài liệu PDF.
    Dùng Gemini Vision để đọc và dịch các trang tài liệu.
    """
    try:
        content = await file.read()
        result = _ocr_handler.extract_text_from_bytes(content=content)
        return OCRResponse(success=True, raw_text=result)
    except Exception as e:
        return OCRResponse(success=False, error=str(e))
