import datetime
import os

from src.bidv import email_handling


def execute(content):
    files = content["files"]

    # Save the uploaded file to a temporary path
    for uploaded_file in files:
        temp_file_path = os.path.abspath(os.path.join("./temp", uploaded_file.name))
        os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)

        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(uploaded_file.getbuffer())


    fake_content = fake_email_content()
    content = merge_first_not_none(content, fake_content)
    email_handling.send_lending_email(**content)


def fake_email_content():
    base_url = "http://localhost:8501"
    document_id = "4f3f8bb7-83e8-474e-bc14-3ab47ff32e1c"
    recipient_email = "vanhci52@gmail.com"
    recipient_name = "Tên QHKH"
    company_name = "Công ty cổ phần chứng khoán DNSE"
    verification_time = datetime.datetime.now()
    total_fields = "60/72 (theo bộ tiêu chuẩn hồ sơ vay DN chuẩn hóa)"
    document_id = "1111"
    document_status = "- 3 trường thông tin cần kiểm tra\n- 12 trường thông tin bị thiếu"
    detail_url = f"https://{base_url}/detail?document_id={document_id}"

    document_categories = [
        {
            'document_type_name': 'Hồ sơ pháp lý',
            'documents': [
                {'name': 'Giấy phép đăng ký kinh doanh', 'quantity': 1},
                {'name': 'Điều lệ công ty', 'quantity': 1},
                {'name': 'CMND/CCCD người đại diện', 'quantity': 0},
                {'name': 'Quyết định bổ nhiệm', 'quantity': 1}
            ]
        },
        {
            'document_type_name': 'Hồ sơ tài chính',
            'documents': [
                {'name': 'Báo cáo tài chính 2022', 'quantity': 1},
                {'name': 'Báo cáo tài chính 2023', 'quantity': 1},
                {'name': 'Báo cáo tài chính 2024', 'quantity': 1},
                {'name': 'Báo cáo quản hệ tín dụng', 'quantity': 1}
            ]
        },
        {
            'document_type_name': 'Hồ sơ tài sản bảo đảm (TSBD)',
            'documents': [
                {'name': 'Giấy chứng nhận quyền sử dụng đất', 'quantity': 3}
            ]
        },
        {
            'document_type_name': 'Cần bổ sung',
            'documents': [
                {'name': '- CMND/CCCD người đại diện', 'quantity': ''}
            ]
        }
    ]

    return {
        "recipient_email": recipient_email,
        "recipient_name": recipient_name,
        "company_name": company_name,
        "document_id": document_id,
        "verification_time": verification_time,
        "total_fields": total_fields,
        "document_status": document_status,
        "document_categories": document_categories,
        "detail_url": detail_url,
    }


def merge_first_not_none(dict1, dict2):
    """Concise version using dictionary comprehension."""
    all_keys = set(dict1.keys()) | set(dict2.keys())
    return {
        key: dict1.get(key) if dict1.get(key) is not None else dict2.get(key)
        for key in all_keys
        if dict1.get(key) is not None or dict2.get(key) is not None
    }
