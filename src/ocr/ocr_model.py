from enum import Enum
from typing import List, Dict
from pathlib import Path

EXTENSION_SPLITTER = "."
FILE_NAME_COMPONENT_SPLITTER = "-"


class DocumentType(str, Enum):
    BUSINESS_REGISTRATION = "business_registration"
    SECURITIES_FINANCIAL_REPORT = "securities_financial_report"
    COMPANY_CHARTER = "company_charter"


class MetadataPageType(str, Enum):
    TABLE_OF_CONTENTS = "table_of_contents"
    CONTENT = "content"


class DocumentIdentifierMetadata:

    def __init__(
        self,
        company: str,
        category: str,
        file_type: str,
        time: str = None,
        note: str = None,
    ):
        self.company = company
        self.category = category
        self.file_type = file_type
        self.time = time
        self.note = note


class DocumentPageInfoMetadata:

    def __init__(
        self, from_page: int = None, to_page: int = None, page_length: int = None
    ):
        self.from_page = from_page
        self.to_page = to_page
        if page_length is None and from_page is not None and to_page is not None:
            self.page_length = to_page + 1 - from_page
        else:
            self.page_length = page_length


class DocumentSectionMetadata:
    def __init__(self, component_type: str, page_info: DocumentPageInfoMetadata = None):
        self.component_type = component_type
        self.page_info = page_info


class DocumentMetadata:

    def __init__(
        self,
        document_type: str,
        document_identifier: DocumentIdentifierMetadata,
        document_path: str,
        sections: List[DocumentSectionMetadata] = None,
        other_info: Dict = None,
    ):
        self.document_type = document_type
        self.document_identifier = document_identifier
        self.sections = sections
        self.document_path = document_path
        self.other_info = other_info
