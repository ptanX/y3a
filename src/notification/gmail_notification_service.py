import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.notification.notification_service import NotificationService, NotificationMessage


class GmailNotificationService(NotificationService):
    """
    Triển khai NotificationService dùng Gmail SMTP.
    Đọc thông tin xác thực từ biến môi trường SENDER_EMAIL, SENDER_PASSWORD.
    """

    def __init__(
        self,
        sender_email: str = None,
        sender_password: str = None,
        smtp_host: str = "smtp.gmail.com",
        smtp_port: int = 587,
    ):
        self.sender_email = sender_email or os.getenv("SENDER_EMAIL")
        self.sender_password = sender_password or os.getenv("SENDER_PASSWORD")
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port

    def send(self, message: NotificationMessage) -> bool:
        sender = message.sender_email or self.sender_email
        recipient = message.recipient_email

        if not isinstance(sender, str):
            sender = ", ".join(sender)
        if not isinstance(recipient, str):
            recipient = ", ".join(recipient)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = message.subject
        msg["From"] = sender
        msg["To"] = recipient

        plain_payload = MIMEText("plain_body", "plain")
        payload = MIMEText(message.body, message.body_type)
        msg.attach(plain_payload)
        msg.attach(payload)

        try:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(sender, self.sender_password)
            server.send_message(msg)
            server.quit()
            print(f"✓ Email gửi thành công tới {recipient}")
            return True
        except Exception as e:
            print(f"✗ Lỗi gửi email: {e}")
            return False
