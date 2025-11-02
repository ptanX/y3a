import asyncio
import json
from abc import abstractmethod, ABC

from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.dispatcher.executions_dispatcher import ExecutionDispatcherBuilder
from src.ocr.data.data_prompt_registry import get_data_prompt_by_section
from src.ocr.data.pdf_text_extractor import DocumentAIExtractor
from src.ocr.metadata.identifier_retriever import NameBasedIdentifierRetriever
from src.ocr.metadata.metadata_retriever import (
    extract_single_securities_report_page_raw_metadata,
    SecuritiesFinancialReportMetadataRetriever, BusinessRegistrationMetadataRetriever,
)
from src.ocr.ocr_model import DocumentMetadata
from src.ocr.utils import cut_pdf_to_bytes

load_dotenv()

FIELD_MAPPING = {
    # Doanh thu hoạt động
    "profit_from_financial_assets_recognized_through_p_and_l_at_fvtpl": "interest_and_fee_income_from_financial_assets_recognized_through_p_and_l",
    "income_from_financial_assets_at_fvtpl": "interest_and_fee_income_from_financial_assets_recognized_through_p_and_l",
    "profit_from_sale_of_fvtpl_financial_assets": "interest_income_from_financial_assets_recognized_through_p_and_l",
    "gain_on_sale_of_financial_assets_at_fvtpl": "interest_income_from_financial_assets_recognized_through_p_and_l",
    "unrealized_gain_on_fvtpl_financial_assets": "increase_decrease_in_fair_value_of_financial_assets_recognized_through_p_and_l",
    "unrealized_gain_on_remeasurement_of_financial_assets_at_fvtpl": "increase_decrease_in_fair_value_of_financial_assets_recognized_through_p_and_l",
    "dividends_and_interest_from_fvtpl_financial_assets": "dividend_and_interest_income_from_financial_assets_recognized_through_p_and_l",
    "dividends_and_interest_income_from_financial_assets_at_fvtpl": "dividend_and_interest_income_from_financial_assets_recognized_through_p_and_l",
    "profit_from_held_to_maturity_investments": "interest_income_from_held_to_maturity_investments",
    "profit_from_loans_and_receivables": "interest_income_from_loans_and_receivables",
    "securities_brokerage_revenue": "brokerage_revenue",
    "brokerage_service_revenue": "brokerage_revenue",
    "underwriting_and_issuance_agency_revenue": "underwriting_revenue",
    "securities_investment_advisory_revenue": "investment_advisory_revenue",
    # Chi phí hoạt động
    "loss_from_financial_assets_recognized_through_p_and_l_at_fvtpl": "interest_expense_on_financial_assets_recognized_through_p_and_l",
    "loss_from_financial_assets_at_fvtpl": "interest_expense_on_financial_assets_recognized_through_p_and_l",
    "loss_from_sale_of_fvtpl_financial_assets": "interest_expense",
    "loss_on_sale_of_financial_assets_at_fvtpl": "interest_expense",
    "unrealized_loss_on_fvtpl_financial_assets": "decrease_in_fair_value_of_financial_assets",
    "unrealized_loss_on_remeasurement_of_financial_assets_at_fvtpl": "decrease_in_fair_value_of_financial_assets",
    "transaction_costs_for_fvtpl_financial_assets": "transaction_fees_for_financial_assets",
    "transaction_costs_for_financial_assets_at_fvtpl": "transaction_fees_for_financial_assets",
    "provision_for_financial_assets_impairment_bad_debt_write_off_financial_asset_decline_and_loan_borrowing_costs": "provisions_for_impairment_of_financial_assets",
    "provision_for_financial_assets_and_loans": "provisions_for_impairment_of_financial_assets",
    "proprietary_trading_expenses": "operating_expense",
    "securities_brokerage_expenses": "brokerage_fees",
    "brokerage_service_expenses": "brokerage_fees",
    "underwriting_and_issuance_agency_expenses": "underwriting_and_bond_issuance_costs",
    "securities_investment_advisory_expenses": "investment_advisory_expenses",
    # Doanh thu tài chính
    "realized_and_unrealized_foreign_exchange_gains": "increase_decrease_in_fair_value_of_exchange_rate_and_unrealized",
    "realized_and_unrealized_exchange_rate_gain": "increase_decrease_in_fair_value_of_exchange_rate_and_unrealized",
    "dividends_and_undrawn_interest_from_non_fixed_deposits": "interest_income_from_deposits",
    "dividends_and_interest_income_from_non_fixed_deposits": "interest_income_from_deposits",
    "profit_from_sale_and_liquidation_of_investments_in_subsidiaries_associates": "other_investment_income",
    "gain_on_sale_and_liquidation_of_investments_in_subsidiaries_and_associates": "other_investment_income",
    # Chi phí tài chính
    "realized_and_unrealized_foreign_exchange_losses": "increase_decrease_in_fair_value_of_exchange_rate_loss",
    "realized_and_unrealized_exchange_rate_loss": "increase_decrease_in_fair_value_of_exchange_rate_loss",
    # Lưu ý: "interest_expense" từ SSI cần map sang "interest_expense_on_borrowings" nếu là chi phí lãi vay
    # Nhưng cũng có "interest_expense" ở trường #15 (lỗ bán TSTC)
    # Cần xử lý theo context
    # Quản lý
    "administrative_expenses": "general_and_administrative_expenses",
    # Kết quả
    "operating_result": "operating_profit",
    "total_other_activities_result": "net_other_income_and_expenses",
    # Lợi nhuận
    "profit_before_tax": "accounting_profit_before_tax",
    "retained_earnings_realized": "realized_profit",
    "retained_earnings_unrealized": "unrealized_profit_loss",
    # Thuế
    "deferred_corporate_income_tax_expense_or_income": "benefit_from_deferred_income_tax_expense",
    "deferred_income_tax_expense": "benefit_from_deferred_income_tax_expense",
    "corporate_income_tax_expense": "total_corporate_income_tax",
    "profit_after_tax": "net_profit_after_tax",
}

PROJECT_ID = "387819483924"
LOCATION = "us"
business_registration_processor_id = "5110722c3ac24f03"
company_character_processor_id = "12676ebbd1c0ed5"


class DocumentDataRetriever(ABC):

    @abstractmethod
    def retrieve(self, doc_metadata: DocumentMetadata):
        pass


class FinancialSecuritiesReportDataRetriever(DocumentDataRetriever):
    def retrieve(self, doc_metadata: DocumentMetadata):
        client = genai.Client()
        reports = []
        for section in doc_metadata.sections:
            page_content_in_bytes = cut_pdf_to_bytes(
                input_pdf=doc_metadata.document_path,
                start_page=section.page_info.from_page,
                end_page=section.page_info.to_page,
            )
            prompt = get_data_prompt_by_section(
                document_type=doc_metadata.document_type,
                section_type=section.component_type,
            )
            response = client.models.generate_content(
                model="gemini-2.5-pro",
                contents=[
                    types.Part.from_bytes(
                        data=page_content_in_bytes,
                        mime_type="application/pdf",
                    ),
                    prompt,
                ],
            )
            response_json = json.loads(
                response.text.replace("```json", "").replace("```", "").strip()
            )
            if section.component_type == "income_statement":
                response_json = self.normalize_field_names(response_json)
            report = {
                "report_name": section.component_type,
                "description": section.component_type,
                "fields": response_json,
            }
            reports.append(report)
        return {
            "company": "",
            "report_date": doc_metadata.other_info.get("report_date"),
            "currency": "VND",
            "reports": reports,
        }

    def normalize_field_names(self, gemini_output):
        """
        Chuyển đổi tên field từ Gemini output sang tên chuẩn DNSE
        """
        result = []
        for item in gemini_output:
            name = item.get("name")
            value = item.get("value")

            # Map sang tên chuẩn
            standard_name = FIELD_MAPPING.get(name, name)

            result.append({"name": standard_name, "value": value})

        return result


class BusinessRegistrationDataRetriever(DocumentDataRetriever):

    def retrieve(self, doc_metadata: DocumentMetadata):
        content_in_bytes = cut_pdf_to_bytes(
            input_pdf=doc_metadata.document_path,
            start_page=doc_metadata.sections[0].page_info.from_page,
            end_page=doc_metadata.sections[0].page_info.to_page,
        )
        business_regis_extractor = DocumentAIExtractor(project_id=PROJECT_ID,
                                                       location=LOCATION,
                                                       processor_id=business_registration_processor_id,
                                                       )
        business_regis_cert = business_regis_extractor.extract_normalized_text(file_content=content_in_bytes)
        return business_regis_cert


if __name__ == '__main__':
    load_dotenv()
    input_path = (
        "C:\\Users\\ADMIN\\Desktop\\working\\code\\y3s\\documentations\\dnse-pl-dkkd.pdf"
    )
    execution_dispatcher = (
        ExecutionDispatcherBuilder().set_dispatcher(
            name="extract_single_page_metadata",
            handler=extract_single_securities_report_page_raw_metadata,
        ).build()
    )
    identifier_retriever = NameBasedIdentifierRetriever()
    doc_identifier_metadata = identifier_retriever.retrieve(path=input_path)
    # print(doc_identifier_metadata)
    metadata_retriever = BusinessRegistrationMetadataRetriever()
    doc_metadata = asyncio.run(
        metadata_retriever.retrieve(path=input_path, document_identifier=doc_identifier_metadata))
    print(doc_metadata)
    actual_data = BusinessRegistrationDataRetriever().retrieve(doc_metadata)
    print(actual_data)
