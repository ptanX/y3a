"""
Lending Service API – FastAPI entrypoint chính của Backend.
Thay thế Streamlit, cung cấp REST API cho Frontend riêng biệt.

Endpoints:
  POST /api/auth/login
  POST /api/documents/upload
  GET  /api/documents/{document_id}
  GET  /api/documents/{document_id}/validate
  POST /api/chat/invoke
  GET  /api/plugins
  GET  /health
"""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import auth, documents, chat, plugins

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Nạp Plugin Registry khi server khởi động
    from plugin_registry.plugin_loader import plugin_loader
    plugins_loaded = plugin_loader.load_all()
    print(f"[LendingAPI] Đã nạp {len(plugins_loaded)} plugin(s).")
    yield


app = FastAPI(
    title="RAWIQ Lending Service API",
    description="""
## RAWIQ Backend API

REST API cho nền tảng phân tích hồ sơ cho vay RAWIQ.

### Tính năng chính:
- **Authentication**: Đăng nhập, quản lý phiên
- **Documents**: Upload, xem chi tiết, xác thực hồ sơ
- **Chat Agent**: Tương tác với AI Agent để phân tích tài chính
- **Plugins**: Quản lý và truy vấn danh sách plugin
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS – Cho phép FE gọi từ origin khác ──────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Đăng ký routers ────────────────────────────────────────────────────────────
app.include_router(auth.router,      prefix="/api/auth",      tags=["Authentication"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(chat.router,      prefix="/api/chat",      tags=["Chat Agent"])
app.include_router(plugins.router,   prefix="/api/plugins",   tags=["Plugins"])


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "ok",
        "service": "lending-service",
        "version": "1.0.0",
    }
