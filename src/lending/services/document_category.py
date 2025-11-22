LEGAL_DOCS = [
    {
        "name": "business_registration_cert",
        "description": "Giấy chứng nhận đăng ký doanh nghiệp",
        "required": True,
    },
    {
        "name": "company_charter",
        "description": "Điều lệ doanh nghiệp",
        "required": True,
    },
    {
        "name": "investment_business_license",
        "description": "Giấy phép hành nghề đối với ngành nghề đầu tư kinh doanh",
        "required": True,
    },
    {
        "name": "appointment_document",
        "description": "Quyết định bổ nhiệm",
        "required": True,
    },
    {
        "name": "legal_rep_auth_document",
        "description": "Quyết định/Văn bản ủy quyền thường xuyên/từng lần của Người đại diện theo pháp luật của doanh nghiệp",
        "required": True,
    },
    {
        "name": "branch_registration_cert",
        "description": "Giấy chứng nhận phần vốn góp",
        "required": True,
    },
    {
        "name": "signature_sample_notice",
        "description": "Thông báo mẫu chữ ký của người đại diện pháp luật",
        "required": True,
    },
    {
        "name": "legal_rep_personal_docs",
        "description": "Giấy tờ pháp lý của cá nhân của Người đại diện theo pháp luật",
        "required": True,
    },
]

# Category II: Financial Documents
FINANCIAL_DOCS = [
    {
        "name": "financial_report",
        "description": "Báo cáo tài chính năm",
        "required": True,
    },
    {
        "name": "bank_statements",
        "description": "Sao kê tài khoản tại các TCTD",
        "required": True,
    },
    {
        "name": "economic_contract",
        "description": "Hợp đồng kinh tế đầu vào, đầu ra",
        "required": True,
    },
]

COLLATERAL_DOCS = [
    {
        "name": "land_use_cert",
        "description": "Giấy chứng nhận quyền sử dụng đất, sở hữu nhà",
        "required": False,
    },
    {
        "name": "vehicle_registration",
        "description": "Giấy đăng ký xe",
        "required": False,
    },
    {"name": "savings_book", "description": "Sổ tiết kiệm", "required": False},
]


def process_document_categories(document_categories):
    def get_quantity(doc_name):
        """Get quantity for a document, checking multiple variations."""
        if doc_name in document_categories:
            return document_categories[doc_name]
        return 0

    def process_category(docs, category_name, category_description):
        """Process a category of documents."""
        processed_docs = []

        for doc in docs:
            quantity = get_quantity(doc["name"])
            processed_docs.append(
                {
                    "name": doc["name"],
                    "description": doc["description"],
                    "quantity": quantity,
                }
            )

        return {
            "name": category_name,
            "description": category_description,
            "documents": processed_docs,
        }

    # Process each category
    result = [
        process_category(LEGAL_DOCS, "legal_docs", "Hồ sơ pháp lý"),
        process_category(FINANCIAL_DOCS, "financial_docs", "Hồ sơ tài chính"),
        process_category(
            COLLATERAL_DOCS, "collateral_docs", "Hồ sơ tài sản bảo đảm (TSBD)"
        ),
    ]

    # Find missing required documents
    missing_docs = []
    all_docs = LEGAL_DOCS + FINANCIAL_DOCS + COLLATERAL_DOCS

    for doc in all_docs:
        if doc.get("required", False):
            quantity = get_quantity(doc["name"])
            if quantity == 0:
                missing_docs.append(
                    {
                        "name": doc["name"],
                        "description": doc["description"],
                        "quantity": "-",
                    }
                )

    if missing_docs:
        result.append(
            {
                "name": "missing_required_docs",
                "description": "Cần bổ sung",
                "documents": missing_docs,
            }
        )

    return result
