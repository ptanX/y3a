from src.ocr.ocr_model import DocumentMetadata, DocumentMetadataPageInfo, DocumentSectionMetadata

KPMG_SECURITIES_FINANCIAL_METADATA = [
    DocumentSectionMetadata(
        component_type="financial_statement",
        page_info=DocumentMetadataPageInfo(page_length=5)
    ),
    DocumentSectionMetadata(
        component_type="income_statement",
        page_info=DocumentMetadataPageInfo(page_length=2)
    )
]
