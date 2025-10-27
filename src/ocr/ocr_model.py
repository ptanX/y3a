from enum import Enum


class DocumentType(str, Enum):
    BUSINESS_REGISTRATION = "business_registration"
    SECURITIES_FINANCIAL_REPORT = "securities_financial_report"
    COMPANY_CHARTER = "company_charter"
