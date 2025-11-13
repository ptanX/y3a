basic_mapping_tables = """
{
  "query_type_mappings": {
    "revenue_profit_table": {
      "description": "Bảng phân tích doanh thu và lợi nhuận",
      "sections": [
        {
          "section_name": "Doanh thu và Lợi nhuận",
          "fields": [
            {
              "display_name": "Doanh thu",
              "field_path": "data.income_statement.operating_revenue.total_operating_revenue",
              "data_type": "VND"
            },
            {
              "display_name": "Giá vốn hàng bán",
              "field_path": "data.income_statement.operating_expenses.cost_of_goods_sold",
              "data_type": "VND",
              "note": "Thường null cho công ty chứng khoán"
            },
            {
              "display_name": "Lợi nhuận trước thuế",
              "field_path": "data.income_statement.profit_and_tax.profit_before_tax",
              "data_type": "VND"
            },
            {
              "display_name": "Lợi nhuận sau thuế",
              "field_path": "data.income_statement.profit_and_tax.net_profit_after_tax",
              "data_type": "VND"
            }
          ]
        }
      ]
    },
    "financial_overview_table": {
      "description": "Bảng tình hình tài chính cơ bản",
      "sections": [
        {
          "section_name": "I. Khoản mục chính",
          "fields": [
            {
              "display_name": "Tổng tài sản",
              "field_path": "data.balance_sheet.totals.total_assets",
              "data_type": "VND"
            },
            {
              "display_name": "(Khoản phải thu ngắn hạn)",
              "field_path": "data.balance_sheet.short_term_assets.receivables",
              "data_type": "VND"
            },
            {
              "display_name": "(Hàng tồn kho)",
              "field_path": "data.balance_sheet.short_term_assets.inventory",
              "data_type": "VND",
              "note": "Thường null cho công ty CK"
            },
            {
              "display_name": "Tổng nợ phải trả",
              "field_path": "data.balance_sheet.totals.total_liabilities",
              "data_type": "VND"
            },
            {
              "display_name": "(Phải trả người bán)",
              "field_path": "data.balance_sheet.short_term_liabilities.trade_payables",
              "data_type": "VND"
            },
            {
              "display_name": "Vay và nợ thuê tài chính",
              "field_path": "data.balance_sheet.short_term_liabilities.short_term_borrowings",
              "data_type": "VND"
            },
            {
              "display_name": "Vốn chủ sở hữu",
              "field_path": "data.balance_sheet.equity.total_equity",
              "data_type": "VND"
            },
            {
              "display_name": "Doanh thu",
              "field_path": "data.income_statement.operating_revenue.total_operating_revenue",
              "data_type": "VND"
            },
            {
              "display_name": "Giá vốn hàng bán",
              "field_path": "data.income_statement.operating_expenses.cost_of_goods_sold",
              "data_type": "VND",
              "note": "Thường null cho công ty CK"
            },
            {
              "display_name": "Chi phí bán hàng",
              "field_path": "data.income_statement.administrative_expenses.selling_expenses",
              "data_type": "VND"
            },
            {
              "display_name": "Chi phí quản lý doanh nghiệp",
              "field_path": "data.income_statement.administrative_expenses.general_admin_expenses",
              "data_type": "VND"
            },
            {
              "display_name": "Lợi nhuận thuần từ hoạt động kinh doanh",
              "field_path": "data.income_statement.profit_and_tax.operating_profit",
              "data_type": "VND"
            },
            {
              "display_name": "Thu nhập khác",
              "field_path": "data.income_statement.profit_and_tax.other_income",
              "data_type": "VND"
            },
            {
              "display_name": "Chi phí khác",
              "field_path": "data.income_statement.profit_and_tax.other_expenses",
              "data_type": "VND"
            },
            {
              "display_name": "(Chi phí lãi vay)",
              "field_path": "data.income_statement.financial_income_expenses.interest_expense_borrowings",
              "data_type": "VND"
            },
            {
              "display_name": "EBIT",
              "field_path": "data.metrics.earnings.profit_metrics.ebit",
              "data_type": "VND"
            },
            {
              "display_name": "EBITDA",
              "field_path": "data.metrics.earnings.profit_metrics.ebitda",
              "data_type": "VND"
            },
            {
              "display_name": "Lợi nhuận thuần",
              "field_path": "data.income_statement.profit_and_tax.net_profit_after_tax",
              "data_type": "VND"
            },
            {
              "display_name": "Dòng tiền ròng từ hoạt động kinh doanh",
              "field_path": "data.cashflow.operating_cashflow.net_operating_cashflow",
              "data_type": "VND"
            },
            {
              "display_name": "Dòng tiền ròng từ hoạt động đầu tư",
              "field_path": "data.cashflow.investing_cashflow.net_investing_cashflow",
              "data_type": "VND"
            },
            {
              "display_name": "Dòng tiền ròng từ hoạt động tài chính",
              "field_path": "data.cashflow.financing_cashflow.net_financing_cashflow",
              "data_type": "VND"
            }
          ]
        }
      ]
    },
    "liquidity_ratios_table": {
      "description": "Bảng chỉ số thanh khoản",
      "sections": [
        {
          "section_name": "1. Chỉ tiêu thanh khoản",
          "fields": [
            {
              "display_name": "Khả năng TT hiện hành",
              "field_path": "data.metrics.liquidity.liquidity_ratios.current_ratio",
              "data_type": "Ratio"
            },
            {
              "display_name": "Khả năng TT nhanh",
              "field_path": "data.metrics.liquidity.liquidity_ratios.quick_ratio",
              "data_type": "Ratio"
            },
            {
              "display_name": "Khả năng TT tức thời",
              "field_path": "data.metrics.liquidity.liquidity_ratios.cash_ratio",
              "data_type": "Ratio"
            }
          ]
        }
      ]
    },
    "operational_efficiency_table": {
      "description": "Bảng hiệu quả hoạt động",
      "sections": [
        {
          "section_name": "2. Chỉ tiêu hoạt động",
          "fields": [
            {
              "display_name": "Vòng quay VLĐ",
              "field_path": "data.metrics.asset_quality.turnover_metrics.working_capital_turnover",
              "data_type": "Times"
            },
            {
              "display_name": "Vòng quay Hàng tồn kho",
              "field_path": "data.metrics.asset_quality.turnover_metrics.inventory_turnover",
              "note": "Thường null cho công ty CK"
            },
            {
              "display_name": "Vòng quay các khoản phải thu",
              "field_path": "data.metrics.asset_quality.turnover_metrics.receivables_turnover",
              "data_type": "Times"
            },
            {
              "display_name": "Hiệu quả sử dụng TSCĐ",
              "field_path": "data.metrics.management_quality.operational_efficiency.fixed_asset_turnover",
              "data_type": "Times"
            },
            {
              "display_name": "DT thuần trên TS BQ",
              "field_path": "data.metrics.asset_quality.turnover_metrics.asset_turnover",
              "data_type": "Times"
            }
          ]
        }
      ]
    },
    "leverage_table": {
      "description": "Bảng cân nợ và cơ cấu vốn",
      "sections": [
        {
          "section_name": "3. Chỉ tiêu cân nợ và cơ cấu vốn",
          "fields": [
            {
              "display_name": "Nợ phải trả trên Tổng TS",
              "field_path": "data.metrics.capital_adequacy.debt_management.debt_ratio",
              "data_type": "Percentage"
            },
            {
              "display_name": "Nợ dài hạn trên VCSH",
              "field_path": "data.metrics.capital_adequacy.debt_management.long_term_debt_to_equity",
              "data_type": "Percentage"
            },
            {
              "display_name": "Hệ số TSCĐ",
              "field_path": "data.metrics.capital_adequacy.debt_management.leverage_ratio",
              "data_type": "Ratio"
            },
            {
              "display_name": "Tốc độ gia tăng TS",
              "field_path": "data.metrics.capital_adequacy.growth_metrics.asset_growth_rate",
              "data_type": "Percentage"
            }
          ]
        }
      ]
    },
    "profitability_table": {
      "description": "Bảng thu nhập và sinh lời",
      "sections": [
        {
          "section_name": "4. Chỉ tiêu thu nhập",
          "fields": [
            {
              "display_name": "LN gộp trên Dthu",
              "field_path": "data.metrics.earnings.profitability_ratios.gross_profit_margin",
              "data_type": "Percentage",
              "note": "Thường null cho công ty CK"
            },
            {
              "display_name": "LN từ HĐKD trên DT thuần",
              "field_path": "data.metrics.earnings.profitability_ratios.operating_profit_margin",
              "data_type": "Percentage"
            },
            {
              "display_name": "LN sau thuế trên VCSHbq",
              "field_path": "data.metrics.earnings.profitability_ratios.roe",
              "data_type": "Percentage"
            },
            {
              "display_name": "LN sau thuế trên TSbq",
              "field_path": "data.metrics.earnings.profitability_ratios.roa",
              "data_type": "Percentage"
            },
            {
              "display_name": "EBIT/chi phí lãi vay",
              "field_path": "data.metrics.capital_adequacy.debt_management.interest_coverage_ratio",
              "data_type": "Ratio"
            },
            {
              "display_name": "Tốc độ tăng trưởng LN sau thuế",
              "field_path": "data.metrics.earnings.growth_metrics.net_profit_growth_rate",
              "data_type": "Percentage"
            }
          ]
        }
      ]
    },
    "cashflow_table": {
      "description": "Bảng lưu chuyển tiền tệ",
      "sections": [
        {
          "section_name": "Lưu chuyển tiền tệ",
          "fields": [
            {
              "display_name": "Lưu chuyển tiền thuần từ hoạt động kinh doanh",
              "field_path": "data.cashflow.operating_cashflow.net_operating_cashflow",
              "data_type": "VND"
            },
            {
              "display_name": "Lưu chuyển tiền thuần từ hoạt động đầu tư",
              "field_path": "data.cashflow.investing_cashflow.net_investing_cashflow",
              "data_type": "VND"
            },
            {
              "display_name": "Lưu chuyển tiền thuần từ hoạt động tài chính",
              "field_path": "data.cashflow.financing_cashflow.net_financing_cashflow",
              "data_type": "VND"
            },
            {
              "stt": null,
              "display_name": "Lưu chuyển tiền thuần trong năm",
              "field_path": "data.cashflow.net_cashflow.net_change_in_cash",
              "data_type": "VND"
            }
          ]
        }
      ]
    }
  }
}
"""

horizontal_comparison_mapping_tables = """
{
  "query_type_mappings": {
    "balance_sheet_horizontal": {
      "description": "Bảng cân đối kế toán so sánh ngang",
      "sections": [
        {
          "section_name": "A. TÀI SẢN NGẮN HẠN",
          "fields": [
            {
              "display_name": "I. Tài sản tài chính",
              "field_path": "data.balance_sheet.short_term_assets.total_short_term_assets",
              "is_group_header": true
            },
            {
              "display_name": "1. Tiền và các khoản tương đương tiền",
              "field_path": "data.balance_sheet.short_term_assets.cash_and_equivalents",
              "proportion_base": "data.balance_sheet.short_term_assets.total_short_term_assets",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "2. Các tài sản tài chính ghi nhận thông qua lãi/lỗ",
              "field_path": "data.balance_sheet.short_term_assets.financial_assets_fvtpl",
              "proportion_base": "data.balance_sheet.short_term_assets.total_short_term_assets",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "3. Các khoản đầu tư nắm giữ đến ngày đáo hạn",
              "field_path": "data.balance_sheet.short_term_assets.held_to_maturity_investments",
              "proportion_base": "data.balance_sheet.short_term_assets.total_short_term_assets",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "4. Các khoản cho vay",
              "field_path": "data.balance_sheet.short_term_assets.loans",
              "proportion_base": "data.balance_sheet.short_term_assets.total_short_term_assets",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "5. Tài sản tài chính sẵn sàng để bán",
              "field_path": "data.balance_sheet.short_term_assets.available_for_sale_assets",
              "proportion_base": "data.balance_sheet.short_term_assets.total_short_term_assets",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "7. Các khoản phải thu",
              "field_path": "data.balance_sheet.short_term_assets.receivables",
              "proportion_base": "data.balance_sheet.short_term_assets.total_short_term_assets",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "II. Tài sản ngắn hạn khác",
              "is_group_header": true
            },
            {
              "display_name": "7. Tài sản ngắn hạn khác",
              "field_path": "data.balance_sheet.short_term_assets.other_short_term_assets",
              "proportion_base": "data.balance_sheet.short_term_assets.total_short_term_assets",
              "show_proportion": true,
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "B. TÀI SẢN DÀI HẠN",
          "fields": [
            {
              "display_name": "I. Tài sản tài chính dài hạn",
              "is_group_header": true
            },
            {
              "display_name": "2. Các khoản đầu tư",
              "field_path": "data.balance_sheet.long_term_assets.long_term_financial_assets",
              "proportion_base": "data.balance_sheet.long_term_assets.total_long_term_assets",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "II. Tài sản cố định",
              "is_group_header": true
            },
            {
              "display_name": "1. Tài sản cố định hữu hình",
              "field_path": "data.balance_sheet.long_term_assets.tangible_fixed_assets",
              "proportion_base": "data.balance_sheet.long_term_assets.total_long_term_assets",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "3. Tài sản cố định vô hình",
              "field_path": "data.balance_sheet.long_term_assets.intangible_fixed_assets",
              "proportion_base": "data.balance_sheet.long_term_assets.total_long_term_assets",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "III. Bất động sản đầu tư",
              "is_group_header": true
            },
            {
              "display_name": "Bất động sản đầu tư",
              "field_path": "data.balance_sheet.long_term_assets.investment_property",
              "proportion_base": "data.balance_sheet.long_term_assets.total_long_term_assets",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "V. Tài sản dài hạn khác",
              "is_group_header": true
            },
            {
              "display_name": "Tài sản dài hạn khác",
              "field_path": "data.balance_sheet.long_term_assets.other_long_term_assets",
              "proportion_base": "data.balance_sheet.long_term_assets.total_long_term_assets",
              "show_proportion": true,
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "TỔNG CỘNG TÀI SẢN",
          "fields": [
            {
              "display_name": "TỔNG CỘNG TÀI SẢN",
              "field_path": "data.balance_sheet.totals.total_assets",
              "is_bold": true,
              "is_total_row": true,
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "C. NỢ PHẢI TRẢ",
          "fields": [
            {
              "display_name": "I. Nợ phải trả ngắn hạn",
              "field_path": "data.balance_sheet.totals.total_liabilities",
              "is_group_header": true
            },
            {
              "display_name": "1. Vay và nợ thuê tài chính ngắn hạn",
              "field_path": "data.balance_sheet.short_term_liabilities.short_term_borrowings",
              "proportion_base": "data.balance_sheet.totals.total_liabilities",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "4. Trái phiếu phát hành ngắn hạn",
              "field_path": "data.balance_sheet.short_term_liabilities.short_term_bonds",
              "proportion_base": "data.balance_sheet.totals.total_liabilities",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "6. Phải trả hoạt động giao dịch chứng khoán",
              "field_path": "data.balance_sheet.short_term_liabilities.payables_from_securities_trading",
              "proportion_base": "data.balance_sheet.totals.total_liabilities",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "8. Phải trả người bán ngắn hạn",
              "field_path": "data.balance_sheet.short_term_liabilities.trade_payables",
              "proportion_base": "data.balance_sheet.totals.total_liabilities",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "10. Thuế và các khoản phải nộp Nhà nước",
              "field_path": "data.balance_sheet.short_term_liabilities.taxes_payable",
              "proportion_base": "data.balance_sheet.totals.total_liabilities",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "17. Các khoản phải trả khác ngắn hạn",
              "field_path": "data.balance_sheet.short_term_liabilities.other_short_term_payables",
              "proportion_base": "data.balance_sheet.totals.total_liabilities",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "II. Nợ phải trả dài hạn",
              "is_group_header": true
            },
            {
              "display_name": "1. Vay và nợ thuê tài chính dài hạn",
              "field_path": "data.balance_sheet.long_term_liabilities.long_term_borrowings",
              "proportion_base": "data.balance_sheet.totals.total_liabilities",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "4. Trái phiếu phát hành dài hạn",
              "field_path": "data.balance_sheet.long_term_liabilities.long_term_bonds",
              "proportion_base": "data.balance_sheet.totals.total_liabilities",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "14. Thuế thu nhập hoãn lại phải trả",
              "field_path": "data.balance_sheet.long_term_liabilities.deferred_tax_liabilities",
              "proportion_base": "data.balance_sheet.totals.total_liabilities",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "11. Các khoản phải trả khác dài hạn",
              "field_path": "data.balance_sheet.long_term_liabilities.other_long_term_payables",
              "proportion_base": "data.balance_sheet.totals.total_liabilities",
              "show_proportion": true,
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "VỐN CHỦ SỞ HỮU",
          "fields": [
            {
              "display_name": "I. Vốn chủ sở hữu",
              "field_path": "data.balance_sheet.equity.total_equity",
              "is_group_header": true
            },
            {
              "display_name": "1. Vốn đầu tư của chủ sở hữu",
              "field_path": "data.balance_sheet.equity.share_capital",
              "proportion_base": "data.balance_sheet.equity.total_equity",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "2. Thặng dư vốn cổ phần",
              "field_path": "data.balance_sheet.equity.share_premium",
              "proportion_base": "data.balance_sheet.equity.total_equity",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "3. Cổ phiếu quỹ",
              "field_path": "data.balance_sheet.equity.treasury_shares",
              "proportion_base": "data.balance_sheet.equity.total_equity",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "5. Quỹ dự phòng tài chính và rủi ro nghiệp vụ",
              "field_path": "data.balance_sheet.equity.reserves",
              "proportion_base": "data.balance_sheet.equity.total_equity",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "7. Lợi nhuận chưa phân phối",
              "field_path": "data.balance_sheet.equity.retained_earnings",
              "proportion_base": "data.balance_sheet.equity.total_equity",
              "show_proportion": true,
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "TỔNG CỘNG VỐN CHỦ SỞ HỮU",
          "fields": [
            {
              "display_name": "TỔNG CỘNG VỐN CHỦ SỞ HỮU",
              "field_path": "data.balance_sheet.equity.total_equity",
              "is_bold": true,
              "is_total_row": true,
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "TỔNG CỘNG NỢ PHẢI TRẢ VÀ VỐN CHỦ SỞ HỮU",
          "fields": [
            {
              "display_name": "TỔNG CỘNG NỢ PHẢI TRẢ VÀ VỐN CHỦ SỞ HỮU",
              "field_path": "data.balance_sheet.totals.total_assets",
              "is_bold": true,
              "is_total_row": true,
              "show_difference": true
            }
          ]
        }
      ]
    },
    "income_statement_horizontal": {
      "description": "Báo cáo kết quả kinh doanh so sánh ngang",
      "sections": [
        {
          "section_name": "I. DOANH THU HOẠT ĐỘNG",
          "fields": [
            {
              "display_name": "1.1. Lãi từ các tài sản tài chính ghi nhận thông qua lãi/lỗ (FVTPL)",
              "field_path": "data.income_statement.operating_revenue.interest_income_fvtpl",
              "proportion_base": "data.income_statement.operating_revenue.total_operating_revenue",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "1.2. Lãi từ các khoản đầu tư nắm giữ đến ngày đáo hạn (HTM)",
              "field_path": "data.income_statement.operating_revenue.interest_income_htm",
              "proportion_base": "data.income_statement.operating_revenue.total_operating_revenue",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "1.3. Lãi từ các khoản cho vay và phải thu",
              "field_path": "data.income_statement.operating_revenue.interest_income_loans",
              "proportion_base": "data.income_statement.operating_revenue.total_operating_revenue",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "1.4. Lãi từ tài sản tài chính sẵn sàng để bán (AFS)",
              "field_path": "data.income_statement.operating_revenue.interest_income_afs",
              "proportion_base": "data.income_statement.operating_revenue.total_operating_revenue",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "1.6. Doanh thu nghiệp vụ môi giới chứng khoán",
              "field_path": "data.income_statement.operating_revenue.brokerage_revenue",
              "proportion_base": "data.income_statement.operating_revenue.total_operating_revenue",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "1.7. Doanh thu nghiệp vụ bảo lãnh, đại lý phát hành chứng khoán",
              "field_path": "data.income_statement.operating_revenue.underwriting_revenue",
              "proportion_base": "data.income_statement.operating_revenue.total_operating_revenue",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "1.8. Doanh thu nghiệp vụ tư vấn đầu tư chứng khoán",
              "field_path": "data.income_statement.operating_revenue.investment_advisory_revenue",
              "proportion_base": "data.income_statement.operating_revenue.total_operating_revenue",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "1.9. Doanh thu nghiệp vụ lưu ký chứng khoán",
              "field_path": "data.income_statement.operating_revenue.custody_revenue",
              "proportion_base": "data.income_statement.operating_revenue.total_operating_revenue",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "1.10. Doanh thu hoạt động tư vấn tài chính",
              "field_path": "data.income_statement.operating_revenue.financial_advisory_revenue",
              "proportion_base": "data.income_statement.operating_revenue.total_operating_revenue",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "1.11. Thu nhập hoạt động khác",
              "field_path": "data.income_statement.operating_revenue.other_operating_income",
              "proportion_base": "data.income_statement.operating_revenue.total_operating_revenue",
              "show_proportion": true,
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "II. CHI PHÍ HOẠT ĐỘNG",
          "fields": [
            {
              "display_name": "2.1. Lỗ các tài sản tài chính ghi nhận thông qua lãi/lỗ (FVTPL)",
              "field_path": "data.income_statement.operating_expenses.loss_from_fvtpl",
              "proportion_base": "data.income_statement.operating_expenses.total_operating_expenses",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "2.4. Chi phí dự phòng tài sản tài chính",
              "field_path": "data.income_statement.operating_expenses.provisions_for_impairment",
              "proportion_base": "data.income_statement.operating_expenses.total_operating_expenses",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "2.7. Chi phí nghiệp vụ môi giới chứng khoán",
              "field_path": "data.income_statement.operating_expenses.brokerage_expenses",
              "proportion_base": "data.income_statement.operating_expenses.total_operating_expenses",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "2.8. Chi phí nghiệp vụ bảo lãnh",
              "field_path": "data.income_statement.operating_expenses.underwriting_expenses",
              "proportion_base": "data.income_statement.operating_expenses.total_operating_expenses",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "2.9. Chi phí nghiệp vụ tư vấn đầu tư chứng khoán",
              "field_path": "data.income_statement.operating_expenses.advisory_expenses",
              "proportion_base": "data.income_statement.operating_expenses.total_operating_expenses",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "2.10. Chi phí nghiệp vụ lưu ký chứng khoán",
              "field_path": "data.income_statement.operating_expenses.custody_expenses",
              "proportion_base": "data.income_statement.operating_expenses.total_operating_expenses",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "2.11. Chi phí hoạt động tư vấn tài chính",
              "field_path": "data.income_statement.operating_expenses.financial_advisory_expenses",
              "proportion_base": "data.income_statement.operating_expenses.total_operating_expenses",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "2.12. Chi phí các dịch vụ khác",
              "field_path": "data.income_statement.operating_expenses.other_operating_expenses",
              "proportion_base": "data.income_statement.operating_expenses.total_operating_expenses",
              "show_proportion": true,
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "III. DOANH THU HOẠT ĐỘNG TÀI CHÍNH",
          "fields": [
            {
              "display_name": "3.2. Lãi tiền gửi ngân hàng",
              "field_path": "data.income_statement.financial_income_expenses.interest_income_deposits",
              "proportion_base": "data.income_statement.financial_income_expenses.total_financial_income",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "3.1. Chênh lệch lãi tỷ giá",
              "field_path": "data.income_statement.financial_income_expenses.forex_gain",
              "proportion_base": "data.income_statement.financial_income_expenses.total_financial_income",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "3.3. Lãi bán, thanh lý đầu tư",
              "field_path": "data.income_statement.financial_income_expenses.gain_on_disposal_investments",
              "proportion_base": "data.income_statement.financial_income_expenses.total_financial_income",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "3.4. Doanh thu khác về đầu tư",
              "field_path": "data.income_statement.financial_income_expenses.other_investment_income",
              "proportion_base": "data.income_statement.financial_income_expenses.total_financial_income",
              "show_proportion": true,
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "IV. CHI PHÍ TÀI CHÍNH",
          "fields": [
            {
              "display_name": "4.2. Chi phí lãi vay",
              "field_path": "data.income_statement.financial_income_expenses.interest_expense_borrowings",
              "proportion_base": "data.income_statement.financial_income_expenses.total_financial_expenses",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "4.1. Chênh lệch lỗ tỷ giá",
              "field_path": "data.income_statement.financial_income_expenses.forex_loss",
              "proportion_base": "data.income_statement.financial_income_expenses.total_financial_expenses",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "4.3. Lỗ bán, thanh lý đầu tư",
              "field_path": "data.income_statement.financial_income_expenses.loss_on_disposal_investments",
              "proportion_base": "data.income_statement.financial_income_expenses.total_financial_expenses",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "4.4. Chi phí dự phòng đầu tư dài hạn",
              "field_path": "data.income_statement.financial_income_expenses.provision_long_term_investments",
              "proportion_base": "data.income_statement.financial_income_expenses.total_financial_expenses",
              "show_proportion": true,
              "show_difference": true
            },
            {
              "display_name": "4.5. Chi phí tài chính khác",
              "field_path": "data.income_statement.financial_income_expenses.other_financial_expenses",
              "proportion_base": "data.income_statement.financial_income_expenses.total_financial_expenses",
              "show_proportion": true,
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "V. CHI PHÍ BÁN HÀNG",
          "fields": [
            {
              "display_name": "Chi phí bán hàng",
              "field_path": "data.income_statement.administrative_expenses.selling_expenses",
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "VI. CHI PHÍ QUẢN LÝ CÔNG TY CHỨNG KHOÁN",
          "fields": [
            {
              "display_name": "Chi phí quản lý doanh nghiệp",
              "field_path": "data.income_statement.administrative_expenses.general_admin_expenses",
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "VII. KẾT QUẢ HOẠT ĐỘNG",
          "fields": [
            {
              "display_name": "Lợi nhuận thuần từ hoạt động kinh doanh",
              "field_path": "data.income_statement.profit_and_tax.operating_profit",
              "is_bold": true,
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "VIII. THU NHẬP KHÁC VÀ CHI PHÍ KHÁC",
          "fields": [
            {
              "display_name": "8.1. Thu nhập khác",
              "field_path": "data.income_statement.profit_and_tax.other_income",
              "show_difference": true
            },
            {
              "display_name": "8.2. Chi phí khác",
              "field_path": "data.income_statement.profit_and_tax.other_expenses",
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "IX. TỔNG LỢI NHUẬN KẾ TOÁN TRƯỚC THUẾ",
          "fields": [
            {
              "display_name": "Tổng lợi nhuận kế toán trước thuế",
              "field_path": "data.income_statement.profit_and_tax.profit_before_tax",
              "is_bold": true,
              "show_difference": true
            },
            {
              "display_name": "9.1. Lợi nhuận đã thực hiện",
              "field_path": "data.income_statement.profit_and_tax.realized_profit",
              "show_difference": true
            },
            {
              "display_name": "9.2. Lợi nhuận chưa thực hiện",
              "field_path": "data.income_statement.profit_and_tax.unrealized_profit",
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "X. CHI PHÍ THUẾ TNDN",
          "fields": [
            {
              "display_name": "Chi phí thuế thu nhập doanh nghiệp",
              "field_path": "data.income_statement.profit_and_tax.corporate_income_tax",
              "show_difference": true
            }
          ]
        },
        {
          "section_name": "XI. LỢI NHUẬN SAU THUẾ",
          "fields": [
            {
              "display_name": "Lợi nhuận kế toán sau thuế TNDN",
              "field_path": "data.income_statement.profit_and_tax.net_profit_after_tax",
              "is_bold": true,
              "show_difference": true
            }
          ]
        }
      ]
    }
  }
}
"""