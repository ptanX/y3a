from enum import Enum


class DocumentType(str, Enum):
    BUSINESS_REGISTRATION = "business_registration"
    SECURITIES_FINANCIAL_REPORT = "securities_financial_report"
    COMPANY_CHARTER = "company_charter"


class DocumentMetadataPageRange:

    def __init__(self, from_page: int, to_page: int):
        self.from_page = from_page
        self.to_page = to_page


class DocumentMetadata:
    def __init__(self, doc_type: str, page_range: DocumentMetadataPageRange):
        self.doc_type = doc_type
        self.page_range = page_range
