from src.ocr.ocr_model import DocumentMetadata, DocumentMetadataPageInfo

KPMG_SECURITIES_FINANCIAL_METADATA = [
    DocumentMetadata(
        component_type="financial_statement",
        page_info=DocumentMetadataPageInfo(page_length=5)
    ),
    DocumentMetadata(
        component_type="income_statement",
        page_info=DocumentMetadataPageInfo(page_length=2)
    )
]
