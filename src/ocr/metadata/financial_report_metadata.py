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
