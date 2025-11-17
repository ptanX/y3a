DIMENSIONAL_MAPPING = {
    "capital_adequacy": {
        "fields": [
            {
                "display_name": "Nợ phải trả / Tổng tài sản",
                "field_path": "debt_ratio",
                "data_type": "Percentage",
                "show_difference": True
            },
            {
                "display_name": "Hệ số đòn bẩy (Tổng TS / VCSH)",
                "field_path": "leverage_ratio",
                "data_type": "Ratio",
                "show_difference": True
            },
            {
                "display_name": "Nợ dài hạn / VCSH",
                "field_path": "long_term_debt_to_equity",
                "data_type": "Percentage",
                "show_difference": True
            },
            {
                "display_name": "Nợ / VCSH",
                "field_path": "debt_to_equity",
                "data_type": "Ratio",
                "show_difference": True
            },
            {
                "display_name": "Tốc độ tăng trưởng tài sản",
                "field_path": "asset_growth_rate",
                "data_type": "Percentage",
                "show_difference": True
            }
        ]
    },
    "asset_quality": {
        "fields": [
            {
                "display_name": "Vòng quay các khoản phải thu",
                "field_path": "receivables_turnover",
                "data_type": "Times",
                "show_difference": True
            },
            {
                "display_name": "Vòng quay tài sản (ATO)",
                "field_path": "ato",
                "data_type": "Times",
                "show_difference": True
            },
            {
                "display_name": "Hiệu quả sử dụng TSCĐ",
                "field_path": "fixed_asset_turnover",
                "data_type": "Times",
                "show_difference": True
            }
        ]
    },
    "management_quality": {
        "fields": [
            {
                "display_name": "Chi phí bán hàng",
                "field_path": "income_statement.selling_expenses",
                "data_type": "VND",
                "show_difference": True
            },
            {
                "display_name": "Chi phí quản lý doanh nghiệp",
                "field_path": "income_statement.general_and_administrative_expenses",
                "data_type": "VND",
                "show_difference": True
            },
            {
                "display_name": "Tổng doanh thu hoạt động",
                "field_path": "income_statement.total_operating_revenue",
                "data_type": "VND",
                "show_difference": True
            },
            {
                "display_name": "Lợi nhuận hoạt động",
                "field_path": "income_statement.operating_profit",
                "data_type": "VND",
                "show_difference": True
            },
            {
                "display_name": "Tỷ suất LN hoạt động",
                "field_path": "operating_profit_margin",
                "data_type": "Percentage",
                "show_difference": True
            }
        ]
    },
    "earnings": {
        "fields": [
            {
                "display_name": "ROA (LN sau thuế / TS bình quân)",
                "field_path": "roa",
                "data_type": "Percentage",
                "show_difference": True
            },
            {
                "display_name": "ROE (LN sau thuế / VCSH bình quân)",
                "field_path": "roe",
                "data_type": "Percentage",
                "show_difference": True
            },
            {
                "display_name": "ROS (LN sau thuế / Doanh thu)",
                "field_path": "ros",
                "data_type": "Percentage",
                "show_difference": True
            },
            {
                "display_name": "EBIT",
                "field_path": "ebit",
                "data_type": "VND",
                "show_difference": True
            },
            {
                "display_name": "EBITDA",
                "field_path": "ebitda",
                "data_type": "VND",
                "show_difference": True
            },
            {
                "display_name": "Tỷ suất EBIT",
                "field_path": "ebit_margin",
                "data_type": "Percentage",
                "show_difference": True
            },
            {
                "display_name": "LN trước thuế",
                "field_path": "income_statement.accounting_profit_before_tax",
                "data_type": "VND",
                "show_difference": True
            },
            {
                "display_name": "LN sau thuế",
                "field_path": "income_statement.net_profit_after_tax",
                "data_type": "VND",
                "show_difference": True
            },
            {
                "display_name": "Tốc độ tăng trưởng LN",
                "field_path": "net_profit_growth_rate",
                "data_type": "Percentage",
                "show_difference": True
            }
        ]
    },
    "liquidity": {
        "fields": [
            {
                "display_name": "Khả năng thanh toán hiện hành",
                "field_path": "current_ratio",
                "data_type": "Ratio",
                "show_difference": True
            },
            {
                "display_name": "Khả năng thanh toán nhanh",
                "field_path": "quick_ratio",
                "data_type": "Ratio",
                "show_difference": True
            },
            {
                "display_name": "Khả năng thanh toán tức thời",
                "field_path": "cash_ratio",
                "data_type": "Ratio",
                "show_difference": True
            },
            {
                "display_name": "Vốn lưu động",
                "field_path": "working_capital",
                "data_type": "VND",
                "show_difference": True
            },
            {
                "display_name": "Tiền và tương đương tiền",
                "field_path": "financial_statement.cash_and_cash_equivalents",
                "data_type": "VND",
                "show_difference": True
            },
            {
                "display_name": "Tài sản ngắn hạn",
                "field_path": "financial_statement.short_term_assets",
                "data_type": "VND",
                "show_difference": True
            },
            {
                "display_name": "Nợ ngắn hạn",
                "field_path": "financial_statement.short_term_liabilities",
                "data_type": "VND",
                "show_difference": True
            }
        ]
    },
    "sensitivity": {
        "fields": [
            {
                "display_name": "Chi phí lãi vay",
                "field_path": "income_statement.interest_expense_on_borrowings",
                "data_type": "VND",
                "show_difference": True
            },
            {
                "display_name": "Khả năng thanh toán lãi vay (EBIT / Lãi vay)",
                "field_path": "interest_coverage_ratio",
                "data_type": "Ratio",
                "show_difference": True
            },
            {
                "display_name": "Vay ngắn hạn",
                "field_path": "financial_statement.short_term_borrowings_and_finance_lease_liabilities",
                "data_type": "VND",
                "show_difference": True
            },
            {
                "display_name": "Vay dài hạn",
                "field_path": "financial_statement.long_term_borrowings_and_finance_lease_liabilities",
                "data_type": "VND",
                "show_difference": True
            },
            {
                "display_name": "Tổng nợ phải trả",
                "field_path": "financial_statement.liabilities",
                "data_type": "VND",
                "show_difference": True
            }
        ]
    },
    "revenue_profit_table": {
        "fields": [
            {
                "display_name": "Doanh thu",
                "field_path": "income_statement.total_operating_revenue",
                "data_type": "VND"
            },
            {
                "display_name": "Lợi nhuận trước thuế",
                "field_path": "income_statement.accounting_profit_before_tax",
                "data_type": "VND"
            },
            {
                "display_name": "Lợi nhuận sau thuế",
                "field_path": "income_statement.net_profit_after_tax",
                "data_type": "VND"
            }
        ]
    },
    "financial_overview_table": {
        "fields": [
            {
                "display_name": "Tổng tài sản",
                "field_path": "financial_statement.total_assets",
                "data_type": "VND"
            },
            {
                "display_name": "(Khoản phải thu ngắn hạn)",
                "field_path": "financial_statement.receivables",
                "data_type": "VND"
            },
            {
                "display_name": "Tổng nợ phải trả",
                "field_path": "financial_statement.liabilities",
                "data_type": "VND"
            },
            {
                "display_name": "(Phải trả người bán)",
                "field_path": "financial_statement.short_term_trade_payables",
                "data_type": "VND"
            },
            {
                "display_name": "Vay và nợ thuê tài chính",
                "field_path": "financial_statement.short_term_borrowings_and_finance_lease_liabilities",
                "data_type": "VND"
            },
            {
                "display_name": "Vốn chủ sở hữu",
                "field_path": "financial_statement.owners_equity",
                "data_type": "VND"
            },
            {
                "display_name": "Doanh thu",
                "field_path": "income_statement.total_operating_revenue",
                "data_type": "VND"
            },
            {
                "display_name": "Chi phí bán hàng",
                "field_path": "income_statement.selling_expenses",
                "data_type": "VND"
            },
            {
                "display_name": "Chi phí quản lý doanh nghiệp",
                "field_path": "income_statement.general_and_administrative_expenses",
                "data_type": "VND"
            },
            {
                "display_name": "Lợi nhuận thuần từ hoạt động kinh doanh",
                "field_path": "income_statement.operating_profit",
                "data_type": "VND"
            },
            {
                "display_name": "Thu nhập khác",
                "field_path": "income_statement.other_income",
                "data_type": "VND"
            },
            {
                "display_name": "Chi phí khác",
                "field_path": "income_statement.other_expenses",
                "data_type": "VND"
            },
            {
                "display_name": "(Chi phí lãi vay)",
                "field_path": "income_statement.interest_expense_on_borrowings",
                "data_type": "VND"
            },
            {
                "display_name": "EBIT",
                "field_path": "calculated_metrics.ebit",
                "data_type": "VND"
            },
            {
                "display_name": "EBITDA",
                "field_path": "calculated_metrics.ebitda",
                "data_type": "VND"
            },
            {
                "display_name": "Lợi nhuận thuần",
                "field_path": "income_statement.net_profit_after_tax",
                "data_type": "VND"
            }
        ]
    },
    "liquidity_ratios_table": {
        "fields": [
            {
                "display_name": "Khả năng TT hiện hành",
                "field_path": "calculated_metrics.current_ratio",
                "data_type": "Ratio"
            },
            {
                "display_name": "Khả năng TT nhanh",
                "field_path": "calculated_metrics.quick_ratio",
                "data_type": "Ratio"
            },
            {
                "display_name": "Khả năng TT tức thời",
                "field_path": "calculated_metrics.cash_ratio",
                "data_type": "Ratio"
            }
        ]
    },
    "operational_efficiency_table": {
        "fields": [
            {
                "display_name": "Vòng quay các khoản phải thu",
                "field_path": "calculated_metrics.receivables_turnover",
                "data_type": "Times"
            },
            {
                "display_name": "Hiệu quả sử dụng TSCĐ",
                "field_path": "calculated_metrics.fixed_asset_turnover",
                "data_type": "Times"
            },
            {
                "display_name": "DT thuần trên TS BQ",
                "field_path": "calculated_metrics.ato",
                "data_type": "Times"
            }
        ]
    },
    "leverage_table": {
        "fields": [
            {
                "display_name": "Nợ phải trả trên Tổng TS",
                "field_path": "calculated_metrics.debt_ratio",
                "data_type": "Percentage"
            },
            {
                "display_name": "Nợ dài hạn trên VCSH",
                "field_path": "calculated_metrics.long_term_debt_to_equity",
                "data_type": "Percentage"
            },
            {
                "display_name": "Hệ số TSCĐ",
                "field_path": "calculated_metrics.leverage_ratio",
                "data_type": "Ratio"
            },
            {
                "display_name": "Tốc độ gia tăng TS",
                "field_path": "calculated_metrics.asset_growth_rate",
                "data_type": "Percentage"
            }
        ]
    },
    "profitability_table": {
        "fields": [
            {
                "display_name": "LN từ HĐKD trên DT thuần",
                "field_path": "calculated_metrics.operating_profit_margin",
                "data_type": "Percentage"
            },
            {
                "display_name": "LN sau thuế trên VCSHbq",
                "field_path": "calculated_metrics.roe",
                "data_type": "Percentage"
            },
            {
                "display_name": "LN sau thuế trên TSbq",
                "field_path": "calculated_metrics.roa",
                "data_type": "Percentage"
            },
            {
                "display_name": "EBIT/chi phí lãi vay",
                "field_path": "calculated_metrics.interest_coverage_ratio",
                "data_type": "Ratio"
            },
            {
                "display_name": "Tốc độ tăng trưởng LN sau thuế",
                "field_path": "calculated_metrics.net_profit_growth_rate",
                "data_type": "Percentage"
            }
        ]
    },
    "balance_sheet_horizontal": {
        "fields": [
            {
                "display_name": "A. TÀI SẢN NGẮN HẠN",
                "is_group_header": True
            },
            {
                "display_name": "I. Tài sản tài chính",
                "is_group_header": True
            },
            {
                "display_name": "1. Tiền và các khoản tương đương tiền",
                "field_path": "financial_statement.cash_and_cash_equivalents",
                "proportion_base": "financial_statement.short_term_assets",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "2. Các tài sản tài chính ghi nhận thông qua lãi/lỗ",
                "field_path": "financial_statement.financial_assets_at_fair_value_through_profit_or_loss",
                "proportion_base": "financial_statement.short_term_assets",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "3. Các khoản đầu tư nắm giữ đến ngày đáo hạn",
                "field_path": "financial_statement.held_to_maturity_investments",
                "proportion_base": "financial_statement.short_term_assets",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "4. Các khoản cho vay",
                "field_path": "financial_statement.loans",
                "proportion_base": "financial_statement.short_term_assets",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "5. Tài sản tài chính sẵn sàng để bán",
                "field_path": "financial_statement.available_for_sale_financial_assets",
                "proportion_base": "financial_statement.short_term_assets",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "7. Các khoản phải thu",
                "field_path": "financial_statement.receivables",
                "proportion_base": "financial_statement.short_term_assets",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "II. Tài sản ngắn hạn khác",
                "is_group_header": True
            },
            {
                "display_name": "7. Tài sản ngắn hạn khác",
                "field_path": "financial_statement.other_short_term_assets",
                "proportion_base": "financial_statement.short_term_assets",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "B. TÀI SẢN DÀI HẠN",
                "is_group_header": True
            },
            {
                "display_name": "I. Tài sản tài chính dài hạn",
                "is_group_header": True
            },
            {
                "display_name": "2. Các khoản đầu tư",
                "field_path": "financial_statement.investments",
                "proportion_base": "financial_statement.long_term_assets",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "II. Tài sản cố định",
                "is_group_header": True
            },
            {
                "display_name": "1. Tài sản cố định hữu hình",
                "field_path": "financial_statement.tangible_fixed_assets",
                "proportion_base": "financial_statement.long_term_assets",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "3. Tài sản cố định vô hình",
                "field_path": "financial_statement.intangible_fixed_assets",
                "proportion_base": "financial_statement.long_term_assets",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "III. Bất động sản đầu tư",
                "is_group_header": True
            },
            {
                "display_name": "Bất động sản đầu tư",
                "field_path": "financial_statement.investment_property",
                "proportion_base": "financial_statement.long_term_assets",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "V. Tài sản dài hạn khác",
                "is_group_header": True
            },
            {
                "display_name": "Tài sản dài hạn khác",
                "field_path": "financial_statement.other_long_term_assets",
                "proportion_base": "financial_statement.long_term_assets",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "C. NỢ PHẢI TRẢ",
                "is_group_header": True
            },
            {
                "display_name": "I. Nợ phải trả ngắn hạn",
                "is_group_header": True
            },
            {
                "display_name": "1. Vay và nợ thuê tài chính ngắn hạn",
                "field_path": "financial_statement.short_term_borrowings_and_finance_lease_liabilities",
                "proportion_base": "financial_statement.liabilities",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "4. Trái phiếu phát hành ngắn hạn",
                "field_path": "financial_statement.short_term_bonds_issued",
                "proportion_base": "financial_statement.liabilities",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "6. Phải trả hoạt động giao dịch chứng khoán",
                "field_path": "financial_statement.payables_from_securities_trading_activities",
                "proportion_base": "financial_statement.liabilities",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "8. Phải trả người bán ngắn hạn",
                "field_path": "financial_statement.short_term_trade_payables",
                "proportion_base": "financial_statement.liabilities",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "10. Thuế và các khoản phải nộp Nhà nước",
                "field_path": "financial_statement.taxes_and_other_payables_to_the_state",
                "proportion_base": "financial_statement.liabilities",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "17. Các khoản phải trả khác ngắn hạn",
                "field_path": "financial_statement.other_short_term_payables",
                "proportion_base": "financial_statement.liabilities",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "II. Nợ phải trả dài hạn",
                "is_group_header": True
            },
            {
                "display_name": "1. Vay và nợ thuê tài chính dài hạn",
                "field_path": "financial_statement.long_term_borrowings_and_finance_lease_liabilities",
                "proportion_base": "financial_statement.liabilities",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "4. Trái phiếu phát hành dài hạn",
                "field_path": "financial_statement.long_term_bonds_issued",
                "proportion_base": "financial_statement.liabilities",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "14. Thuế thu nhập hoãn lại phải trả",
                "field_path": "financial_statement.deferred_tax_liabilities",
                "proportion_base": "financial_statement.liabilities",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "11. Các khoản phải trả khác dài hạn",
                "field_path": "financial_statement.other_long_term_payables",
                "proportion_base": "financial_statement.liabilities",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "VỐN CHỦ SỞ HỮU",
                "is_group_header": True
            },
            {
                "display_name": "I. Vốn chủ sở hữu",
                "is_group_header": True
            },
            {
                "display_name": "1. Vốn đầu tư của chủ sở hữu",
                "field_path": "financial_statement.capital",
                "proportion_base": "financial_statement.owners_equity",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "2. Thặng dư vốn cổ phần",
                "field_path": "financial_statement.share_premium",
                "proportion_base": "financial_statement.owners_equity",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "3. Cổ phiếu quỹ",
                "field_path": "financial_statement.treasury_shares",
                "proportion_base": "financial_statement.owners_equity",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "5. Quỹ dự phòng tài chính và rủi ro nghiệp vụ",
                "field_path": "financial_statement.financial_reserve_and_business_risk_fund",
                "proportion_base": "financial_statement.owners_equity",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "7. Lợi nhuận chưa phân phối",
                "field_path": "financial_statement.retained_earnings",
                "proportion_base": "financial_statement.owners_equity",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "TỔNG CỘNG VỐN CHỦ SỞ HỮU",
                "field_path": "financial_statement.owners_equity",
                "is_bold": True,
                "is_total_row": True,
                "show_difference": True
            },
            {
                "display_name": "TỔNG CỘNG NỢ PHẢI TRẢ VÀ VỐN CHỦ SỞ HỮU",
                "field_path": "financial_statement.total_assets",
                "is_bold": True,
                "is_total_row": True,
                "show_difference": True
            }
        ]
    },
    "income_statement_horizontal": {
        "fields": [
            {
                "display_name": "I. DOANH THU HOẠT ĐỘNG",
                "is_group_header": True
            },
            {
                "display_name": "1.1. Lãi từ các tài sản tài chính ghi nhận thông qua lãi/lỗ (FVTPL)",
                "field_path": "income_statement.interest_income_from_financial_assets_recognized_through_p_and_l",
                "proportion_base": "income_statement.total_operating_revenue",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "1.2. Lãi từ các khoản đầu tư nắm giữ đến ngày đáo hạn (HTM)",
                "field_path": "income_statement.interest_income_from_held_to_maturity_investments",
                "proportion_base": "income_statement.total_operating_revenue",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "1.3. Lãi từ các khoản cho vay và phải thu",
                "field_path": "income_statement.interest_income_from_loans_and_receivables",
                "proportion_base": "income_statement.total_operating_revenue",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "1.4. Lãi từ tài sản tài chính sẵn sàng để bán (AFS)",
                "field_path": "income_statement.interest_income_from_available_for_sale_financial_assets",
                "proportion_base": "income_statement.total_operating_revenue",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "1.6. Doanh thu nghiệp vụ môi giới chứng khoán",
                "field_path": "income_statement.brokerage_revenue",
                "proportion_base": "income_statement.total_operating_revenue",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "1.7. Doanh thu nghiệp vụ bảo lãnh, đại lý phát hành chứng khoán",
                "field_path": "income_statement.underwriting_revenue",
                "proportion_base": "income_statement.total_operating_revenue",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "1.8. Doanh thu nghiệp vụ tư vấn đầu tư chứng khoán",
                "field_path": "income_statement.investment_advisory_revenue",
                "proportion_base": "income_statement.total_operating_revenue",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "1.9. Doanh thu nghiệp vụ lưu ký chứng khoán",
                "field_path": "income_statement.securities_custody_revenue",
                "proportion_base": "income_statement.total_operating_revenue",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "1.10. Doanh thu hoạt động tư vấn tài chính",
                "field_path": "income_statement.financial_advisory_revenue",
                "proportion_base": "income_statement.total_operating_revenue",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "1.11. Thu nhập hoạt động khác",
                "field_path": "income_statement.other_operating_income",
                "proportion_base": "income_statement.total_operating_revenue",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "II. CHI PHÍ HOẠT ĐỘNG",
                "is_group_header": True
            },
            {
                "display_name": "2.1. Lỗ các tài sản tài chính ghi nhận thông qua lãi/lỗ (FVTPL)",
                "field_path": "income_statement.interest_expense_on_financial_assets_recognized_through_p_and_l",
                "proportion_base": "income_statement.total_operating_expenses",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "2.4. Chi phí dự phòng tài sản tài chính",
                "field_path": "income_statement.provisions_for_impairment_of_financial_assets",
                "proportion_base": "income_statement.total_operating_expenses",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "2.7. Chi phí nghiệp vụ môi giới chứng khoán",
                "field_path": "income_statement.brokerage_fees",
                "proportion_base": "income_statement.total_operating_expenses",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "2.8. Chi phí nghiệp vụ bảo lãnh",
                "field_path": "income_statement.underwriting_and_bond_issuance_costs",
                "proportion_base": "income_statement.total_operating_expenses",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "2.9. Chi phí nghiệp vụ tư vấn đầu tư chứng khoán",
                "field_path": "income_statement.investment_advisory_expenses",
                "proportion_base": "income_statement.total_operating_expenses",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "2.10. Chi phí nghiệp vụ lưu ký chứng khoán",
                "field_path": "income_statement.securities_custody_expenses",
                "proportion_base": "income_statement.total_operating_expenses",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "2.11. Chi phí hoạt động tư vấn tài chính",
                "field_path": "income_statement.financial_advisory_expenses",
                "proportion_base": "income_statement.total_operating_expenses",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "2.12. Chi phí các dịch vụ khác",
                "field_path": "income_statement.other_operating_expenses",
                "proportion_base": "income_statement.total_operating_expenses",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "III. DOANH THU HOẠT ĐỘNG TÀI CHÍNH",
                "is_group_header": True
            },
            {
                "display_name": "3.2. Lãi tiền gửi ngân hàng",
                "field_path": "income_statement.interest_income_from_deposits",
                "proportion_base": "income_statement.total_financial_operating_revenue",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "3.1. Chênh lệch lãi tỷ giá",
                "field_path": "income_statement.increase_decrease_in_fair_value_of_exchange_rate_and_unrealized",
                "proportion_base": "income_statement.total_financial_operating_revenue",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "3.3. Lãi bán, thanh lý đầu tư",
                "field_path": "income_statement.gain_on_disposal_of_investments_in_subsidiaries_associates_and_joint_ventures",
                "proportion_base": "income_statement.total_financial_operating_revenue",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "3.4. Doanh thu khác về đầu tư",
                "field_path": "income_statement.other_investment_income",
                "proportion_base": "income_statement.total_financial_operating_revenue",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "IV. CHI PHÍ TÀI CHÍNH",
                "is_group_header": True
            },
            {
                "display_name": "4.2. Chi phí lãi vay",
                "field_path": "income_statement.interest_expense_on_borrowings",
                "proportion_base": "income_statement.total_financial_expenses",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "4.1. Chênh lệch lỗ tỷ giá",
                "field_path": "income_statement.increase_decrease_in_fair_value_of_exchange_rate_loss",
                "proportion_base": "income_statement.total_financial_expenses",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "4.3. Lỗ bán, thanh lý đầu tư",
                "field_path": "income_statement.loss_on_disposal_of_investments_in_subsidiaries_associates_and_joint_ventures",
                "proportion_base": "income_statement.total_financial_expenses",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "4.4. Chi phí dự phòng đầu tư dài hạn",
                "field_path": "income_statement.provision_for_impairment_of_long_term_financial_investments",
                "proportion_base": "income_statement.total_financial_expenses",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "4.5. Chi phí tài chính khác",
                "field_path": "income_statement.other_financial_expenses",
                "proportion_base": "income_statement.total_financial_expenses",
                "show_proportion": True,
                "show_difference": True
            },
            {
                "display_name": "V. CHI PHÍ BÁN HÀNG",
                "is_group_header": True
            },
            {
                "display_name": "Chi phí bán hàng",
                "field_path": "income_statement.selling_expenses",
                "show_difference": True
            },
            {
                "display_name": "VI. CHI PHÍ QUẢN LÝ CÔNG TY CHỨNG KHOÁN",
                "is_group_header": True
            },
            {
                "display_name": "Chi phí quản lý doanh nghiệp",
                "field_path": "income_statement.general_and_administrative_expenses",
                "show_difference": True
            },
            {
                "display_name": "VII. KẾT QUẢ HOẠT ĐỘNG",
                "is_group_header": True
            },
            {
                "display_name": "Lợi nhuận thuần từ hoạt động kinh doanh",
                "field_path": "income_statement.operating_profit",
                "is_bold": True,
                "show_difference": True
            },
            {
                "display_name": "VIII. THU NHẬP KHÁC VÀ CHI PHÍ KHÁC",
                "is_group_header": True
            },
            {
                "display_name": "8.1. Thu nhập khác",
                "field_path": "income_statement.other_income",
                "show_difference": True
            },
            {
                "display_name": "8.2. Chi phí khác",
                "field_path": "income_statement.other_expenses",
                "show_difference": True
            },
            {
                "display_name": "IX. TỔNG LỢI NHUẬN KẾ TOÁN TRƯỚC THUẾ",
                "is_group_header": True
            },
            {
                "display_name": "Tổng lợi nhuận kế toán trước thuế",
                "field_path": "income_statement.accounting_profit_before_tax",
                "is_bold": True,
                "show_difference": True
            },
            {
                "display_name": "9.1. Lợi nhuận đã thực hiện",
                "field_path": "income_statement.realized_profit",
                "show_difference": True
            },
            {
                "display_name": "9.2. Lợi nhuận chưa thực hiện",
                "field_path": "income_statement.unrealized_profit_loss",
                "show_difference": True
            },
            {
                "display_name": "X. CHI PHÍ THUẾ TNDN",
                "is_group_header": True
            },
            {
                "display_name": "Chi phí thuế thu nhập doanh nghiệp",
                "field_path": "income_statement.total_corporate_income_tax",
                "show_difference": True
            },
            {
                "display_name": "XI. LỢI NHUẬN SAU THUẾ",
                "is_group_header": True
            },
            {
                "display_name": "Lợi nhuận kế toán sau thuế TNDN",
                "field_path": "income_statement.net_profit_after_tax",
                "is_bold": True,
                "show_difference": True
            }
        ]
    }
}
