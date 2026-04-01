"""
Script test gửi email đơn giản qua SMTP Gmail.
Chạy bên trong container: docker exec rawiq_app python /tmp/test_email.py
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv("/app/.env")

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECIPIENT_EMAIL = "madara.at2k@gmail.com"

print(f"📧 Sender   : {SENDER_EMAIL}")
print(f"📨 Recipient: {RECIPIENT_EMAIL}")

# ── Build email ──────────────────────────────────────────────
msg = MIMEMultipart("alternative")
msg["Subject"] = "✅ [RawIQ] Test email - SMTP đang hoạt động!"
msg["From"] = SENDER_EMAIL
msg["To"] = RECIPIENT_EMAIL

html_body = """\
<html>
<body style="font-family: Arial, sans-serif; padding: 20px;">
  <h2 style="color: #2e86de;">🧬 RawIQ – Test Email</h2>
  <p>Xin chào,</p>
  <p>Đây là email test tự động từ hệ thống <strong>RawIQ</strong> chạy trên Docker.</p>
  <hr/>
  <ul>
    <li><b>SMTP Server:</b> smtp.gmail.com:587</li>
    <li><b>Sender:</b> {sender}</li>
    <li><b>Status:</b> ✅ Kết nối thành công</li>
  </ul>
  <p style="color: #888; font-size: 12px;">Email này được gửi lúc test cấu hình hệ thống.</p>
</body>
</html>
""".format(
    sender=SENDER_EMAIL
)

msg.attach(MIMEText(html_body, "html", "utf-8"))

# ── Send ─────────────────────────────────────────────────────
try:
    print("\n🔌 Đang kết nối đến smtp.gmail.com:587 ...")
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        print("🔐 Đang đăng nhập ...")
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
    print(f"\n✅ Gửi thành công! Kiểm tra hộp thư: {RECIPIENT_EMAIL}")
except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ Lỗi xác thực Gmail: {e}")
    print(
        "   → Đảm bảo SENDER_PASSWORD là App Password (16 ký tự), không phải mật khẩu Gmail thường."
    )
    print("   → Tạo App Password tại: https://myaccount.google.com/apppasswords")
except Exception as e:
    print(f"\n❌ Lỗi: {type(e).__name__}: {e}")
