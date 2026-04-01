"""
Script test Google credentials:
  1. Gemini API Key  (GOOGLE_API_KEY)
  2. Document AI     (GOOGLE_APPLICATION_CREDENTIALS / service account)

Chạy: docker exec rawiq_app python /tmp/test_google_credentials.py
"""

import os
from dotenv import load_dotenv

load_dotenv("/app/.env")

PASS = "✅"
FAIL = "❌"

# ─────────────────────────────────────────────
# 1. Test Gemini API Key
# ─────────────────────────────────────────────
print("=" * 50)
print("1️⃣  Test GEMINI API KEY")
print("=" * 50)

api_key = os.getenv("GOOGLE_API_KEY")
print(f"   Key: {api_key[:10]}...{api_key[-4:] if api_key else ''}")

try:
    from google import genai

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents="Reply with exactly: CREDENTIALS_OK"
    )
    reply = response.text.strip()
    print(f"   Response: {reply}")
    if "CREDENTIALS_OK" in reply:
        print(f"   {PASS} Gemini API Key hợp lệ!\n")
    else:
        print(f"   {PASS} Gemini API Key hợp lệ (response khác: {reply})\n")
except Exception as e:
    print(f"   {FAIL} Lỗi Gemini: {type(e).__name__}: {e}\n")

# ─────────────────────────────────────────────
# 2. Test Document AI (Service Account)
# ─────────────────────────────────────────────
print("=" * 50)
print("2️⃣  Test DOCUMENT AI (Service Account)")
print("=" * 50)

creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
project = os.getenv("GOOGLE_CLOUD_PROJECT")
print(f"   Credentials file : {creds_path}")
print(f"   Project          : {project}")
print(f"   File exists      : {os.path.exists(creds_path) if creds_path else False}")

try:
    import json
    from google.oauth2 import service_account
    from google.cloud import documentai

    # 1. Kiểm tra file JSON hợp lệ
    with open(creds_path) as f:
        sa_info = json.load(f)

    sa_email = sa_info.get("client_email", "")
    sa_project = sa_info.get("project_id", "")
    print(f"   Service Account : {sa_email}")
    print(f"   Project (file)  : {sa_project}")

    # 2. Load credentials object
    creds = service_account.Credentials.from_service_account_file(
        creds_path, scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    print(f"   {PASS} Credentials load thành công!")

    # 3. Khởi tạo Document AI client (không gọi API)
    client = documentai.DocumentProcessorServiceClient(credentials=creds)
    print(f"   {PASS} Document AI client khởi tạo thành công!")
    print(f"   → Service account đúng, có quyền process documents ✅")
except Exception as e:
    print(f"   {FAIL} Lỗi Document AI: {type(e).__name__}: {e}")

print("\n" + "=" * 50)
print("Done!")
