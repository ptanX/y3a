import asyncio
import json
import os
import threading
import uuid
from datetime import datetime
from typing import List

import unicodedata
from PyPDF2 import PdfReader, PdfWriter
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.lending import email_handling
from src.lending.db.bidv_entity import DocumentationInformation
from src.lending.pdf_text_extractor import DocumentAIExtractor
from src.lending.services.data_validator_service import DataValidatorService
from src.lending.startup.environment_initialization import DATABASE_PATH
from src.lending.table_parsing import extract_information
from src.dispatcher.executions_dispatcher import ExecutionDispatcherBuilder, ExecutionInput, ExecutionOutput
from src.ocr.data.data_retriever import FinancialSecuritiesReportDataRetriever, BusinessRegistrationDataRetriever, \
    CompanyCharterDataRetriever
from src.ocr.metadata.identifier_retriever import NameBasedIdentifierRetriever
from src.ocr.metadata.metadata_retriever import extract_single_securities_raw_metadata_report_page, \
    SecuritiesFinancialReportMetadataRetriever, BusinessRegistrationMetadataRetriever, CompanyCharterMetadataRetriever, \
    BUSINESS_REGISTRATION_SINGLE_METADATA_PAGE_EXTRACTION, extract_single_business_registration_raw_metadata_page, \
    SECURITIES_FINANCIAL_REPORT_SINGLE_METADATA_PAGE_EXTRACTION

load_dotenv()

FINANCIAL_EXECUTION_DISPATCHER = (
    ExecutionDispatcherBuilder().set_dispatcher(
        name=SECURITIES_FINANCIAL_REPORT_SINGLE_METADATA_PAGE_EXTRACTION,
        handler=extract_single_securities_raw_metadata_report_page,
    ).build()
)
FINANCIAL_METADATA_RETRIEVER = SecuritiesFinancialReportMetadataRetriever(
    execution_dispatcher=FINANCIAL_EXECUTION_DISPATCHER
)
BUSINESS_REGISTRATION_METADATA_RETRIEVER = BusinessRegistrationMetadataRetriever(
    ExecutionDispatcherBuilder().set_dispatcher(
        name=BUSINESS_REGISTRATION_SINGLE_METADATA_PAGE_EXTRACTION,
        handler=extract_single_business_registration_raw_metadata_page
    ).build()
)
COMPANY_CHARTER_METADATA_RETRIEVER = CompanyCharterMetadataRetriever()
FINANCIAL_DATA_RETRIEVER = FinancialSecuritiesReportDataRetriever()
BUSINESS_REGISTRATION_DATA_RETRIEVER = BusinessRegistrationDataRetriever()
COMPANY_CHARTER_DATA_RETRIEVER = CompanyCharterDataRetriever()


def execute(file_path, email_input):
    # Start async task in background thread
    threading.Thread(
        target=lambda: asyncio.run(heavy_tasks(file_path, email_input)),
        daemon=True
    ).start()
    return {"status": "success"}


async def handle_heavy_tasks(files: List[str]):
    identifier_retriever = NameBasedIdentifierRetriever()
    heavy_task_execution_handler = ExecutionDispatcherBuilder().set_dispatcher(
       name="handle_business_registration",
       handler=handle_business_registration
    ).set_dispatcher(
        name="handle_company_charter",
        handler=handle_company_charter
    ).set_dispatcher(
        name="handle_securities_financial_report",
        handler=handle_securities_financial_report
    ).build()
    execution_items = []
    financial_data = []
    company_charter_data = {}
    business_registration_data = {}
    for file_path in files:
        identifier = identifier_retriever.retrieve(path=file_path)
        if identifier.file_type == 'dl':
            execution_input = ExecutionInput(
                handler_name="handle_company_charter",
                execution_id="dl",
                input_content={"file_path": file_path, "identifier": identifier}
            )
            execution_items.append(execution_input)
        if identifier.file_type == 'dkkd':
            execution_input = ExecutionInput(
                handler_name="handle_business_registration",
                execution_id=f"dkkd",
                input_content={"file_path": file_path, "identifier": identifier}
            )
            execution_items.append(execution_input)
        if identifier.file_type == 'bctc':
            execution_input = ExecutionInput(
                handler_name="handle_securities_financial_report",
                execution_id=f"bctc_{identifier.time}",
                input_content={"file_path": file_path, "identifier": identifier}
            )
            execution_items.append(execution_input)
    execution_outputs = await heavy_task_execution_handler.dispatch(execution_items)
    # handle on parallel
    for execution_output in execution_outputs:
        if execution_output.handler_name == "handle_company_charter":
            company_charter_data = execution_output.output_content
        elif execution_output.handler_name == "handle_business_registration":
            business_registration_data = execution_output.output_content
        elif execution_output.handler_name == "handle_securities_financial_report":
            financial_data.append(execution_output.output_content)

    raw_data = {"business_registration_cert": business_registration_data, "company_charter": company_charter_data}
    # validate_results = validate_with_database(raw_data)

    return raw_data, financial_data


def handle_business_registration(execution_input: ExecutionInput) -> ExecutionOutput:
    file_path = execution_input.input_content.get("file_path")
    identifier = execution_input.input_content.get("identifier")
    business_registration_metadata = asyncio.run(BUSINESS_REGISTRATION_METADATA_RETRIEVER.retrieve(path=file_path,
                                                                                             document_identifier=identifier))
    business_registration_data =asyncio.run(BUSINESS_REGISTRATION_DATA_RETRIEVER.retrieve(business_registration_metadata))
    return ExecutionOutput(
        handler_name=execution_input.handler_name,
        execution_id=execution_input.execution_id,
        output_content=business_registration_data
    )


def handle_company_charter(execution_input: ExecutionInput) -> ExecutionOutput:
    file_path = execution_input.input_content.get("file_path")
    identifier = execution_input.input_content.get("identifier")
    company_charter_metadata = asyncio.run(COMPANY_CHARTER_METADATA_RETRIEVER.retrieve(path=file_path,
                                                                                 document_identifier=identifier))
    company_charter_data = asyncio.run(COMPANY_CHARTER_DATA_RETRIEVER.retrieve(doc_metadata=company_charter_metadata))
    return ExecutionOutput(
        handler_name=execution_input.handler_name,
        execution_id=execution_input.execution_id,
        output_content=company_charter_data
    )


def handle_securities_financial_report(execution_input: ExecutionInput) -> ExecutionOutput:
    file_path = execution_input.input_content.get("file_path")
    identifier = execution_input.input_content.get("identifier")
    financial_metadata = asyncio.run(FINANCIAL_METADATA_RETRIEVER.retrieve(path=file_path,
                                                                     document_identifier=identifier))
    financial_data = asyncio.run(FINANCIAL_DATA_RETRIEVER.retrieve(financial_metadata))
    return ExecutionOutput(
        handler_name=execution_input.handler_name,
        execution_id=execution_input.execution_id,
        output_content=financial_data
    )


async def heavy_tasks(file_path, email_input):
    document_id = str(uuid.uuid4())

    # Step 1: Validate the document
    business_file_path, company_charter_file_path = split_report_for_verify(file_path)
    # raw_data = extraction(business_file_path, company_charter_file_path)
    raw_data = fake_raw_data()
    validate_results = validate_with_database(raw_data)

    # Step 2: Split document then save to db
    balance_sheet_y22, income_statement_y22 = split_report_for_analyze(file_path, 2022)
    balance_sheet_y23, income_statement_y23 = split_report_for_analyze(file_path, 2023)
    balance_sheet_y24, income_statement_y24 = split_report_for_analyze(file_path, 2024)

    # raw_data_y22 = fake_extraction_statistic(balance_sheet_y22, income_statement_y22, "2022-12-31")
    # raw_data_y23 = fake_extraction_statistic(balance_sheet_y23, income_statement_y23, "2023-12-31")
    # raw_data_y24 = fake_extraction_statistic(balance_sheet_y24, income_statement_y24, "2024-03-31")
    tasks = [
        async_wrapper(extraction_statistic, balance_sheet_y22, income_statement_y22, "2022-12-31"),
        async_wrapper(extraction_statistic, balance_sheet_y23, income_statement_y23, "2023-12-31"),
        async_wrapper(extraction_statistic, balance_sheet_y24, income_statement_y24, "2024-03-31")
    ]

    raw_data_y22, raw_data_y23, raw_data_y24 = await asyncio.gather(*tasks)

    documents = [raw_data_y22, raw_data_y23, raw_data_y24]
    save_document(document_id, documents)

    # Step 3: Send email when processing is done
    email_handling.execute(document_id, validate_results, email_input)


async def async_wrapper(func, *args, **kwargs):
    """Async wrapper for the extraction_numbers function"""
    loop = asyncio.get_event_loop()
    # Run the blocking function in a thread pool
    return await loop.run_in_executor(
        None,
        func,
        *args
    )


def fake_raw_data():
    with open("final_result.json", 'r') as f:
        sample_data = json.load(f)
    return sample_data


def split_report_for_verify(file_path):
    business_file_path = generate_filename(file_path)
    _cut_pdf(file_path, business_file_path, start_page=1, end_page=1)

    company_charter_file_path = generate_filename(file_path)
    _cut_pdf(file_path, company_charter_file_path, start_page=7, end_page=12)

    return business_file_path, company_charter_file_path


def split_report_for_analyze(file_path, year):
    if year == 2022:
        balance_sheet_file_path = generate_filename(file_path)
        _cut_pdf(file_path, balance_sheet_file_path, start_page=54, end_page=56)

        income_statement_file_path = generate_filename(file_path)
        _cut_pdf(file_path, income_statement_file_path, start_page=59, end_page=60)

        return balance_sheet_file_path, income_statement_file_path

    if year == 2023:
        balance_sheet_file_path = generate_filename(file_path)
        _cut_pdf(file_path, balance_sheet_file_path, start_page=106, end_page=108)

        income_statement_file_path = generate_filename(file_path)
        _cut_pdf(file_path, income_statement_file_path, start_page=111, end_page=112)

        return balance_sheet_file_path, income_statement_file_path

    if year == 2024:
        balance_sheet_file_path = generate_filename(file_path)
        _cut_pdf(file_path, balance_sheet_file_path, start_page=167, end_page=169)

        income_statement_file_path = generate_filename(file_path)
        _cut_pdf(file_path, income_statement_file_path, start_page=172, end_page=173)

        return balance_sheet_file_path, income_statement_file_path

    raise ValueError("Invalid year")


def clean_filename(text):
    """Remove Vietnamese accents, lowercase, spaces to dashes"""
    # Remove accents
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')

    # Replace đ
    text = text.replace('đ', 'd').replace('Đ', 'd')

    # Lowercase and replace spaces
    text = text.lower().replace(' ', '-')

    return text


def generate_filename(old_path):
    """Generate new file path with cleaned name"""
    directory = os.path.dirname(old_path)
    filename = os.path.basename(old_path)
    name, ext = os.path.splitext(filename)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S.%f")
    new_name = clean_filename(name)
    new_filename = f"{new_name}_{timestamp}{ext}"
    return os.path.join(directory, new_filename)


def extraction(business_file_path, company_charter_file_path):
    PROJECT_ID = "387819483924"
    LOCATION = "us"
    business_registration_processor_id = "5110722c3ac24f03"
    company_character_processor_id = "12676ebbd1c0ed5"

    business_regis_extractor = DocumentAIExtractor(project_id=PROJECT_ID,
                                                   location=LOCATION,
                                                   processor_id=business_registration_processor_id,
                                                   )
    business_regis_cert = business_regis_extractor.extract_normalized_text(file_path=business_file_path)

    company_charter_extractor = DocumentAIExtractor(project_id=PROJECT_ID,
                                                    location=LOCATION,
                                                    processor_id=company_character_processor_id,
                                                    )
    company_charter = company_charter_extractor.extract_normalized_text(file_path=company_charter_file_path)

    result = {"business_registration_cert": business_regis_cert, "company_charter": company_charter}

    with open("final_result.json", 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result


def extraction_statistic(business_file_path, income_statement_file_path, report_date) -> dict:
    business_sheet_numbers = extract_information(business_file_path)
    income_statement_sheet_numbers = extract_information(income_statement_file_path)

    return {
        "company": "DNSE Securities Joint Stock Company",
        "report_date": report_date,
        "currency": "VND",
        "reports": [
            {
                "report_name": "balance_sheet",
                "description": "Báo cáo tình hình tài chính",
                "fields": business_sheet_numbers,
            },
            {
                "report_name": "income_statement",
                "description": "Income Statement",
                "fields": income_statement_sheet_numbers,
            }
        ]
    }


def fake_extraction_statistic(business_file_path, income_statement_file_path, report_date) -> dict:
    with open("/Users/anhdv7/Desktop/practice/y3a/temp/ho-so-dnse_20251016_002649.265565.json", "r") as f:
        business_sheet_numbers = json.loads(f.read())

    with open("/Users/anhdv7/Desktop/practice/y3a/temp/ho-so-dnse_20251016_002649.243636.json", "r") as f:
        income_statement_sheet_numbers = json.loads(f.read())

    return {
        "company": "DNSE Securities Joint Stock Company",
        "report_date": report_date,
        "currency": "VND",
        "reports": [
            {
                "report_name": "balance_sheet",
                "description": "Báo cáo tình hình tài chính",
                "fields": business_sheet_numbers,
            },
            {
                "report_name": "income_statement",
                "description": "Income Statement",
                "fields": income_statement_sheet_numbers,
            }
        ]
    }


def validate_with_database(sample_data):
    engine = create_engine(f"sqlite:///{DATABASE_PATH}")
    Session = sessionmaker(bind=engine)
    validator = DataValidatorService(Session)

    results = validator.validate_with_database(sample_data)
    response = {
        "results": results
    }
    return json.loads(json.dumps(response, default=lambda o: o.__dict__, indent=4, ensure_ascii=False))


def save_document(document_id, data):
    engine = create_engine(f"sqlite:///{DATABASE_PATH}")
    session = sessionmaker(bind=engine)()
    entity = DocumentationInformation(id=document_id, data=json.dumps(data, ensure_ascii=False))
    session.add(entity)
    session.commit()


def _cut_pdf(input_pdf, output_pdf, start_page, end_page):
    """Extracts pages from start_page to end_page (inclusive) into a new PDF."""
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page_num in range(start_page - 1, end_page):  # 0-indexed
        writer.add_page(reader.pages[page_num])

    with open(output_pdf, "wb") as f_out:
        writer.write(f_out)


# if __name__ == '__main__':
#
#     list_files = []
#     result = asyncio.run(handle_heavy_tasks(list_files))
#     print(result)
