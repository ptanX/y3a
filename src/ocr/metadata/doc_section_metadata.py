from src.ocr.ocr_model import (
    DocumentPageInfoMetadata,
    DocumentSectionMetadata,
)

KPMG_SECURITIES_FINANCIAL_SECTION_METADATA = [
    DocumentSectionMetadata(
        component_type="financial_statement",
        page_info=DocumentPageInfoMetadata(page_length=5),
    ),
    DocumentSectionMetadata(
        component_type="income_statement",
        page_info=DocumentPageInfoMetadata(page_length=2),
    ),
]

DNSE_BUSINESS_REGISTRATION = [
    DocumentSectionMetadata(
        component_type="business_registration",
        page_info=DocumentPageInfoMetadata(from_page=1, to_page=1),
    ),
]

SSI_BUSINESS_REGISTRATION = [
    DocumentSectionMetadata(
        component_type="business_registration",
        page_info=DocumentPageInfoMetadata(from_page=3, to_page=3),
    ),
]


DNSE_COMPANY_CHARTER = [
    DocumentSectionMetadata(
        component_type="business_registration",
        page_info=DocumentPageInfoMetadata(from_page=6, to_page=11),
    ),
]


SSI_COMPANY_CHARTER = [
    DocumentSectionMetadata(
        component_type="business_registration",
        page_info=DocumentPageInfoMetadata(from_page=5, to_page=8),
    ),
]
