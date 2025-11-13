import json

import mlflow
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph.state import CompiledStateGraph, StateGraph
from pydantic import BaseModel, Field

from src.agent.agent_application import AgentApplication
from src.lending.agent.lending_agent_model import BusinessLoanValidationState, LendingShortTermContext, \
    OrchestrationInformation
from src.lending.agent.lending_prompt import (
    INCOMING_QUESTION_ANALYSIS,
    OVERALL_ANALYSIS_PROMPT,
    TRENDING_ANALYSIS_PROMPT,
    DEEP_ANALYSIS_PROMPT,
)
from src.lending.agent.short_term_context import InMemoryShortTermContextRepository
from src.graph.graph_provider import GraphProvider
from src.state.type import DefaultState

load_dotenv()
"""
{
  "dimensions": [
    {
      "dimension_name": "capital",
      "sub_dimension_name": ["1", "2", "3"]
    },
    {
      "dimension_name": "financial_situation",
      "sub_dimension_name": ["1", "2", "3"]
    }
  ],
  "analysis_type": "overall/trending/deep_analysis",
  "time_period": "1/2/3"
}
"""


class BusinessLoanValidationGraphProvider(GraphProvider[BusinessLoanValidationState]):

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0)
        self.short_term_context_repository = InMemoryShortTermContextRepository()

    def provide(self) -> CompiledStateGraph:
        graph = StateGraph(BusinessLoanValidationState)
        graph.add_node("supervisor", self.handle_supervisor)
        graph.add_node("final_answer", self.handle_final_answer)
        graph.add_node("fallback", self.handle_fallback)
        graph.set_entry_point("supervisor")
        graph.add_conditional_edges("supervisor", self.route_function)
        graph.set_finish_point("final_answer")
        graph.set_finish_point("fallback")
        return graph.compile()

    def handle_supervisor(self, state):
        incoming_message = state.get("message")
        structured_message = json.loads(incoming_message.content)
        document_id = structured_message.get("document_id")
        question = structured_message.get("question")
        documents = structured_message.get("documents")
        orchestration_information = self.get_orchestration_information(document_id, question, documents)
        filtered_documents = []
        for document in documents:
            document_time = document.get("report_date").split("-")[0]
            for period_time in orchestration_information.time_period:
                if document_time in period_time:
                    filtered_documents.append(document)
        fined_grain_data = calculate_financial_data(filtered_documents)
        return {
            "question": question,
            "orchestration_information": orchestration_information,
            "fined_grain_data": fined_grain_data,
        }

    def get_orchestration_information(self, document_id, question, documents):
        previous_context = self.short_term_context_repository.get(thread_id=document_id)
        if len(previous_context) > 0:
            previous_context_json = previous_context[-1].model_dump_json()
        else:
            previous_context_json = "{}"
        available_time_period = []
        # print(f"########### {previous_context_json} ########")
        for document in documents:
            report_date = document.get("report_date")
            available_time_period.append(report_date)
        available_time_period_json = json.dumps(sorted(available_time_period))
        prompt_template = ChatPromptTemplate.from_template(INCOMING_QUESTION_ANALYSIS)
        rag_chain = (
                {
                    "question": RunnablePassthrough(),
                    "available_periods": lambda _: available_time_period_json,
                    "previous_context": lambda _: previous_context_json
                }
                | prompt_template
                | self.llm.with_structured_output(
            OrchestrationInformation, method="json_mode"
        )
        )
        orchestration_response = rag_chain.invoke(question)
        print(orchestration_response)
        current_context = LendingShortTermContext(
            previous_analysis_type=orchestration_response.analysis_type,
            previous_dimensions=orchestration_response.dimensions,
            previous_period=orchestration_response.time_period
        )
        self.short_term_context_repository.put(thread_id=document_id, context=current_context)
        # memory_context = self.short_term_context_repository.get("680314b8-14b8-1803-99ee-f8afe3e7b2de")[-1]
        # print(f"########## {memory_context.model_dump_json()} #########")
        return orchestration_response

    def route_function(self, state):
        orchestration_information = state["orchestration_information"]
        confidence = orchestration_information.confidence
        if confidence is None:
            confidence = 0.0
        if confidence > 0.7:
            return "final_answer"
        else:
            return "fallback"

    def handle_fallback(self, state):
        question = state["question"]
        orchestration_information = state["orchestration_information"]
        clarifications = (
            []
            if orchestration_information is None
            else orchestration_information.suggested_clarifications
        )
        raw_clarifications = (
            ", ".join(clarifications)
            if clarifications is not None and len(clarifications) > 0
            else ""
        )
        prompt = """Tôi chưa xác định được rõ yêu cầu của bạn. Bạn có thể làm rõ thêm câu hỏi sau không?
        Câu hỏi: {question}
        Làm rõ: {clarifications}
        """
        prompt_template = ChatPromptTemplate.from_template(prompt)
        rag_chain = (
                {
                    "question": RunnablePassthrough(),
                    "clarifications": lambda _: raw_clarifications,
                }
                | prompt_template
                | self.llm
                | StrOutputParser()
        )
        return {"message": rag_chain.invoke(question)}

    def handle_final_answer(self, state):
        question = state["question"]
        orchestration_request = state["orchestration_information"]
        orchestration_request_json = orchestration_request.model_dump_json()
        financial_data_input = state["fined_grain_data"]
        financial_data_input_json = json.dumps(financial_data_input)
        analysis_type = orchestration_request.analysis_type
        if analysis_type == "overall":
            prompt_template = ChatPromptTemplate.from_template(OVERALL_ANALYSIS_PROMPT)
        elif analysis_type == "trending":
            prompt_template = ChatPromptTemplate.from_template(TRENDING_ANALYSIS_PROMPT)
        elif analysis_type == "deep_analysis":
            prompt_template = ChatPromptTemplate.from_template(DEEP_ANALYSIS_PROMPT)
        else:
            raise Exception(f"Illegal analysis type {analysis_type}")
        rag_chain = (
                {
                    "question": RunnablePassthrough(),
                    "orchestration_request": lambda _: orchestration_request_json,
                    "financial_data_input": lambda _: financial_data_input_json,
                }
                | prompt_template
                | self.llm
                | StrOutputParser()
        )
        return {"message": rag_chain.invoke(question)}


def calculate_financial_data(data):
    """
    Tính toán các chỉ số tài chính từ dữ liệu raw

    Input: list of dictionaries với format:
    [
        {
            "company": "SSI",
            "report_date": "2024-12-31",
            "currency": "VND",
            "reports": [
                {
                    "report_name": "financial_statement",
                    "fields": [
                        {"name": "total_assets", "value": 80000000000},
                        ...
                    ]
                },
                {
                    "report_name": "income_statement",
                    "fields": [...]
                },
                {
                    "report_name": "cashflow_statement",
                    "fields": [...]
                }
            ]
        },
        ...
    ]

    Output: list of dictionaries theo CAMEL structure:
    [
        {
            "company": "SSI",
            "report_date": "2024-12-31",
            "currency": "VND",
            "data": {
                "balance_sheet": {...},
                "income_statement": {...},
                "cashflow": {...},
                "metrics": {
                    "capital_adequacy": {...},
                    "asset_quality": {...},
                    "management_quality": {...},
                    "earnings": {...},
                    "liquidity": {...}
                }
            }
        },
        ...
    ]
    """
    results = []

    # Tạo dictionary để lưu data theo năm
    data_by_year = {}
    for report in data:
        year = report["report_date"]
        data_by_year[year] = report

    # Lấy danh sách năm và sắp xếp
    years = sorted(data_by_year.keys())

    for i, year in enumerate(years):
        report = data_by_year[year]

        # Tìm năm trước (nếu có)
        prev_year_data = None
        if i > 0:
            prev_year_data = data_by_year[years[i - 1]]

        # ============================================================
        # HELPER FUNCTIONS
        # ============================================================

        def get_value(report_name, field_name):
            """Lấy giá trị từ report hiện tại"""
            for r in report.get("reports", []):
                if r["report_name"] == report_name:
                    for field in r.get("fields", []):
                        if field["name"] == field_name:
                            return field["value"]
            return None

        def get_prev_value(report_name, field_name):
            """Lấy giá trị từ report năm trước"""
            if prev_year_data is None:
                return None
            for r in prev_year_data.get("reports", []):
                if r["report_name"] == report_name:
                    for field in r.get("fields", []):
                        if field["name"] == field_name:
                            return field["value"]
            return None

        # ============================================================
        # EXTRACT RAW DATA - BALANCE SHEET
        # ============================================================

        # Short-term assets
        short_term_assets = get_value("financial_statement", "short_term_assets")
        cash_and_equivalents = get_value("financial_statement", "cash_and_cash_equivalents")
        financial_assets_fvtpl = get_value("financial_statement", "financial_assets_at_fair_value_through_profit_or_loss")
        held_to_maturity = get_value("financial_statement", "held_to_maturity_investments")
        loans = get_value("financial_statement", "loans")
        available_for_sale = get_value("financial_statement", "available_for_sale_financial_assets")
        receivables = get_value("financial_statement", "receivables")
        other_short_term_assets = get_value("financial_statement", "other_short_term_assets")

        # Long-term assets
        long_term_assets = get_value("financial_statement", "long_term_assets")
        long_term_financial_assets = get_value("financial_statement", "long_term_financial_assets")
        fixed_assets = get_value("financial_statement", "fixed_assets")
        tangible_fixed_assets = get_value("financial_statement", "tangible_fixed_assets")
        intangible_fixed_assets = get_value("financial_statement", "intangible_fixed_assets")
        investment_property = get_value("financial_statement", "investment_property")
        investments_in_subsidiaries = get_value("financial_statement", "investments_in_subsidiaries")
        other_long_term_assets_detail = get_value("financial_statement", "other_long_term_assets")

        # Liabilities
        total_assets = get_value("financial_statement", "total_assets")
        total_liabilities = get_value("financial_statement", "liabilities")
        short_term_liabilities = get_value("financial_statement", "short_term_liabilities")
        short_term_borrowings = get_value("financial_statement", "short_term_borrowings")
        short_term_bonds = get_value("financial_statement", "short_term_bonds_issued")
        payables_securities_trading = get_value("financial_statement", "payables_from_securities_trading_activities")
        trade_payables = get_value("financial_statement", "short_term_trade_payables")
        taxes_payable = get_value("financial_statement", "taxes_and_other_payables_to_the_state")
        other_short_term_payables = get_value("financial_statement", "other_short_term_payables")

        long_term_liabilities = get_value("financial_statement", "long_term_liabilities")
        long_term_borrowings = get_value("financial_statement", "long_term_borrowings")
        long_term_bonds = get_value("financial_statement", "long_term_bonds_issued")
        deferred_tax_liabilities = get_value("financial_statement", "deferred_tax_liabilities")
        other_long_term_payables = get_value("financial_statement", "other_long_term_payables")

        # Equity
        owners_equity = get_value("financial_statement", "owners_equity")
        share_capital = get_value("financial_statement", "share_capital")
        share_premium = get_value("financial_statement", "share_premium")
        treasury_shares = get_value("financial_statement", "treasury_shares")
        retained_earnings = get_value("financial_statement", "retained_earnings")
        financial_reserve = get_value("financial_statement", "financial_reserve_and_business_risk_fund")
        other_equity = get_value("financial_statement", "other_funds_under_owners_equity")

        # ============================================================
        # EXTRACT RAW DATA - INCOME STATEMENT
        # ============================================================

        # Operating revenue
        total_operating_revenue = get_value("income_statement", "total_operating_revenue")
        interest_income_fvtpl = get_value("income_statement", "interest_and_fee_income_from_financial_assets_recognized_through_p_and_l")
        interest_income_htm = get_value("income_statement", "interest_income_from_held_to_maturity_investments")
        interest_income_loans = get_value("income_statement", "interest_income_from_loans_and_receivables")
        interest_income_afs = get_value("income_statement", "interest_income_from_available_for_sale_financial_assets")
        gain_hedging_derivatives = get_value("income_statement", "gain_from_hedging_derivatives")
        brokerage_revenue = get_value("income_statement", "brokerage_revenue")
        underwriting_revenue = get_value("income_statement", "underwriting_revenue")
        investment_advisory_revenue = get_value("income_statement", "investment_advisory_revenue")
        securities_custody_revenue = get_value("income_statement", "securities_custody_revenue")
        financial_advisory_revenue = get_value("income_statement", "financial_advisory_revenue")
        other_operating_income = get_value("income_statement", "other_operating_income")

        # Operating expenses
        total_operating_expenses = get_value("income_statement", "total_operating_expenses")
        loss_from_fvtpl = get_value("income_statement", "interest_expense_on_financial_assets_recognized_through_p_and_l")
        provisions_impairment = get_value("income_statement", "provisions_for_impairment_of_financial_assets")
        brokerage_expenses = get_value("income_statement", "brokerage_fees")
        underwriting_expenses = get_value("income_statement", "underwriting_and_bond_issuance_costs")
        investment_advisory_expenses = get_value("income_statement", "investment_advisory_expenses")
        securities_custody_expenses = get_value("income_statement", "securities_custody_expenses")
        financial_advisory_expenses = get_value("income_statement", "financial_advisory_expenses")
        other_operating_expenses = get_value("income_statement", "other_operating_expenses")

        # Financial income & expenses
        total_financial_income = get_value("income_statement", "total_financial_operating_revenue")
        interest_income_deposits = get_value("income_statement", "interest_income_from_deposits")
        forex_gain = get_value("income_statement", "increase_decrease_in_fair_value_of_exchange_rate_and_unrealized")
        gain_disposal = get_value("income_statement", "gain_on_disposal_of_investments_in_subsidiaries_associates_and_joint_ventures")
        other_investment_income = get_value("income_statement", "other_investment_income")

        total_financial_expenses = get_value("income_statement", "total_financial_expenses")
        interest_expense_borrowings = get_value("income_statement", "interest_expense_on_borrowings")
        forex_loss = get_value("income_statement", "increase_decrease_in_fair_value_of_exchange_rate_loss")
        loss_disposal = get_value("income_statement", "loss_on_disposal_of_investments_in_subsidiaries_associates_and_joint_ventures")
        provision_long_term_investments = get_value("income_statement", "provision_for_impairment_of_long_term_financial_investments")
        other_financial_expenses = get_value("income_statement", "other_financial_expenses")

        # Administrative expenses
        selling_expenses = get_value("income_statement", "selling_expenses")
        general_admin_expenses = get_value("income_statement", "general_and_administrative_expenses")

        # Profit and tax
        operating_profit = get_value("income_statement", "operating_profit")
        other_income = get_value("income_statement", "other_income")
        other_expenses = get_value("income_statement", "other_expenses")
        net_other_income_expenses = get_value("income_statement", "net_other_income_and_expenses")
        profit_before_tax = get_value("income_statement", "accounting_profit_before_tax")
        realized_profit = get_value("income_statement", "realized_profit")
        unrealized_profit = get_value("income_statement", "unrealized_profit_loss")
        corporate_income_tax = get_value("income_statement", "total_corporate_income_tax")
        current_tax_expense = get_value("income_statement", "current_corporate_income_tax_expense")
        deferred_tax_benefit = get_value("income_statement", "benefit_from_deferred_income_tax_expense")
        net_profit_after_tax = get_value("income_statement", "net_profit_after_tax")

        # ============================================================
        # EXTRACT RAW DATA - CASHFLOW
        # ============================================================

        net_operating_cashflow = get_value("cashflow_statement", "net_operating_cashflow")
        net_investing_cashflow = get_value("cashflow_statement", "net_investing_cashflow")
        net_financing_cashflow = get_value("cashflow_statement", "net_financing_cashflow")
        net_change_in_cash = get_value("cashflow_statement", "net_change_in_cash")
        depreciation_amortization = get_value("cashflow_statement", "depreciation_and_amortization")

        # ============================================================
        # GET PREVIOUS YEAR VALUES
        # ============================================================

        prev_total_assets = get_prev_value("financial_statement", "total_assets")
        prev_owners_equity = get_prev_value("financial_statement", "owners_equity")
        prev_net_profit = get_prev_value("income_statement", "net_profit_after_tax")

        # ============================================================
        # CALCULATE AVERAGE VALUES (cho ratios)
        # ============================================================

        # Tổng tài sản bình quân = (Tài sản năm T + Tài sản năm T-1) / 2
        avg_total_assets = None
        if total_assets and prev_total_assets:
            avg_total_assets = (total_assets + prev_total_assets) / 2

        # Vốn chủ sở hữu bình quân = (VCSH năm T + VCSH năm T-1) / 2
        avg_owners_equity = None
        if owners_equity and prev_owners_equity:
            avg_owners_equity = (owners_equity + prev_owners_equity) / 2

        # ============================================================
        # CALCULATE METRICS - CAPITAL ADEQUACY
        # ============================================================

        # Debt management
        debt_to_equity = (
            total_liabilities / owners_equity
            if total_liabilities and owners_equity and owners_equity != 0
            else None
        )

        leverage_ratio = (
            total_assets / owners_equity
            if total_assets and owners_equity and owners_equity != 0
            else None
        )

        debt_ratio = (
            total_liabilities / total_assets
            if total_liabilities and total_assets and total_assets != 0
            else None
        )

        long_term_debt_to_equity = (
            long_term_liabilities / owners_equity
            if long_term_liabilities and owners_equity and owners_equity != 0
            else None
        )

        # ✅ EBIT (ĐÃ SỬA) = Lợi nhuận trước thuế + Chi phí lãi vay
        ebit = None
        if profit_before_tax and interest_expense_borrowings:
            ebit = profit_before_tax + interest_expense_borrowings
        elif profit_before_tax:
            ebit = profit_before_tax

        interest_coverage_ratio = (
            ebit / interest_expense_borrowings
            if ebit and interest_expense_borrowings and interest_expense_borrowings != 0
            else None
        )

        debt_service_coverage_ratio = None  # Requires detailed cashflow

        # Growth metrics
        asset_growth_rate = (
            ((total_assets - prev_total_assets) / prev_total_assets)
            if total_assets and prev_total_assets and prev_total_assets != 0
            else None
        )

        # ============================================================
        # CALCULATE METRICS - ASSET QUALITY
        # ============================================================

        # Turnover metrics
        receivables_turnover = (
            total_operating_revenue / receivables
            if total_operating_revenue and receivables and receivables != 0
            else None
        )

        # Vòng quay vốn lưu động
        working_capital_prev = None
        if prev_year_data:
            prev_short_term_assets = get_prev_value("financial_statement", "short_term_assets")
            prev_short_term_liabilities = get_prev_value("financial_statement", "short_term_liabilities")
            if prev_short_term_assets and prev_short_term_liabilities:
                working_capital_prev = prev_short_term_assets - prev_short_term_liabilities

        working_capital_turnover = (
            total_operating_revenue / working_capital_prev
            if total_operating_revenue and working_capital_prev and working_capital_prev != 0
            else None
        )

        # ✅ ATO (ĐÃ SỬA) = Doanh thu / Tổng tài sản bình quân
        asset_turnover = (
            total_operating_revenue / avg_total_assets
            if total_operating_revenue and avg_total_assets and avg_total_assets != 0
            else None
        )

        # ============================================================
        # CALCULATE METRICS - MANAGEMENT QUALITY
        # ============================================================

        # Cost to income ratio
        cost_to_income_ratio = (
            total_operating_expenses / total_operating_revenue
            if total_operating_expenses and total_operating_revenue and total_operating_revenue != 0
            else None
        )

        # Fixed asset turnover
        fixed_asset_turnover = (
            total_operating_revenue / fixed_assets
            if total_operating_revenue and fixed_assets and fixed_assets != 0
            else None
        )

        # ============================================================
        # CALCULATE METRICS - EARNINGS
        # ============================================================

        # ✅ EBITDA (ĐÃ SỬA) = EBIT + Khấu hao
        ebitda = None
        if ebit:
            ebitda = ebit + (depreciation_amortization or 0)
        elif profit_before_tax:
            ebitda = profit_before_tax + (interest_expense_borrowings or 0) + (depreciation_amortization or 0)

        ebit_margin = (
            ebit / total_operating_revenue
            if ebit and total_operating_revenue and total_operating_revenue != 0
            else None
        )

        # Profitability ratios
        gross_profit_margin = None  # Not applicable for securities

        operating_profit_margin = (
            operating_profit / total_operating_revenue
            if operating_profit and total_operating_revenue and total_operating_revenue != 0
            else None
        )

        net_profit_margin = (
            net_profit_after_tax / total_operating_revenue
            if net_profit_after_tax and total_operating_revenue and total_operating_revenue != 0
            else None
        )

        ros = net_profit_margin  # Same as net_profit_margin

        # ✅ ROA (ĐÃ SỬA) = Lợi nhuận sau thuế / Tổng tài sản bình quân
        roa = (
            net_profit_after_tax / avg_total_assets
            if net_profit_after_tax and avg_total_assets and avg_total_assets != 0
            else None
        )

        # ✅ ROE (ĐÃ SỬA) = Lợi nhuận sau thuế / Vốn chủ sở hữu bình quân
        roe = (
            net_profit_after_tax / avg_owners_equity
            if net_profit_after_tax and avg_owners_equity and avg_owners_equity != 0
            else None
        )

        # Growth metrics
        net_profit_growth_rate = (
            ((net_profit_after_tax - prev_net_profit) / prev_net_profit)
            if net_profit_after_tax and prev_net_profit and prev_net_profit != 0
            else None
        )

        revenue_growth_rate = None
        prev_revenue = get_prev_value("income_statement", "total_operating_revenue")
        if total_operating_revenue and prev_revenue and prev_revenue != 0:
            revenue_growth_rate = ((total_operating_revenue - prev_revenue) / prev_revenue)

        # ============================================================
        # CALCULATE METRICS - LIQUIDITY
        # ============================================================

        current_ratio = (
            short_term_assets / short_term_liabilities
            if short_term_assets and short_term_liabilities and short_term_liabilities != 0
            else None
        )

        quick_ratio = (
            (short_term_assets - (other_short_term_assets or 0)) / short_term_liabilities
            if short_term_assets and short_term_liabilities and short_term_liabilities != 0
            else None
        )

        cash_ratio = (
            cash_and_equivalents / short_term_liabilities
            if cash_and_equivalents and short_term_liabilities and short_term_liabilities != 0
            else None
        )

        working_capital = (
            short_term_assets - short_term_liabilities
            if short_term_assets and short_term_liabilities
            else None
        )

        # ============================================================
        # BUILD OUTPUT STRUCTURE - CAMEL FORMAT
        # ============================================================

        result = {
            "company": report["company"],
            "report_date": report["report_date"],
            "currency": report["currency"],

            "data": {
                # ========================================
                # RAW DATA
                # ========================================
                "balance_sheet": {
                    "short_term_assets": {
                        "total_short_term_assets": short_term_assets,
                        "cash_and_equivalents": cash_and_equivalents,
                        "financial_assets_fvtpl": financial_assets_fvtpl,
                        "held_to_maturity_investments": held_to_maturity,
                        "loans": loans,
                        "available_for_sale_assets": available_for_sale,
                        "receivables": receivables,
                        "other_short_term_assets": other_short_term_assets
                    },
                    "long_term_assets": {
                        "total_long_term_assets": long_term_assets,
                        "long_term_financial_assets": long_term_financial_assets,
                        "fixed_assets": fixed_assets,
                        "tangible_fixed_assets": tangible_fixed_assets,
                        "intangible_fixed_assets": intangible_fixed_assets,
                        "investment_property": investment_property,
                        "investments_in_subsidiaries": investments_in_subsidiaries,
                        "other_long_term_assets": other_long_term_assets_detail
                    },
                    "short_term_liabilities": {
                        "total_short_term_liabilities": short_term_liabilities,
                        "short_term_borrowings": short_term_borrowings,
                        "short_term_bonds": short_term_bonds,
                        "payables_from_securities_trading": payables_securities_trading,
                        "trade_payables": trade_payables,
                        "taxes_payable": taxes_payable,
                        "other_short_term_payables": other_short_term_payables
                    },
                    "long_term_liabilities": {
                        "total_long_term_liabilities": long_term_liabilities,
                        "long_term_borrowings": long_term_borrowings,
                        "long_term_bonds": long_term_bonds,
                        "deferred_tax_liabilities": deferred_tax_liabilities,
                        "other_long_term_payables": other_long_term_payables
                    },
                    "equity": {
                        "total_equity": owners_equity,
                        "share_capital": share_capital,
                        "share_premium": share_premium,
                        "treasury_shares": treasury_shares,
                        "retained_earnings": retained_earnings,
                        "reserves": financial_reserve,
                        "other_equity": other_equity
                    },
                    "totals": {
                        "total_assets": total_assets,
                        "total_liabilities": total_liabilities
                    }
                },

                "income_statement": {
                    "operating_revenue": {
                        "total_operating_revenue": total_operating_revenue,
                        "interest_income_fvtpl": interest_income_fvtpl,
                        "interest_income_htm": interest_income_htm,
                        "interest_income_loans": interest_income_loans,
                        "interest_income_afs": interest_income_afs,
                        "gain_hedging_derivatives": gain_hedging_derivatives,
                        "brokerage_revenue": brokerage_revenue,
                        "underwriting_revenue": underwriting_revenue,
                        "investment_advisory_revenue": investment_advisory_revenue,
                        "custody_revenue": securities_custody_revenue,
                        "financial_advisory_revenue": financial_advisory_revenue,
                        "other_operating_income": other_operating_income
                    },
                    "operating_expenses": {
                        "total_operating_expenses": total_operating_expenses,
                        "loss_from_fvtpl": loss_from_fvtpl,
                        "provisions_for_impairment": provisions_impairment,
                        "brokerage_expenses": brokerage_expenses,
                        "underwriting_expenses": underwriting_expenses,
                        "advisory_expenses": investment_advisory_expenses,
                        "custody_expenses": securities_custody_expenses,
                        "financial_advisory_expenses": financial_advisory_expenses,
                        "other_operating_expenses": other_operating_expenses
                    },
                    "financial_income_expenses": {
                        "total_financial_income": total_financial_income,
                        "interest_income_deposits": interest_income_deposits,
                        "forex_gain": forex_gain,
                        "gain_on_disposal_investments": gain_disposal,
                        "other_investment_income": other_investment_income,
                        "total_financial_expenses": total_financial_expenses,
                        "interest_expense_borrowings": interest_expense_borrowings,
                        "forex_loss": forex_loss,
                        "loss_on_disposal_investments": loss_disposal,
                        "provision_long_term_investments": provision_long_term_investments,
                        "other_financial_expenses": other_financial_expenses
                    },
                    "administrative_expenses": {
                        "selling_expenses": selling_expenses,
                        "general_admin_expenses": general_admin_expenses
                    },
                    "profit_and_tax": {
                        "operating_profit": operating_profit,
                        "other_income": other_income,
                        "other_expenses": other_expenses,
                        "net_other_income_expenses": net_other_income_expenses,
                        "profit_before_tax": profit_before_tax,
                        "realized_profit": realized_profit,
                        "unrealized_profit": unrealized_profit,
                        "corporate_income_tax": corporate_income_tax,
                        "current_tax_expense": current_tax_expense,
                        "deferred_tax_benefit": deferred_tax_benefit,
                        "net_profit_after_tax": net_profit_after_tax
                    }
                },

                "cashflow": {
                    "operating_cashflow": {
                        "net_operating_cashflow": net_operating_cashflow
                    },
                    "investing_cashflow": {
                        "net_investing_cashflow": net_investing_cashflow
                    },
                    "financing_cashflow": {
                        "net_financing_cashflow": net_financing_cashflow
                    },
                    "net_cashflow": {
                        "net_change_in_cash": net_change_in_cash
                    }
                },

                # ========================================
                # CALCULATED METRICS - CAMEL
                # ========================================
                "metrics": {
                    # C - Capital Adequacy
                    "capital_adequacy": {
                        "capital_structure": {
                            "total_assets": total_assets,
                            "total_liabilities": total_liabilities,
                            "short_term_liabilities": short_term_liabilities,
                            "long_term_liabilities": long_term_liabilities,
                            "owners_equity": owners_equity
                        },
                        "debt_management": {
                            "debt_to_equity": debt_to_equity,
                            "leverage_ratio": leverage_ratio,
                            "debt_ratio": debt_ratio,
                            "long_term_debt_to_equity": long_term_debt_to_equity,
                            "interest_coverage_ratio": interest_coverage_ratio,
                            "debt_service_coverage_ratio": debt_service_coverage_ratio
                        },
                        "growth_metrics": {
                            "asset_growth_rate": asset_growth_rate
                        }
                    },

                    # A - Asset Quality
                    "asset_quality": {
                        "asset_composition": {
                            "receivables": receivables,
                            "short_term_assets": short_term_assets,
                            "long_term_assets": long_term_assets
                        },
                        "turnover_metrics": {
                            "receivables_turnover": receivables_turnover,
                            "working_capital_turnover": working_capital_turnover,
                            "asset_turnover": asset_turnover
                        }
                    },

                    # M - Management Quality
                    "management_quality": {
                        "revenue_performance": {
                            "total_operating_revenue": total_operating_revenue,
                            "brokerage_revenue": brokerage_revenue,
                            "proprietary_trading_revenue": interest_income_fvtpl,
                            "advisory_revenue": (investment_advisory_revenue or 0) + (financial_advisory_revenue or 0)
                        },
                        "expense_management": {
                            "total_operating_expenses": total_operating_expenses,
                            "administrative_expenses": (selling_expenses or 0) + (general_admin_expenses or 0),
                            "cost_to_income_ratio": cost_to_income_ratio
                        },
                        "operational_efficiency": {
                            "ato": asset_turnover,
                            "fixed_asset_turnover": fixed_asset_turnover,
                            "revenue_per_employee": None
                        }
                    },

                    # E - Earnings
                    "earnings": {
                        "profit_metrics": {
                            "ebit": ebit,
                            "ebitda": ebitda,
                            "operating_profit": operating_profit,
                            "profit_before_tax": profit_before_tax,
                            "net_profit_after_tax": net_profit_after_tax
                        },
                        "profitability_ratios": {
                            "gross_profit_margin": gross_profit_margin,
                            "operating_profit_margin": operating_profit_margin,
                            "net_profit_margin": net_profit_margin,
                            "ebit_margin": ebit_margin,
                            "ros": ros,
                            "roa": roa,
                            "roe": roe
                        },
                        "growth_metrics": {
                            "net_profit_growth_rate": net_profit_growth_rate,
                            "revenue_growth_rate": revenue_growth_rate
                        }
                    },

                    # L - Liquidity
                    "liquidity": {
                        "liquidity_ratios": {
                            "current_ratio": current_ratio,
                            "quick_ratio": quick_ratio,
                            "cash_ratio": cash_ratio,
                            "working_capital": working_capital
                        }
                    },

                    # S - Sensitivity (placeholder)
                    "sensitivity": {
                        "market_risk_metrics": {
                            "trading_assets_ratio": None,
                            "derivative_exposure": None
                        }
                    }
                }
            }
        }

        results.append(result)

    return results


mlflow.langchain.autolog()
graph = BusinessLoanValidationGraphProvider().provide()
chat_agent = AgentApplication.initialize(graph=graph)
mlflow.models.set_model(chat_agent)
