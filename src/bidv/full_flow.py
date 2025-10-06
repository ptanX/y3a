import asyncio
import json
import os
import unicodedata
from datetime import datetime

from PyPDF2 import PdfReader, PdfWriter
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.bidv import email_handling
from src.bidv.pdf_text_extractor import DocumentAIExtractor
from src.bidv.services.data_validator_service import DataValidatorService

load_dotenv()


async def execute(file_path, email_input):
    asyncio.create_task(heavy_tasks(file_path, email_input))
    return {"status": "success"}


async def heavy_tasks(file_path, email_input):
    business_file_path, company_charter_file_path = split_report(file_path)
    raw_data = extraction(business_file_path, company_charter_file_path)
    # raw_data = fake_raw_data()
    results = validate_with_database(raw_data)
    email_handling.execute(results, email_input)


def fake_raw_data():
    with open("final_result.json", 'r') as f:
        sample_data = json.load(f)
    return sample_data


def split_report(file_path):
    business_file_path = generate_filename(file_path)
    _cut_pdf(file_path, business_file_path, start_page=1, end_page=1)

    company_charter_file_path = generate_filename(file_path)
    _cut_pdf(file_path, company_charter_file_path, start_page=7, end_page=12)

    return business_file_path, company_charter_file_path


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


def validate_with_database(sample_data):
    DATABASE_PATH = os.environ['BIDV_DB_PATH']
    engine = create_engine(f"sqlite:///{DATABASE_PATH}")
    Session = sessionmaker(bind=engine)
    validator = DataValidatorService(Session)

    results = validator.validate_with_database(sample_data)
    response = {
        "results": results
    }
    return json.loads(json.dumps(response, default=lambda o: o.__dict__, indent=4, ensure_ascii=False))


def _cut_pdf(input_pdf, output_pdf, start_page, end_page):
    """Extracts pages from start_page to end_page (inclusive) into a new PDF."""
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page_num in range(start_page - 1, end_page):  # 0-indexed
        writer.add_page(reader.pages[page_num])

    with open(output_pdf, "wb") as f_out:
        writer.write(f_out)
