REQUIRED_EXTRACTION_FIELDS = [
    "company_name_vn",
    "company_name_en",
    "company_abbr",
    "office_address",
    "phone",
    "charter_capital",
    "par_value",
    "total_shares",
    "email",
    "legal_rep",
    "business_code"
]

REQUIRED_FIELDS = {
    # Company Information
    "company_name_vn",
    "company_name_en",
    "company_abbr",
    "office_address",
    "phone",
    "charter_capital",
    "par_value",
    "total_shares",
    "email",
    "legal_rep",
    "business_code",

    # Balance Sheet - Assets
    "short_term_assets",
    "current_financial_assets",  # "Tài sản tài chính" under short-term
    "other_short_term_assets",
    "long_term_assets",
    "long_term_financial_assets",
    "fixed_assets",
    "investment_property",
    "construction_in_progress",
    "other_long_term_assets",
    "provision_long_term_assets",
    "total_assets",

    # Balance Sheet - Liabilities & Equity
    "liabilities",  # "NỢ PHẢI TRẢ"
    "short_term_liabilities",
    "long_term_liabilities",
    "owners_equity",
    "owners_capital",
    "funds_and_reserves",
    "total_liabilities_and_owners_equity",

    # Income Statement
    "selling_expenses",
    "general_and_administrative_expenses",
    "profit_from_operating_activities",
    "total_profit_before_tax",
    "total_corporate_income_tax",
    "net_profit_after_tax",
    "total_comprehensive_income",

    # Cash Flow Statement
    "cash_flow_operating",
    "cash_flow_investing",
    "cash_flow_financing",
    "net_cash_change",
    "cash_beginning",
    "cash_ending"
}
