"""
Script kiểm tra database sau khi upload.
Chạy: docker exec rawiq_app python /app/scripts/test_db.py
"""

import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_PATH = "/app/data/bidv.db"

if not os.path.exists(DATABASE_PATH):
    print(f"❌ Không tìm thấy database tại {DATABASE_PATH}")
    exit(1)

try:
    engine = create_engine(f"sqlite:///{DATABASE_PATH}")
    Session = sessionmaker(bind=engine)
    session = Session()

    from src.lending.db.bidv_entity import DocumentationInformation

    records = session.query(DocumentationInformation).all()
    print(f"📊 Tìm thấy {len(records)} tài liệu đã được xử lý trong database:\n")

    for r in records:
        print(f"🔹 ID: {r.id}")
        try:
            data = json.loads(r.data)
            status = data.get("document_status", "Không có trường document_status")
            print(f"   Status: {status}")
            print(f"   Customer: {data.get('customer_name')}")
            fields = data.get("total_fields")
            if fields:
                print(f"   Fields: {fields}")
        except Exception as e:
            print(f"   [Error parsing JSON data: {e}]")
            print(f"   Data (first 100 chars): {r.data[:100]}...")
        print("-" * 50)

except Exception as e:
    print(f"❌ Lỗi truy vấn database: {e}")
