import asyncio
import datetime
import json
import os
import threading
import uuid
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.bidv import email_handling
from src.bidv.db.bidv_entity import DocumentationInformation
from src.bidv.full_flow import handle_heavy_tasks
from src.bidv.services.data_validator_service import DataValidatorService
from src.bidv.startup.environment_initialization import DATABASE_PATH


def async_execute(content):
    threading.Thread(
        target=lambda: execute_upload_document(content),
        daemon=True
    ).start()


def execute_upload_document(content):
    document_id = content["document_id"]
    files = content["files"]
    file_paths = []

    # Save the uploaded file to a temporary path
    for uploaded_file in files:
        temp_file_path = os.path.abspath(os.path.join(f"./temp/{document_id}", uploaded_file.name))
        os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)

        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(uploaded_file.getbuffer())

        file_paths.append(temp_file_path)

    del content["files"]
    raw_data, financial_documents = asyncio.run(handle_heavy_tasks(file_paths))
    document_data = _build_document_data(content, raw_data)

    save_document(document_id, document_data)

    financial_document_id = document_data["financial_document_id"]
    save_document(financial_document_id, financial_documents)

    fake_content = fake_email_content()
    email_content = merge_first_not_none(document_data, fake_content)
    email_handling.send_lending_email(**email_content)


def execute_submit_document(content):
    document_id = content["document_id"]
    engine = create_engine(f"sqlite:///{DATABASE_PATH}")
    session = sessionmaker(bind=engine)()
    document_entity = session.get(DocumentationInformation, document_id)
    document_data = json.loads(document_entity.data)
    email_content = merge_first_not_none(content, document_data)
    email_handling.send_verified_lending_email(**email_content)


def _build_document_data(content, extracted_data):
    document_id = content["document_id"]
    financial_document_id = str(uuid.uuid4())
    validate_results = validate_with_database(extracted_data)
    customer_name = next(
        (doc.value for r in validate_results if r.field_name == "company_name_vn"
         for doc in r.origin_docs if doc.value is not None),
        None
    )

    total_fields = f"{len(validate_results)}/72 (theo bộ tiêu chuẩn hồ sơ vay DN chuẩn hóa)"
    consistent_count = sum(1 for r in validate_results if r.validation_result.is_consistent_across_doc)
    none_count = sum(1 for r in validate_results if len(r.origin_docs) == 0 and not r.database_value)
    document_status = [f"{consistent_count} trường thông tin cần kiểm tra", f"{none_count} trường thông tin bị thiếu"]
    base_url = os.environ.get("BASE_URL", "http://localhost:8501")
    detail_url = f"{base_url}/detail?document_id={document_id}"

    document_data = {
        **content,
        "financial_document_id": financial_document_id,
        "verification_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "customer_name": customer_name,
        "total_fields": total_fields,
        "document_status": document_status,
        "detail_url": detail_url,
        "validation_results": validate_results,
    }
    return document_data


def validate_with_database(sample_data):
    engine = create_engine(f"sqlite:///{DATABASE_PATH}")
    Session = sessionmaker(bind=engine)
    validator = DataValidatorService(Session)

    return validator.validate_with_database(sample_data)


def save_document(document_id, data):
    json_data = json.dumps(json.loads(json.dumps(data, default=lambda o: o.__dict__, indent=2, ensure_ascii=False)))
    engine = create_engine(f"sqlite:///{DATABASE_PATH}")
    session = sessionmaker(bind=engine)()
    entity = DocumentationInformation(id=document_id, data=json_data)
    session.add(entity)
    session.commit()


def fake_email_content():
    loan_purpose = "Bổ sung vốn lưu động kinh doanh chứng khoán"
    loan_term = "12 tháng"
    loan_amount = "7.000.000.000 VND"

    document_categories = [
        {
            'document_type_name': 'Hồ sơ pháp lý',
            'documents': [
                {'name': 'Giấy phép đăng ký kinh doanh', 'quantity': 1},
                {'name': 'Điều lệ công ty', 'quantity': 1},
                {'name': 'CMND/CCCD người đại diện', 'quantity': 1},
                {'name': 'Quyết định bổ nhiệm', 'quantity': 0}
            ]
        },
        {
            'document_type_name': 'Hồ sơ tài chính',
            'documents': [
                {'name': 'Báo cáo tài chính 2022', 'quantity': 1},
                {'name': 'Báo cáo tài chính 2023', 'quantity': 1},
                {'name': 'Báo cáo tài chính 2024', 'quantity': 1},
                {'name': 'Báo cáo quản hệ tín dụng', 'quantity': 0}
            ]
        },
        {
            'document_type_name': 'Hồ sơ tài sản bảo đảm (TSBD)',
            'documents': [
                {'name': 'Giấy chứng nhận quyền sử dụng đất', 'quantity': 0}
            ]
        },
        {
            'document_type_name': 'Cần bổ sung',
            'documents': [
                {'name': 'Giấy chứng nhận quyền sử dụng đất', 'quantity': 1}
            ]
        }
    ]

    return {
        "loan_purpose": loan_purpose,
        "loan_term": loan_term,
        "loan_amount": loan_amount,
        "document_categories": document_categories,
    }


def merge_first_not_none(dict1, dict2):
    """Concise version using dictionary comprehension."""
    all_keys = set(dict1.keys()) | set(dict2.keys())
    return {
        key: dict1.get(key) if dict1.get(key) is not None else dict2.get(key)
        for key in all_keys
        if dict1.get(key) is not None or dict2.get(key) is not None
    }
