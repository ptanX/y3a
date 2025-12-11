import asyncio
import datetime
import json
import os
import threading
import uuid
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.lending import email_handling
from src.lending.constant import REQUIRED_FIELDS
from src.lending.db.bidv_entity import DocumentationInformation
from src.lending.full_flow import handle_heavy_tasks
from src.lending.services.data_validator_service import DataValidatorService
from src.lending.services.db_service import query_document_information_by_id
from src.lending.services.document_category import process_document_categories
from src.lending.startup.environment_initialization import DATABASE_PATH


def async_execute(content):
    threading.Thread(
        target=lambda: execute_upload_document(content), daemon=True
    ).start()


def execute_upload_document(content):
    document_id = content["document_id"]
    files = content["files"]
    file_paths = []

    # Save the uploaded file to a temporary path
    for uploaded_file in files:
        temp_file_path = os.path.abspath(
            os.path.join(f"./temp/{document_id}", uploaded_file.name)
        )
        os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)

        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(uploaded_file.getbuffer())

        file_paths.append(temp_file_path)

    del content["files"]
    legal_documents, financial_documents, document_categories = asyncio.run(
        handle_heavy_tasks(file_paths)
    )
    document_data = _build_document_data(content, legal_documents, financial_documents)

    save_document(document_id, document_data)

    email_handling.send_lending_email(
        **document_data,
        document_categories=process_document_categories(document_categories),
    )


def execute_submit_document(content):
    document_id = content["document_id"]
    document_entity = query_document_information_by_id(document_id)
    document_data = json.loads(document_entity.data)
    email_content = merge_first_not_none(content, document_data)
    email_handling.send_verified_lending_email(**email_content)


def _build_document_data(content, legal_documents, financial_documents):
    validate_results = validate_with_database(legal_documents)
    customer_name = next(
        (
            doc.value
            for r in validate_results
            if r.field_name == "company_name_vn"
            for doc in r.origin_docs
            if doc.value is not None
        ),
        None,
    )

    all_fields = get_all_field_names(validate_results, financial_documents)
    missing_fields = REQUIRED_FIELDS - all_fields
    print(missing_fields)

    total_fields = f"{len(REQUIRED_FIELDS) - len(missing_fields)}/{len(REQUIRED_FIELDS)} (trường bắt buộc)"
    consistent_count = sum(
        1 for r in validate_results if r.validation_result.is_consistent_across_doc
    )
    none_count = sum(
        1 for r in validate_results if len(r.origin_docs) == 0 and not r.database_value
    )
    document_status = [
        f"{consistent_count} trường thông tin cần kiểm tra",
        f"{none_count} trường thông tin bị thiếu",
    ]

    document_data = {
        **content,
        "verification_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "customer_name": customer_name,
        "total_fields": total_fields,
        "document_status": document_status,
        "validation_results": validate_results,
        "base_information": {
            "legal_documents": legal_documents,
            "financial_documents": financial_documents,
        },
    }
    return document_data


def get_all_field_names(validate_results, financial_documents):
    field_names = set()

    for field in validate_results:
        field_names.add(field.field_name)

    for company_data in financial_documents:
        if "reports" in company_data:
            for report in company_data["reports"]:
                if "fields" in report:
                    for field in report["fields"]:
                        if "name" in field:
                            field_names.add(field["name"])
    return field_names


def validate_with_database(sample_data):
    engine = create_engine(f"sqlite:///{DATABASE_PATH}")
    Session = sessionmaker(bind=engine)
    validator = DataValidatorService(Session)

    return validator.validate_with_database(sample_data)


def save_document(document_id, data):
    json_data = json.dumps(
        json.loads(
            json.dumps(data, default=lambda o: o.__dict__, indent=2, ensure_ascii=False)
        )
    )
    engine = create_engine(f"sqlite:///{DATABASE_PATH}")
    session = sessionmaker(bind=engine)()
    entity = DocumentationInformation(id=document_id, data=json_data)
    session.add(entity)
    session.commit()


def merge_first_not_none(dict1, dict2):
    """Concise version using dictionary comprehension."""
    all_keys = set(dict1.keys()) | set(dict2.keys())
    return {
        key: dict1.get(key) if dict1.get(key) is not None else dict2.get(key)
        for key in all_keys
        if dict1.get(key) is not None or dict2.get(key) is not None
    }
