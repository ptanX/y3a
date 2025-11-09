import json
from typing import List, Dict

import mlflow
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph.state import CompiledStateGraph, StateGraph
from mlflow.types.agent import ChatAgentMessage
from pydantic import BaseModel, Field

from src.agent.agent_application import AgentApplication
from src.bidv.agent.documentation import *
from src.bidv.agent.lending_prompt import (
    INCOMING_QUESTION_ANALYSIS,
    OVERALL_ANALYSIS_PROMPT,
    TRENDING_ANALYSIS_PROMPT,
    DEEP_ANALYSIS_PROMPT,
)
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


class DimensionRequest(BaseModel):
    """Schema cho từng dimension được request"""

    dimension_name: str = Field(
        description="Tên dimension từ danh sách hợp lệ: capital_adequacy, asset_quality, management_quality, earnings,"
                    " liquidity, sensitivity_to_market_risk"
    )
    sub_dimension_name: List[str] = Field(
        description="Danh sách các sub-dimension names thuộc dimension này"
    )


class OrchestrationInformation(BaseModel):
    """Schema cho orchestration output"""

    analysis_type: str = Field(
        description="Loại phân tích: overall, trending, hoặc deep_analysis"
    )
    dimensions: List[DimensionRequest] = Field(
        description="Danh sách các dimensions và sub-dimensions cần phân tích"
    )
    time_period: List[str] = Field(
        description="Các khoảng thời gian cần phân tích: 2021, 2022, 2023, Q1_2024"
    )
    confidence: float = Field(description="mức độ tự tin")
    reasoning: str = Field(description="lý do đưa ra quyết định")
    suggested_clarifications: List[str] = Field(
        description="clarification nếu như confidence < 0.7"
    )


class BusinessLoanValidationState(DefaultState):
    question: str
    orchestration_information: OrchestrationInformation
    documents: List[Dict]
    fined_grain_data: List[Dict]


class BusinessLoanValidationGraphProvider(GraphProvider[BusinessLoanValidationState]):

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0)

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
        question = structured_message.get("question")
        documents = structured_message.get("documents")
        orchestration_information = self.get_orchestration_information(question)
        fined_grain_data = calculate_financial_metrics(documents)
        return {
            "question": question,
            "orchestration_information": orchestration_information,
            "documents": documents,
            "fined_grain_data": fined_grain_data,
        }

    def get_orchestration_information(self, question):
        prompt_template = ChatPromptTemplate.from_template(INCOMING_QUESTION_ANALYSIS)
        rag_chain = (
            {"question": RunnablePassthrough()}
            | prompt_template
            | self.llm.with_structured_output(
                OrchestrationInformation, method="json_mode"
            )
        )
        return rag_chain.invoke(question)

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
        financial_data_input = state["fined_grain_data"]
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
                "orchestration_request": lambda _: orchestration_request,
                "financial_data_input": lambda _: financial_data_input,
            }
            | prompt_template
            | self.llm
            | StrOutputParser()
        )
        return {"message": rag_chain.invoke(question)}


def calculate_financial_metrics(data):
    """
    Tính toán các chỉ số tài chính từ dữ liệu raw
    Input: list of dictionaries
    Output: list of dictionaries với các chỉ số đã tính
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

        # Helper functions để lấy giá trị từ reports
        def get_value(report_name, field_name):
            for r in report.get("reports", []):
                if r["report_name"] == report_name:
                    for field in r.get("fields", []):
                        if field["name"] == field_name:
                            return field["value"]
            return None

        def get_prev_value(report_name, field_name):
            if prev_year_data is None:
                return None
            for r in prev_year_data.get("reports", []):
                if r["report_name"] == report_name:
                    for field in r.get("fields", []):
                        if field["name"] == field_name:
                            return field["value"]
            return None

        # Lấy các giá trị từ financial_statement
        total_assets = get_value("financial_statement", "total_assets")
        total_liabilities = get_value("financial_statement", "liabilities")
        short_term_liabilities = get_value("financial_statement", "short_term_liabilities")
        long_term_liabilities = get_value("financial_statement", "long_term_liabilities")
        owners_equity = get_value("financial_statement", "owners_equity")
        receivables = get_value("financial_statement", "receivables")
        short_term_assets = get_value("financial_statement", "short_term_assets")
        cash_and_cash_equivalents = get_value("financial_statement", "cash_and_cash_equivalents")

        # Lấy các giá trị từ income_statement
        total_operating_revenue = get_value("income_statement", "total_operating_revenue")
        interest_and_fee_income = get_value("income_statement", "interest_and_fee_income_from_financial_assets_recognized_through_p_and_l")
        interest_income_from_fa = get_value("income_statement", "interest_income_from_financial_assets_recognized_through_p_and_l")
        increase_decrease_fair_value_fa = get_value("income_statement", "increase_decrease_in_fair_value_of_financial_assets_recognized_through_p_and_l")
        dividend_and_interest = get_value("income_statement", "dividend_and_interest_income_from_financial_assets_recognized_through_p_and_l")
        decrease_fair_value_warrants = get_value("income_statement", "decrease_in_fair_value_of_outstanding_warrants")
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

        total_operating_expenses = get_value("income_statement", "total_operating_expenses")
        interest_expense_fa = get_value("income_statement", "interest_expense_on_financial_assets_recognized_through_p_and_l")
        interest_expense = get_value("income_statement", "interest_expense")
        decrease_fair_value_fa = get_value("income_statement", "decrease_in_fair_value_of_financial_assets")
        transaction_fees_fa = get_value("income_statement", "transaction_fees_for_financial_assets")
        increase_fair_value_warrants = get_value("income_statement", "increase_in_fair_value_of_outstanding_warrants")
        loss_htm = get_value("income_statement", "loss_from_held_to_maturity_investments")
        loss_afs_reclassification = get_value("income_statement", "loss_and_recognition_of_fair_value_difference_of_available_for_sale_financial_assets_upon_reclassification")
        provisions_impairment = get_value("income_statement", "provisions_for_impairment_of_financial_assets")
        loss_hedging_derivatives = get_value("income_statement", "loss_from_hedging_derivatives")
        operating_expense = get_value("income_statement", "operating_expense")
        brokerage_fees = get_value("income_statement", "brokerage_fees")
        underwriting_costs = get_value("income_statement", "underwriting_and_bond_issuance_costs")
        investment_advisory_expenses = get_value("income_statement", "investment_advisory_expenses")
        securities_custody_expenses = get_value("income_statement", "securities_custody_expenses")
        financial_advisory_expenses = get_value("income_statement", "financial_advisory_expenses")
        other_operating_expenses = get_value("income_statement", "other_operating_expenses")

        total_financial_operating_revenue = get_value("income_statement", "total_financial_operating_revenue")
        exchange_rate_unrealized = get_value("income_statement", "increase_decrease_in_fair_value_of_exchange_rate_and_unrealized")
        interest_income_deposits = get_value("income_statement", "interest_income_from_deposits")
        gain_disposal_investments = get_value("income_statement", "gain_on_disposal_of_investments_in_subsidiaries_associates_and_joint_ventures")
        other_investment_income = get_value("income_statement", "other_investment_income")

        exchange_rate_loss = get_value("income_statement", "increase_decrease_in_fair_value_of_exchange_rate_loss")
        interest_expense_borrowings = get_value("income_statement", "interest_expense_on_borrowings")
        loss_disposal_investments = get_value("income_statement", "loss_on_disposal_of_investments_in_subsidiaries_associates_and_joint_ventures")
        provision_long_term_investments = get_value("income_statement", "provision_for_impairment_of_long_term_financial_investments")
        other_financial_expenses = get_value("income_statement", "other_financial_expenses")
        total_financial_expenses = get_value("income_statement", "total_financial_expenses")

        selling_expenses = get_value("income_statement", "selling_expenses")
        general_admin_expenses = get_value("income_statement", "general_and_administrative_expenses")

        operating_profit = get_value("income_statement", "operating_profit")
        other_income = get_value("income_statement", "other_income")
        other_expenses = get_value("income_statement", "other_expenses")
        net_other_income_expenses = get_value("income_statement", "net_other_income_and_expenses")
        accounting_profit_before_tax = get_value("income_statement", "accounting_profit_before_tax")
        realized_profit = get_value("income_statement", "realized_profit")
        unrealized_profit_loss = get_value("income_statement", "unrealized_profit_loss")
        total_corporate_income_tax = get_value("income_statement", "total_corporate_income_tax")
        current_tax_expense = get_value("income_statement", "current_corporate_income_tax_expense")
        deferred_tax_benefit = get_value("income_statement", "benefit_from_deferred_income_tax_expense")
        net_profit_after_tax = get_value("income_statement", "net_profit_after_tax")
        profit_equity_holders = get_value("income_statement", "profit_attributable_to_equity_holders")
        profit_after_tax_funds = get_value("income_statement", "profit_after_tax_allocated_to_funds")
        profit_non_controlling = get_value("income_statement", "profit_attributable_to_non_controlling_interests")

        # Lấy giá trị năm trước để tính growth và ratios
        prev_total_assets = get_prev_value("financial_statement", "total_assets")
        prev_owners_equity = get_prev_value("financial_statement", "owners_equity")
        prev_net_profit = get_prev_value("income_statement", "net_profit_after_tax")

        # Tính toán các chỉ số
        # Debt management
        debt_to_equity = (
            total_liabilities / owners_equity
            if owners_equity and owners_equity != 0
            else None
        )
        leverage_ratio = (
            total_assets / owners_equity
            if owners_equity and owners_equity != 0
            else None
        )
        debt_ratio = (
            total_liabilities / total_assets
            if total_assets and total_assets != 0
            else None
        )
        long_term_debt_to_equity = (
            long_term_liabilities / owners_equity
            if long_term_liabilities and owners_equity and owners_equity != 0
            else None
        )

        # Interest coverage ratio = EBIT / Interest Expense
        ebit = (
            operating_profit + interest_expense_borrowings
            if operating_profit and interest_expense_borrowings
            else None
        )
        interest_coverage_ratio = (
            ebit / interest_expense_borrowings
            if ebit and interest_expense_borrowings and interest_expense_borrowings != 0
            else None
        )

        # Debt service coverage - cần cash flow data, để null
        debt_service_coverage_ratio = None

        # Growth metrics
        asset_growth_rate = (
            ((total_assets - prev_total_assets) / prev_total_assets)
            if prev_total_assets and prev_total_assets != 0
            else None
        )
        net_profit_growth_rate = (
            ((net_profit_after_tax - prev_net_profit) / prev_net_profit)
            if prev_net_profit and prev_net_profit != 0
            else None
        )

        # Asset turnover metrics
        receivables_turnover = (
            total_operating_revenue / receivables
            if total_operating_revenue and receivables and receivables != 0
            else None
        )

        # Operational efficiency (sử dụng total assets năm trước)
        ato = (
            total_operating_revenue / prev_total_assets
            if total_operating_revenue and prev_total_assets and prev_total_assets != 0
            else None
        )
        fixed_asset_turnover = None

        # Profit metrics
        ebitda = ebit
        ebit_margin = (
            ebit / total_operating_revenue
            if ebit and total_operating_revenue and total_operating_revenue != 0
            else None
        )

        # Profitability ratios (sử dụng assets/equity năm trước)
        ros = (
            net_profit_after_tax / total_operating_revenue
            if net_profit_after_tax and total_operating_revenue and total_operating_revenue != 0
            else None
        )
        roa = (
            net_profit_after_tax / prev_total_assets
            if net_profit_after_tax and prev_total_assets and prev_total_assets != 0
            else None
        )
        roe = (
            net_profit_after_tax / prev_owners_equity
            if net_profit_after_tax and prev_owners_equity and prev_owners_equity != 0
            else None
        )

        # Gross profit margin - không có COGS
        gross_profit_margin = None

        # Liquidity ratios
        current_ratio = (
            short_term_assets / short_term_liabilities
            if short_term_assets and short_term_liabilities and short_term_liabilities != 0
            else None
        )
        quick_ratio = (
            (short_term_assets - 0) / short_term_liabilities
            if short_term_assets and short_term_liabilities and short_term_liabilities != 0
            else None
        )
        cash_ratio = (
            cash_and_cash_equivalents / short_term_liabilities
            if cash_and_cash_equivalents and short_term_liabilities and short_term_liabilities != 0
            else None
        )
        working_capital = (
            short_term_assets - short_term_liabilities
            if short_term_assets and short_term_liabilities
            else None
        )

        # Tạo output structure
        result = {
            "company": report["company"],
            "report_date": report["report_date"],
            "currency": report["currency"],
            "capital_adequacy": {
                "capital_structure": {
                    "total_assets": total_assets,
                    "total_liabilities": total_liabilities,
                    "short_term_liabilities": short_term_liabilities,
                    "long_term_liabilities": long_term_liabilities,
                    "owners_equity": owners_equity,
                },
                "debt_management": {
                    "debt_to_equity": debt_to_equity,
                    "leverage_ratio": leverage_ratio,
                    "debt_service_coverage_ratio": debt_service_coverage_ratio,
                    "interest_coverage_ratio": interest_coverage_ratio,
                    "debt_ratio": debt_ratio,
                    "long_term_debt_to_equity": long_term_debt_to_equity,
                },
                "growth_metrics": {"asset_growth_rate": asset_growth_rate},
            },
            "asset_quality": {
                "asset_quality_metrics": {"receivables": receivables},
                "asset_turnover_metrics": {
                    "receivables_turnover": receivables_turnover
                },
            },
            "management_quality": {
                "operating_revenue": {
                    "total_operating_revenue": total_operating_revenue,
                    "interest_and_fee_income_from_financial_assets_recognized_through_p_and_l": interest_and_fee_income,
                    "interest_income_from_financial_assets_recognized_through_p_and_l": interest_income_from_fa,
                    "increase_decrease_in_fair_value_of_financial_assets_recognized_through_p_and_l": increase_decrease_fair_value_fa,
                    "dividend_and_interest_income_from_financial_assets_recognized_through_p_and_l": dividend_and_interest,
                    "decrease_in_fair_value_of_outstanding_warrants": decrease_fair_value_warrants,
                    "interest_income_from_held_to_maturity_investments": interest_income_htm,
                    "interest_income_from_loans_and_receivables": interest_income_loans,
                    "interest_income_from_available_for_sale_financial_assets": interest_income_afs,
                    "gain_from_hedging_derivatives": gain_hedging_derivatives,
                    "brokerage_revenue": brokerage_revenue,
                    "underwriting_revenue": underwriting_revenue,
                    "investment_advisory_revenue": investment_advisory_revenue,
                    "securities_custody_revenue": securities_custody_revenue,
                    "financial_advisory_revenue": financial_advisory_revenue,
                    "other_operating_income": other_operating_income,
                },
                "operating_expenses": {
                    "total_operating_expenses": total_operating_expenses,
                    "interest_expense_on_financial_assets_recognized_through_p_and_l": interest_expense_fa,
                    "interest_expense": interest_expense,
                    "decrease_in_fair_value_of_financial_assets": decrease_fair_value_fa,
                    "transaction_fees_for_financial_assets": transaction_fees_fa,
                    "increase_in_fair_value_of_outstanding_warrants": increase_fair_value_warrants,
                    "loss_from_held_to_maturity_investments": loss_htm,
                    "loss_and_recognition_of_fair_value_difference_of_available_for_sale_financial_assets_upon_reclassification": loss_afs_reclassification,
                    "provisions_for_impairment_of_financial_assets": provisions_impairment,
                    "loss_from_hedging_derivatives": loss_hedging_derivatives,
                    "operating_expense": operating_expense,
                    "brokerage_fees": brokerage_fees,
                    "underwriting_and_bond_issuance_costs": underwriting_costs,
                    "investment_advisory_expenses": investment_advisory_expenses,
                    "securities_custody_expenses": securities_custody_expenses,
                    "financial_advisory_expenses": financial_advisory_expenses,
                    "other_operating_expenses": other_operating_expenses,
                },
                "financial_revenue": {
                    "total_financial_operating_revenue": total_financial_operating_revenue,
                    "increase_decrease_in_fair_value_of_exchange_rate_and_unrealized": exchange_rate_unrealized,
                    "interest_income_from_deposits": interest_income_deposits,
                    "gain_on_disposal_of_investments_in_subsidiaries_associates_and_joint_ventures": gain_disposal_investments,
                    "other_investment_income": other_investment_income,
                },
                "financial_expenses": {
                    "total_financial_expenses": total_financial_expenses,
                    "increase_decrease_in_fair_value_of_exchange_rate_loss": exchange_rate_loss,
                    "interest_expense_on_borrowings": interest_expense_borrowings,
                    "loss_on_disposal_of_investments_in_subsidiaries_associates_and_joint_ventures": loss_disposal_investments,
                    "provision_for_impairment_of_long_term_financial_investments": provision_long_term_investments,
                    "other_financial_expenses": other_financial_expenses,
                },
                "administrative_expenses": {
                    "selling_expenses": selling_expenses,
                    "general_and_administrative_expenses": general_admin_expenses,
                },
                "operational_efficiency": {
                    "ato": ato,
                    "fixed_asset_turnover": fixed_asset_turnover,
                },
            },
            "earnings": {
                "profit_and_tax": {
                    "operating_profit": operating_profit,
                    "other_income": other_income,
                    "other_expenses": other_expenses,
                    "net_other_income_and_expenses": net_other_income_expenses,
                    "accounting_profit_before_tax": accounting_profit_before_tax,
                    "realized_profit": realized_profit,
                    "unrealized_profit_loss": unrealized_profit_loss,
                    "total_corporate_income_tax": total_corporate_income_tax,
                    "current_corporate_income_tax_expense": current_tax_expense,
                    "benefit_from_deferred_income_tax_expense": deferred_tax_benefit,
                    "net_profit_after_tax": net_profit_after_tax,
                    "profit_attributable_to_equity_holders": profit_equity_holders,
                    "profit_after_tax_allocated_to_funds": profit_after_tax_funds,
                    "profit_attributable_to_non_controlling_interests": profit_non_controlling,
                },
                "profit_metrics": {
                    "ebit": ebit,
                    "ebitda": ebitda,
                    "ebit_margin": ebit_margin,
                },
                "profitability_ratios": {
                    "gross_profit_margin": gross_profit_margin,
                    "ros": ros,
                    "roa": roa,
                    "roe": roe,
                },
                "growth_metrics": {"net_profit_growth_rate": net_profit_growth_rate},
            },
            "liquidity": {
                "liquidity_ratios": {
                    "current_ratio": current_ratio,
                    "quick_ratio": quick_ratio,
                    "cash_ratio": cash_ratio,
                    "working_capital": working_capital,
                }
            },
        }

        results.append(result)

    return results


# mlflow.langchain.autolog()
graph = BusinessLoanValidationGraphProvider().provide()
chat_agent = AgentApplication.initialize(graph=graph)
incoming_message = ChatAgentMessage(role="user", content=DNSE_TEST_QUESTION)
response = chat_agent.predict([incoming_message])
print(response)
# mlflow.models.set_model(chat_agent)
