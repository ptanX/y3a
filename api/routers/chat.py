"""
Chat Router – Tương tác với AI Agent qua MLflow endpoint.
POST /api/chat/invoke → Gửi câu hỏi, nhận phân tích AI
"""

import os
from typing import Any, Dict, List, Optional, Union

import requests
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from api.routers.auth import get_current_user

router = APIRouter()

MLFLOW_ENDPOINT = os.getenv("MLFLOW_MODEL_ENDPOINT", "http://mlflow_serve:8080/invocations")


# ── Models ────────────────────────────────────────────────────────────────────
class ChatMessage(BaseModel):
    role: str       # "user" hoặc "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    document_id: Optional[str] = None
    documents: Optional[List[Dict[str, Any]]] = None


class ChatResponse(BaseModel):
    reply: str
    model_used: str = "rawiq-quickstart-model"


# ── Endpoints ─────────────────────────────────────────────────────────────────
@router.post("/invoke", response_model=ChatResponse)
def invoke_chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Gửi câu hỏi tới AI Agent để phân tích tài chính.
    Yêu cầu permission 'chat_agent'.
    """
    if "chat_agent" not in current_user.get("permissions", []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Không có quyền dùng Chat Agent.")

    # Chuẩn bị payload theo MLflow chat agent format
    last_message = request.messages[-1].content if request.messages else ""

    payload = {
        "messages": [
            {
                "role": msg.role,
                "content": msg.content if msg.role != "user" else _build_enriched_content(
                    question=last_message if msg == request.messages[-1] else msg.content,
                    document_id=request.document_id,
                    documents=request.documents or [],
                )
            }
            for msg in request.messages
        ]
    }

    try:
        response = requests.post(
            MLFLOW_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120,
        )
        response.raise_for_status()
        result = response.json()

        # Trích xuất nội dung từ MLflow response
        reply = _extract_reply(result)
        return ChatResponse(reply=reply)

    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Không thể kết nối tới AI Model. Vui lòng thử lại sau."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi AI Model: {str(e)}"
        )


def _build_enriched_content(question: str, document_id: Optional[str], documents: list) -> str:
    """Gắn context tài liệu vào câu hỏi trước khi gửi tới MLflow."""
    import json
    return json.dumps({
        "question": question,
        "document_id": document_id or "",
        "documents": documents,
    })


def _extract_reply(mlflow_response: Union[dict, str]) -> str:
    """Trích xuất text trả lời từ nhiều format response của MLflow."""
    if isinstance(mlflow_response, str):
        return mlflow_response
    if isinstance(mlflow_response, dict):
        # Format: {"messages": [{"content": "..."}]}
        messages = mlflow_response.get("messages", [])
        if messages:
            return messages[-1].get("content", str(mlflow_response))
        # Format đơn giản: {"content": "..."}
        return mlflow_response.get("content", str(mlflow_response))
    return str(mlflow_response)
