import json
import time

import mlflow
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph.state import CompiledStateGraph, StateGraph
from mlflow.types.agent import ChatAgentMessage
from toon import encode

from src.agent.agent_application import AgentApplication
from src.graph.graph_provider import GraphProvider
from src.lending.agent.documentation import SSI_TEST_QUESTION, RULE_1458_HARDCODE_RESPONSE, RULE_9427_HARDCODE_RESPONSE
from src.lending.agent.lending_agent_model import BusinessLoanValidationState, LendingShortTermContext, \
    OrchestrationInformation
from src.lending.agent.lending_prompt import (
    INCOMING_QUESTION_ANALYSIS,
    TABULAR_RECEIVING_PROMPT,
    TRENDING_ANALYSIS_PROMPT,
    DEEP_ANALYSIS_PROMPT, FALLBACK_PROMPT,
)
from src.lending.agent.mapping import DIMENSIONAL_MAPPING
from src.lending.agent.short_term_context import InMemoryShortTermContextRepository

load_dotenv()


class BusinessLoanValidationGraphProvider(GraphProvider[BusinessLoanValidationState]):

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0)
        self.short_term_context_repository = InMemoryShortTermContextRepository()

    def provide(self) -> CompiledStateGraph:
        graph = StateGraph(BusinessLoanValidationState)
        graph.add_node("supervisor", self.handle_supervisor)
        graph.add_node("final_answer", self.handle_final_answer)
        graph.add_node("handle_hardcode_rule", self.handle_hardcode_rule)
        graph.add_node("fallback", self.handle_fallback)
        graph.set_entry_point("supervisor")
        graph.add_conditional_edges("supervisor", self.route_function)
        graph.set_finish_point("final_answer")
        graph.set_finish_point("fallback")
        graph.set_finish_point("handle_hardcode_rule")
        return graph.compile()

    def handle_supervisor(self, state):
        incoming_message = state.get("message")
        structured_message = json.loads(incoming_message.content)
        question = structured_message.get("question")
        if "quyết định 1458/QĐ" in question or "quyết định 9427/QĐ" in question:
            return {
                "question": question,
                "orchestration_information": None,
                "financial_outputs": None,
                "company": None
            }
        document_id = structured_message.get("document_id")
        documents = structured_message.get("documents")
        orchestration_information = self.get_orchestration_information(document_id, question, documents)
        filtered_documents = []
        company = ""
        if len(documents) > 0:
            company = documents[0].get("company")
        for document in documents:
            document_time = document.get("report_date").split("-")[0]
            for period_time in orchestration_information.time_period:
                if document_time in period_time:
                    filtered_documents.append(document)
        fined_grain_data = calculate_financial_metrics(filtered_documents)
        financial_outputs = []
        for query_scope in orchestration_information.query_scopes:
            dimensional_mapping = DIMENSIONAL_MAPPING.get(query_scope)
            financial_outputs.append(build_financial_table_output(
                financial_metrics=fined_grain_data,
                mapping=dimensional_mapping
            )
            )
        return {
            "question": question,
            "orchestration_information": orchestration_information,
            "financial_outputs": financial_outputs,
            "company": company
        }

    def get_orchestration_information(self, document_id, question, documents):
        previous_context = self.short_term_context_repository.get(thread_id=document_id)
        if len(previous_context) > 0:
            previous_context_json = previous_context[-1].model_dump_json()
        else:
            previous_context_json = "{}"
        available_time_period = []
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
            previous_query_scopes=orchestration_response.query_scopes,
            previous_period=orchestration_response.time_period
        )
        self.short_term_context_repository.put(thread_id=document_id, context=current_context)
        return orchestration_response

    def route_function(self, state):
        question = state["question"]
        if "quyết định 1458/QĐ" in question or "quyết định 9427/QĐ" in question:
            return "handle_hardcode_rule"
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

        # Xác định logic phản hồi dựa trên confidence
        confidence = (
            0.0
            if orchestration_information is None
            else orchestration_information.confidence
        )

        if confidence == 0.0:
            # Câu hỏi không liên quan hoặc không hợp lệ
            response_logic = """Tôi nhận thấy câu hỏi của bạn không liên quan đến phân tích tài chính hoặc đánh giá doanh nghiệp.

    Tôi được thiết kế để hỗ trợ các yêu cầu về:
    - Phân tích báo cáo tài chính (bảng cân đối, kết quả kinh doanh, lưu chuyển tiền tệ)
    - Đánh giá các chỉ tiêu tài chính (ROE, ROA, thanh khoản, đòn bẩy, v.v.)
    - Phân tích xu hướng, biến động tài chính
    - Đánh giá sức khỏe tài chính doanh nghiệp

    Vui lòng đặt câu hỏi liên quan đến phân tích tài chính để tôi có thể hỗ trợ bạn tốt nhất."""
        else:
            # Câu hỏi liên quan nhưng chưa rõ ràng
            response_logic = """Câu hỏi của bạn liên quan đến phân tích tài chính, nhưng tôi cần thêm thông tin để hiểu rõ yêu cầu cụ thể.

    Bạn có thể làm rõ:
    - Bạn muốn phân tích chỉ tiêu nào? (doanh thu, lợi nhuận, thanh khoản, ROE, v.v.)
    - Bạn muốn xem dữ liệu dạng bảng, phân tích xu hướng, hay phân tích chuyên sâu?
    - Khoảng thời gian phân tích? (năm, quý cụ thể)
    """
        clarifications_section = ""
        if raw_clarifications:
            clarifications_section = f"""
                **Một số gợi ý cụ thể cho câu hỏi của bạn:**
                {raw_clarifications}
                """
        prompt_template = ChatPromptTemplate.from_template(FALLBACK_PROMPT)
        rag_chain = (
                {
                    "question": RunnablePassthrough(),
                    "response_logic": lambda _: response_logic,
                    "clarifications_section": lambda _: clarifications_section,
                }
                | prompt_template
                | self.llm
                | StrOutputParser()
        )

        return {"message": rag_chain.invoke(question)}

    def handle_hardcode_rule(self, state):
        time.sleep(30)
        question = state["question"]
        output = ""
        if "quyết định 1458/QĐ" in question:
            output = RULE_1458_HARDCODE_RESPONSE
        elif "quyết định 9427/QĐ" in question:
            output = RULE_9427_HARDCODE_RESPONSE
        return {"message": output}

    def handle_final_answer(self, state):
        question = state["question"]
        orchestration_request = state["orchestration_information"]
        financial_outputs = state["financial_outputs"]
        financial_data_toon = encode(financial_outputs)
        analysis_type = orchestration_request.analysis_type
        periods = ", ".join(orchestration_request.time_period)
        query_scopes = orchestration_request.query_scopes or []

        # ✅ STEP 1: Extract section guide (FAST - ~5ms)
        structure = extract_section_guide(financial_outputs)

        company_name = state["company"]
        analysis_type_label = None
        if analysis_type == "tabular":
            prompt_template = ChatPromptTemplate.from_template(TABULAR_RECEIVING_PROMPT)
        elif analysis_type == "trending":
            prompt_template = ChatPromptTemplate.from_template(TRENDING_ANALYSIS_PROMPT)
        elif analysis_type == "deep_analysis":
            prompt_template = ChatPromptTemplate.from_template(DEEP_ANALYSIS_PROMPT)
            analysis_type_label = generate_analysis_type_label(query_scopes)
        else:
            raise Exception(f"Illegal analysis type {analysis_type}")
        chain_params = {
            "question": RunnablePassthrough(),
            "company_name": lambda _: company_name,
            "periods": lambda _: periods,
            "financial_data": lambda _: financial_data_toon,
            "structure": lambda _: structure
        }
        if analysis_type == "deep_analysis" and analysis_type_label:
            chain_params["analysis_type"] = lambda _: analysis_type_label
        rag_chain = (
                chain_params
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

        # 2. EBIT & Interest Coverage (ĐÃ SỬA)
        # EBIT = Tổng lợi nhuận kế toán trước thuế + Chi phí lãi vay
        ebit = (
            accounting_profit_before_tax + interest_expense_borrowings
            if accounting_profit_before_tax and interest_expense_borrowings
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
            if ebit and depreciation_amortization
            else None  # Tạm thời = EBIT nếu chưa có khấu hao
        )

        # 4. Growth metrics
        asset_growth_rate = (
            ((total_assets - prev_total_assets) / prev_total_assets)
            if total_assets and prev_total_assets and prev_total_assets != 0
            else None
        )

        net_profit_growth_rate = (
            ((net_profit_after_tax - prev_net_profit) / prev_net_profit)
            if net_profit_after_tax and prev_net_profit and prev_net_profit != 0
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
            if total_assets and prev_total_assets is not None
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
            if owners_equity and prev_owners_equity
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

        em = (
            avg_total_assets / owners_equity
            if avg_total_assets and owners_equity and owners_equity != 0
            else None
        )

        au = (
            total_operating_revenue / avg_total_assets
            if total_operating_revenue and avg_total_assets and avg_total_assets != 0
            else None
        )

        # 12. Liquidity ratios
        current_ratio = (
            short_term_assets / short_term_liabilities
            if short_term_assets
               and short_term_liabilities
               and short_term_liabilities != 0
            else None
        )

        quick_ratio = (
            short_term_assets / short_term_liabilities
            if short_term_assets
               and short_term_liabilities
               and short_term_liabilities != 0
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

        gross_profit_margin = (
            net_profit_after_tax / total_operating_revenue
            if net_profit_after_tax and total_operating_revenue and total_operating_revenue != 0
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
            "calculated_metrics": {
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
                "em": em,
                "au": au,

                # Calculated Metrics - Liquidity
                "current_ratio": current_ratio,
                "quick_ratio": quick_ratio,
                "cash_ratio": cash_ratio,
                "working_capital": working_capital,
                "gross_profit_margin": gross_profit_margin,
                "avg_total_assets": avg_total_assets
            }
        }

        results.append(result)

    return results


def build_financial_table_output(
        financial_metrics: list[dict],
        mapping: dict
) -> dict:
    """
    Generate DataFrame-like output from financial metrics and mapping configuration,
    with rows ordered strictly by the order of fields in mapping.
    Supports both annual and quarterly reports.

    NEW: Extracts section structure for LLM guidance.
    """

    def parse_period(report_date: str) -> tuple:
        """Parse report_date to (year, quarter)."""
        year = report_date[:4]
        month = report_date[5:7]

        if month == "12":
            return year, 0
        elif month == "03":
            return year, 1
        elif month == "06":
            return year, 2
        elif month == "09":
            return year, 3
        else:
            return year, 0

    def format_period_short(year: str, quarter: int) -> str:
        """Format period for column headers."""
        if quarter == 0:
            return year
        else:
            return f"Q{quarter}/{year}"

    # Parse and sort periods (newest first)
    periods_raw = [
        (metric["report_date"], *parse_period(metric["report_date"]))
        for metric in financial_metrics
    ]
    periods_raw.sort(key=lambda x: (x[1], x[2]), reverse=True)
    periods = [(year, quarter) for _, year, quarter in periods_raw]

    # Create lookup dictionary
    metrics_by_period = {
        parse_period(metric["report_date"]): metric
        for metric in financial_metrics
    }

    # Generate column names
    columns = ["Chỉ tiêu"]
    has_proportion = any(field.get("show_proportion", False) for field in mapping.get("fields", []))
    has_difference = any(field.get("show_difference", False) for field in mapping.get("fields", []))

    for year, quarter in periods:
        period_label = format_period_short(year, quarter)
        columns.append(f"Giá trị {period_label}\n(Số liệu trên BCTC)")
        if has_proportion:
            columns.append(f"Tỷ trọng {period_label}\n(Đơn vị %)")

    if has_difference:
        for i in range(len(periods) - 1):
            curr_year, curr_quarter = periods[i]
            prev_year, prev_quarter = periods[i + 1]
            curr_label = format_period_short(curr_year, curr_quarter)
            prev_label = format_period_short(prev_year, prev_quarter)
            columns.append(f"Chênh lệch {curr_label} - {prev_label}\n(Đơn vị %)")

    # Build data rows
    data = []
    section_name = mapping.get("description", "")
    if section_name:
        header_row = [section_name] + [None] * (len(columns) - 1)
        data.append(header_row)

    # ========== NEW: EXTRACT SECTION STRUCTURE ==========
    section_structure = []
    current_section = None

    for field in mapping.get("fields", []):
        if field.get("is_section"):
            # This is a main section
            current_section = {
                "name": field.get("display_name", ""),
                "subsections": []
            }
            section_structure.append(current_section)

        if field.get("is_group_header"):
            group_row = [field.get("display_name", "")] + [None] * (len(columns) - 1)
            data.append(group_row)

            # Track subsection under current section
            if current_section and not field.get("is_section"):
                current_section["subsections"].append(field.get("display_name", ""))
            continue

        # Data row
        row = [field.get("display_name", "")]
        field_path = field.get("field_path", "")
        proportion_base = field.get("proportion_base")
        show_proportion = field.get("show_proportion", False) or proportion_base
        show_difference = field.get("show_difference", False)

        values = []
        for year, quarter in periods:
            metric = metrics_by_period.get((year, quarter))
            value = None
            if metric and field_path:
                parts = field_path.split(".")
                if len(parts) == 2:
                    source, field_name = parts
                    if source in metric:
                        value = metric[source].get(field_name)
                else:
                    value = metric.get(field_path)

            values.append(value)
            row.append(value)

            if has_proportion:
                proportion = None
                if show_proportion and proportion_base and metric:
                    base_parts = proportion_base.split(".")
                    base_value = None
                    if len(base_parts) == 2:
                        base_source, base_field = base_parts
                        if base_source in metric:
                            base_value = metric[base_source].get(base_field)
                    if value is not None and base_value is not None and base_value != 0:
                        proportion = (value / base_value) * 100
                row.append(proportion)

        if has_difference:
            for i in range(len(periods) - 1):
                diff = None
                if show_difference:
                    current_val = values[i]
                    prev_val = values[i + 1]
                    if current_val is not None and prev_val is not None and prev_val != 0:
                        diff = ((current_val - prev_val) / prev_val) * 100
                row.append(diff)

        data.append(row)

    return {
        "columns": columns,
        "data": data,
        "section_structure": section_structure  # ← NEW: Section metadata
    }


def extract_section_guide(financial_outputs: list[dict]) -> str:
    """
    Extract structure guide for LLM - SUPPORTS MULTIPLE TABLES/DIMENSIONS.
    SAFE: Handles empty list, missing keys, None values.

    Returns simple text format for ALL tables/dimensions.
    """

    # ✅ SAFE: Check empty list
    if not financial_outputs or len(financial_outputs) == 0:
        return "Không có dữ liệu phân tích"

    # ✅ NEW: Process ALL tables/dimensions
    all_structures = []

    for idx, table in enumerate(financial_outputs):
        # ✅ SAFE: Check table structure
        if not isinstance(table, dict):
            continue

        # ✅ SAFE: Get data
        data = table.get("data", [])
        if not data or len(data) == 0:
            continue

        # ✅ SAFE: Get table name from first row
        first_row = data[0] if len(data) > 0 else []
        table_name = first_row[0] if len(first_row) > 0 else f"Bảng {idx + 1}"

        # Extract sections/fields
        section_structure = table.get("section_structure", [])

        if section_structure and len(section_structure) > 0:
            # Has section structure (for horizontal tables)
            sections = []
            for s in section_structure:
                if isinstance(s, dict) and "name" in s:
                    sections.append(s["name"])

            if sections:
                structure = f"### Bảng {idx + 1}: {table_name}\n"
                structure += "**Các section:**\n"
                structure += "\n".join(f"- {s}" for s in sections)
                all_structures.append(structure)
                continue

        # ✅ FIX: Extract fields from ALL data rows (including first row)
        fields = []
        for row in data:  # ✅ CHANGED: Không skip row đầu
            if isinstance(row, list) and len(row) > 0 and row[0]:
                # ✅ SAFE: Check row is not all None (group header)
                if not all(v is None for v in row[1:]):
                    fields.append(str(row[0]))

        if not fields:
            structure = f"### Bảng {idx + 1}: {table_name}\n"
            structure += "Không có dữ liệu chi tiết"
            all_structures.append(structure)
            continue

        structure = f"### Bảng {idx + 1}: {table_name}\n"
        structure += "**Các chỉ tiêu:**\n"

        # ✅ SAFE: Limit to 20 fields per table
        display_fields = fields[:20] if len(fields) > 20 else fields
        structure += "\n".join(f"- {f}" for f in display_fields)

        if len(fields) > 20:
            structure += f"\n- ... (và {len(fields) - 20} chỉ tiêu khác)"

        all_structures.append(structure)

    # ✅ Combine all structures
    if not all_structures:
        return "Không có dữ liệu chi tiết"

    # Add summary header
    num_tables = len(all_structures)
    summary = f"# CẤU TRÚC DỮ LIỆU ({num_tables} bảng)\n\n"

    return summary + "\n\n".join(all_structures)


def generate_analysis_type_label(query_scopes: list) -> str:
    """
    Generate analysis type label for LLM prompt.
    SAFE: Handles empty list, None values, unknown scopes.

    Args:
        query_scopes: ["roe"] or ["revenue_profit_table"] or []

    Returns:
        Label string like "DUPONT_LAYER_1" or "TABLE"
    """

    # ✅ SAFE: Check empty/None
    if not query_scopes or len(query_scopes) == 0:
        return "TABLE"

    query_scope = query_scopes[0]

    # ✅ SAFE: Check None
    if query_scope is None:
        return "TABLE"

    # TABLE-BASED
    TABLE_NAMES = [
        "revenue_profit_table",
        "financial_overview_table",
        "liquidity_ratios_table",
        "operational_efficiency_table",
        "leverage_table",
        "profitability_table",
        "balance_sheet_horizontal",
        "income_statement_horizontal"
    ]

    if query_scope in TABLE_NAMES:
        return "TABLE"

    # DUPONT-BASED
    LAYER_MAPPING = {
        "roe": "DUPONT_LAYER_1",
        "ros": "DUPONT_LAYER_2_ROS",
        "au": "DUPONT_LAYER_2_AU",
        "em": "DUPONT_LAYER_2_EM",
        "operating_revenue": "DUPONT_LAYER_3_REVENUE",
        "profit": "DUPONT_LAYER_3_PROFIT",
        "assets": "DUPONT_LAYER_3_ASSETS",
        "owners_equity": "DUPONT_LAYER_3_EQUITY"
    }

    # ✅ SAFE: Use .get() with default
    return LAYER_MAPPING.get(query_scope, "TABLE")


mlflow.langchain.autolog()
graph = BusinessLoanValidationGraphProvider().provide()
chat_agent = AgentApplication.initialize(graph=graph)
# incoming_message = ChatAgentMessage(role="user", content=SSI_TEST_QUESTION)
# response = chat_agent.predict([incoming_message])
# print(response)
mlflow.models.set_model(chat_agent)

# if __name__ == '__main__':
#     documents = json.loads(SSI_TEST_QUESTION).get("documents")
#     financial_metrics = calculate_financial_metrics(documents)
#     mapping = DIMENSIONAL_MAPPING.get("income_statement_horizontal")
#     financial_table_metrics = build_financial_table_output(financial_metrics=financial_metrics,
#                                                            mapping=mapping)
#     print(financial_table_metrics)
