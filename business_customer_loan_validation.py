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
from src.bidv.agent.lending_agent_model import BusinessLoanValidationState, LendingShortTermContext, \
    OrchestrationInformation
from src.bidv.agent.lending_prompt import (
    INCOMING_QUESTION_ANALYSIS,
    OVERALL_ANALYSIS_PROMPT,
    TRENDING_ANALYSIS_PROMPT,
    DEEP_ANALYSIS_PROMPT,
)
from src.bidv.agent.short_term_context import InMemoryShortTermContextRepository
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
        fined_grain_data = calculate_financial_metrics(filtered_documents)
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


def calculate_financial_metrics(data):
    """
    Tính toán các chỉ số tài chính từ dữ liệu raw với công thức đã FIX
    Input: list of dictionaries
    Output: list of dictionaries gồm:
        - Metadata (company, report_date, currency)
        - financial_statement: dict chứa tất cả fields từ financial_statement
        - income_statement: dict chứa tất cả fields từ income_statement
        - Calculated metrics
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

        def get_all_fields(report_name):
            """Lấy tất cả fields từ một report dưới dạng dict"""
            result_dict = {}
            for r in report.get("reports", []):
                if r["report_name"] == report_name:
                    for field in r.get("fields", []):
                        result_dict[field["name"]] = field["value"]
            return result_dict

        # ============ LẤY TOÀN BỘ FINANCIAL_STATEMENT & INCOME_STATEMENT ============
        financial_statement_data = get_all_fields("financial_statement")
        income_statement_data = get_all_fields("income_statement")

        # ============ LẤY GIÁ TRỊ ĐỂ TÍNH TOÁN ============
        total_assets = financial_statement_data.get("total_assets")
        total_liabilities = financial_statement_data.get("liabilities")
        short_term_liabilities = financial_statement_data.get("short_term_liabilities")
        long_term_liabilities = financial_statement_data.get("long_term_liabilities")
        owners_equity = financial_statement_data.get("owners_equity")
        receivables = financial_statement_data.get("receivables")
        short_term_assets = financial_statement_data.get("short_term_assets")
        cash_and_cash_equivalents = financial_statement_data.get("cash_and_cash_equivalents")

        total_operating_revenue = income_statement_data.get("total_operating_revenue")
        interest_expense_borrowings = income_statement_data.get("interest_expense_on_borrowings")
        operating_profit = income_statement_data.get("operating_profit")
        accounting_profit_before_tax = income_statement_data.get("accounting_profit_before_tax")
        net_profit_after_tax = income_statement_data.get("net_profit_after_tax")

        # ============ GIÁ TRỊ NĂM TRƯỚC ============
        prev_total_assets = get_prev_value("financial_statement", "total_assets")
        prev_owners_equity = get_prev_value("financial_statement", "owners_equity")
        prev_net_profit = get_prev_value("income_statement", "net_profit_after_tax")

        # ============ TÍNH TOÁN CÁC CHỈ SỐ ============

        # 1. Debt management ratios
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

        # 2. EBIT & Interest Coverage (ĐÃ SỬA)
        # EBIT = Tổng lợi nhuận kế toán trước thuế + Chi phí lãi vay
        ebit = (
            accounting_profit_before_tax + interest_expense_borrowings
            if accounting_profit_before_tax is not None and interest_expense_borrowings is not None
            else None
        )

        interest_coverage_ratio = (
            ebit / interest_expense_borrowings
            if ebit and interest_expense_borrowings and interest_expense_borrowings != 0
            else None
        )

        # 3. EBITDA (ĐÃ SỬA - CẦN BỔ SUNG KHẤU HAO TỪ CASHFLOW)
        # EBITDA = EBIT + Khấu hao
        # TODO: Cần lấy khấu hao từ báo cáo lưu chuyển tiền tệ
        depreciation_amortization = None  # Placeholder - cần get từ cashflow report
        ebitda = (
            ebit + depreciation_amortization
            if ebit is not None and depreciation_amortization is not None
            else ebit  # Tạm thời = EBIT nếu chưa có khấu hao
        )

        # 4. Growth metrics
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

        # 5. Asset turnover metrics
        receivables_turnover = (
            total_operating_revenue / receivables
            if total_operating_revenue and receivables and receivables != 0
            else None
        )

        # 6. ATO (ĐÃ SỬA)
        # ATO = Tổng doanh thu hoạt động / Tổng tài sản bình quân
        avg_total_assets = (
            (total_assets + prev_total_assets) / 2
            if total_assets is not None and prev_total_assets is not None
            else None
        )

        ato = (
            total_operating_revenue / avg_total_assets
            if total_operating_revenue and avg_total_assets and avg_total_assets != 0
            else None
        )

        # 7. Fixed asset turnover
        fixed_asset_turnover = None  # Chưa có TSCĐ trong input

        # 8. Profit margins
        ebit_margin = (
            ebit / total_operating_revenue
            if ebit and total_operating_revenue and total_operating_revenue != 0
            else None
        )

        operating_profit_margin = (
            operating_profit / total_operating_revenue
            if operating_profit and total_operating_revenue and total_operating_revenue != 0
            else None
        )

        # 9. ROA (ĐÃ SỬA)
        # ROA = Tổng lợi nhuận kế toán sau thuế / Tổng tài sản bình quân
        roa = (
            net_profit_after_tax / avg_total_assets
            if net_profit_after_tax and avg_total_assets and avg_total_assets != 0
            else None
        )

        # 10. ROE (ĐÃ SỬA)
        # ROE = Tổng lợi nhuận kế toán sau thuế / Tổng vốn chủ sở hữu bình quân
        avg_owners_equity = (
            (owners_equity + prev_owners_equity) / 2
            if owners_equity is not None and prev_owners_equity is not None
            else None
        )

        roe = (
            net_profit_after_tax / avg_owners_equity
            if net_profit_after_tax and avg_owners_equity and avg_owners_equity != 0
            else None
        )

        # 11. ROS
        ros = (
            net_profit_after_tax / total_operating_revenue
            if net_profit_after_tax and total_operating_revenue and total_operating_revenue != 0
            else None
        )

        # 12. Liquidity ratios
        current_ratio = (
            short_term_assets / short_term_liabilities
            if short_term_assets and short_term_liabilities and short_term_liabilities != 0
            else None
        )

        quick_ratio = (
            short_term_assets / short_term_liabilities
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

        # ============ OUTPUT: METADATA + RAW DATA + METRICS ============
        result = {
            # Metadata
            "company": report["company"],
            "report_date": report["report_date"],
            "currency": report["currency"],

            # Raw data components
            "financial_statement": financial_statement_data,
            "income_statement": income_statement_data,

            # Calculated Metrics - Debt Management
            "debt_to_equity": debt_to_equity,
            "leverage_ratio": leverage_ratio,
            "debt_ratio": debt_ratio,
            "long_term_debt_to_equity": long_term_debt_to_equity,
            "interest_coverage_ratio": interest_coverage_ratio,

            # Calculated Metrics - Growth
            "asset_growth_rate": asset_growth_rate,
            "net_profit_growth_rate": net_profit_growth_rate,

            # Calculated Metrics - Efficiency
            "receivables_turnover": receivables_turnover,
            "ato": ato,
            "fixed_asset_turnover": fixed_asset_turnover,

            # Calculated Metrics - Profitability
            "ebit": ebit,
            "ebitda": ebitda,
            "ebit_margin": ebit_margin,
            "operating_profit_margin": operating_profit_margin,
            "roa": roa,
            "roe": roe,
            "ros": ros,

            # Calculated Metrics - Liquidity
            "current_ratio": current_ratio,
            "quick_ratio": quick_ratio,
            "cash_ratio": cash_ratio,
            "working_capital": working_capital,
        }

        results.append(result)

    return results


mlflow.langchain.autolog()
graph = BusinessLoanValidationGraphProvider().provide()
chat_agent = AgentApplication.initialize(graph=graph)
mlflow.models.set_model(chat_agent)
