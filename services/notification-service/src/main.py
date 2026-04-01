"""
Notification Service – FastAPI microservice độc lập.
Nhận yêu cầu gửi thông báo, hiện tại hỗ trợ Gmail SMTP.
Dễ dàng mở rộng sang Slack, SMS, Firebase Push Notification...
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="RAWIQ Notification Service",
    description="Microservice gửi thông báo (Email, Slack, SMS...)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request/Response models ────────────────────────────────────────────────────
class EmailRequest(BaseModel):
    recipient_email: str
    subject: str
    body: str
    body_type: str = "html"       # "html" hoặc "plain"
    sender_email: Optional[str] = None


class NotificationResponse(BaseModel):
    success: bool
    message: str


# ── Endpoints ──────────────────────────────────────────────────────────────────
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "notification-service"}


@app.post("/send/email", response_model=NotificationResponse)
def send_email(request: EmailRequest):
    """
    Gửi email thông qua Gmail SMTP.
    Thông tin xác thực đọc từ biến môi trường SENDER_EMAIL, SENDER_PASSWORD.
    """
    sender_email = request.sender_email or os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    if not sender_email or not sender_password:
        return NotificationResponse(
            success=False, message="Thiếu cấu hình SENDER_EMAIL hoặc SENDER_PASSWORD."
        )

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = request.subject
        msg["From"] = sender_email
        msg["To"] = request.recipient_email
        msg.attach(MIMEText("Email from RAWIQ", "plain"))
        msg.attach(MIMEText(request.body, request.body_type))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        return NotificationResponse(
            success=True, message=f"Email gửi thành công tới {request.recipient_email}"
        )
    except Exception as e:
        return NotificationResponse(success=False, message=str(e))
