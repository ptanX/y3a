"""
HTTP Clients để lending-service giao tiếp với các microservices khác.
Thay vì import trực tiếp Python, lending-service gọi qua HTTP REST.
"""
import os
import requests
from typing import Any, Dict, Optional


class OCRServiceClient:
    """
    Client gọi ocr-service qua HTTP.
    Base URL đọc từ biến môi trường OCR_SERVICE_URL.
    """

    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv("OCR_SERVICE_URL", "http://ocr_service:8001")

    def extract_fields(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Gửi file PDF đến ocr-service, nhận về fields có cấu trúc."""
        try:
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f, "application/pdf")}
                response = requests.post(
                    f"{self.base_url}/extract/fields",
                    files=files,
                    timeout=120,
                )
                response.raise_for_status()
                data = response.json()
                if data.get("success"):
                    return data.get("structured_data")
                print(f"[OCRServiceClient] Lỗi từ server: {data.get('error')}")
                return None
        except Exception as e:
            print(f"[OCRServiceClient] Không thể kết nối ocr-service: {e}")
            return None

    def extract_text(self, file_path: str) -> Optional[str]:
        """Gửi file PDF đến ocr-service, nhận về văn bản thô."""
        try:
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f, "application/pdf")}
                response = requests.post(
                    f"{self.base_url}/extract/text",
                    files=files,
                    timeout=120,
                )
                response.raise_for_status()
                data = response.json()
                if data.get("success"):
                    return data.get("raw_text")
                return None
        except Exception as e:
            print(f"[OCRServiceClient] Không thể kết nối ocr-service: {e}")
            return None

    def health(self) -> bool:
        """Kiểm tra ocr-service còn sống không."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False


class NotificationServiceClient:
    """
    Client gọi notification-service qua HTTP.
    Base URL đọc từ biến môi trường NOTIFICATION_SERVICE_URL.
    """

    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv(
            "NOTIFICATION_SERVICE_URL", "http://notification_service:8002"
        )

    def send_email(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        body_type: str = "html",
        sender_email: str = None,
    ) -> bool:
        """Yêu cầu notification-service gửi email."""
        try:
            payload = {
                "recipient_email": recipient_email,
                "subject": subject,
                "body": body,
                "body_type": body_type,
            }
            if sender_email:
                payload["sender_email"] = sender_email

            response = requests.post(
                f"{self.base_url}/send/email",
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            if data.get("success"):
                print(f"✓ Notification service gửi email OK: {data.get('message')}")
                return True
            print(f"✗ Notification service lỗi: {data.get('message')}")
            return False
        except Exception as e:
            print(f"[NotificationServiceClient] Không thể kết nối notification-service: {e}")
            return False

    def health(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
