"""
Documents Router – Quản lý hồ sơ tài liệu.
POST /api/documents/upload        → Upload hồ sơ (OCR async)
GET  /api/documents/{id}          → Lấy chi tiết hồ sơ
GET  /api/documents/{id}/validate → Kết quả xác thực chéo
GET  /api/documents               → Danh sách hồ sơ
"""

import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel

from api.routers.auth import get_current_user
from src.lending import e2e_usecases
from src.lending.services.db_service import query_document_information_by_id

router = APIRouter()


# ── Models ────────────────────────────────────────────────────────────────────
class UploadResponse(BaseModel):
    document_id: str
    message: str
    recipient_email: str
    file_count: int
    timestamp: str


class DocumentDetail(BaseModel):
    document_id: str
    data: dict
    created_at: Optional[str] = None


# ── Endpoints ─────────────────────────────────────────────────────────────────
@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    recipient_name: str = Form(..., description="Tên quan hệ khách hàng"),
    recipient_email: str = Form(..., description="Email nhận kết quả"),
    files: List[UploadFile] = File(..., description="Các file PDF hồ sơ"),
    current_user: dict = Depends(get_current_user),
):
    """
    Upload hồ sơ tài liệu để xử lý OCR và phân tích AI.
    Trả về ngay document_id, xử lý OCR chạy ngầm (async).
    Kết quả sẽ được gửi qua email khi hoàn thành.
    """
    if "upload" not in current_user.get("permissions", []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Không có quyền upload.")

    document_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    upload_record = {
        "document_id": document_id,
        "recipient_name": recipient_name,
        "recipient_email": recipient_email,
        "files": files,                 # e2e_usecases sẽ đọc .read() bên trong
        "timestamp": timestamp,
        "uploaded_by": current_user["username"],
        "uploaded_by_name": current_user["full_name"],
    }

    # Chạy ngầm – không block HTTP response
    e2e_usecases.async_execute(upload_record)

    return UploadResponse(
        document_id=document_id,
        message=f"Đã tiếp nhận {len(files)} file. Kết quả sẽ gửi về {recipient_email}.",
        recipient_email=recipient_email,
        file_count=len(files),
        timestamp=timestamp,
    )


@router.get("/{document_id}", response_model=DocumentDetail)
def get_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Lấy toàn bộ dữ liệu đã xử lý của một hồ sơ theo ID."""
    if "details" not in current_user.get("permissions", []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Không có quyền xem chi tiết.")

    try:
        entity = query_document_information_by_id(document_id)
        if entity is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy hồ sơ.")
        import json
        return DocumentDetail(
            document_id=document_id,
            data=json.loads(entity.data),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{document_id}/validate")
def validate_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Lấy kết quả xác thực chéo (cross-validation) của hồ sơ."""
    if "details" not in current_user.get("permissions", []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Không có quyền xem xác thực.")

    import json
    entity = query_document_information_by_id(document_id)
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy hồ sơ.")

    data = json.loads(entity.data)
    return {
        "document_id": document_id,
        "validation_results": data.get("validation_results", []),
        "document_status": data.get("document_status", []),
        "total_fields": data.get("total_fields"),
    }
