"""
Script test thử handle_heavy_tasks chạy chay trên file pdf đã tải lên ở temp.
Chạy: docker exec rawiq_app python /app/scripts/test_process.py
"""

import asyncio
import traceback
from src.lending.full_flow import handle_heavy_tasks


async def main():
    # Sử dụng 1 file PDF bất kỳ đã upload lưu trong ./temp/
    file_path = "/app/temp/a35cf673-34f3-447e-9340-c81a23cf2e17/ssi-tc-bctc-2024.pdf"

    print(f"🔄 Đang test quy trình xử lý AI trên file: {file_path}")
    try:
        results = await handle_heavy_tasks([file_path])
        print("✅ Xử lý thành công!")
        print(results)
    except Exception as e:
        print("❌ Lỗi trong quá trình xử lý:")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
