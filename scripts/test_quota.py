"""
Kiểm tra quota Gemini API Key còn hay không.
Chạy: docker exec rawiq_app python /tmp/test_quota.py
"""

import os
from dotenv import load_dotenv

load_dotenv("/app/.env")
api_key = os.getenv("GOOGLE_API_KEY")
print(f"Key: {api_key[:10]}...{api_key[-4:]}\n")

# Thử từng model theo thứ tự ưu tiên
models_to_try = [
    "gemini-2.5-flash",  # model đang dùng trong code
    "gemini-2.5-pro",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]

from google import genai

for model in models_to_try:
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model=model, contents="Say OK")
        print(f"✅ {model:<25} → CÒN QUOTA! Response: {response.text.strip()[:30]}")
    except Exception as e:
        err = str(e)
        if "429" in err or "RESOURCE_EXHAUSTED" in err:
            print(f"❌ {model:<25} → HẾT QUOTA (429)")
        elif "404" in err or "not found" in err.lower():
            print(f"⚠️  {model:<25} → Model không tồn tại")
        elif "API_KEY_INVALID" in err:
            print(f"🔑 {model:<25} → API KEY KHÔNG HỢP LỆ")
        else:
            print(f"⚠️  {model:<25} → Lỗi: {err[:80]}")
