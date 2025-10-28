from enum import Enum


class DocumentType(str, Enum):
    BUSINESS_REGISTRATION = "business_registration"
    SECURITIES_FINANCIAL_REPORT = "securities_financial_report"
    COMPANY_CHARTER = "company_charter"


class MetadataPageType(str, Enum):
    TABLE_OF_CONTENTS = "table_of_contents"
    CONTENT = "content"


class DocumentMetadataPageInfo:

    def __init__(self, from_page: int = None, to_page: int = None, page_length: int = None):
        self.from_page = from_page
        self.to_page = to_page
        if page_length is None and from_page is not None and to_page is not None:
            self.page_length = to_page + 1 - from_page
        else:
            self.page_length = page_length


class DocumentMetadata:
    def __init__(self,
                 component_type: str,
                 page_info: DocumentMetadataPageInfo = None):
        self.component_type = component_type
        self.page_info = page_info
