import os
import uuid
from typing import Any, List

import mlflow
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from langgraph.graph.state import CompiledStateGraph, StateGraph
from mlflow.pyfunc import ChatAgent
from mlflow.types.agent import ChatAgentMessage, ChatContext, ChatAgentResponse

from graph.graph_provider import GraphProvider
from state.mapper import StateMapper
from state.type import DefaultState

# os.environ["GOOGLE_API_KEY"] = "MAY_THANG_HACKER_NGHI_TAO_NGU_MA_POST_TOKEN_AH"


def format_docs(docs):
    """Formats a list of document objects into a single string."""
    return "\n\n".join(doc.page_content for doc in docs)


class Demo0DefaultState(DefaultState):
    question: str
    banks: list[str]
    messages: list[str]


class Demo0DefaultStateMapper(StateMapper[DefaultState, list[ChatAgentMessage]]):

    def map_from_state_to_message(self, state: DefaultState) -> list[ChatAgentMessage]:
        message = state.get('message', "")
        content = ""
        if isinstance(message, str):
            content = message
        elif isinstance(message, AIMessage):
            content = message.content
        result = [ChatAgentMessage(role="assistant", content=content, id=str(uuid.uuid4()))]
        return result

    def map_from_message_to_state(self, message: list[ChatAgentMessage]) -> DefaultState:
        actual_message = message[-1].content
        return {"message": HumanMessage(content=actual_message)}


class Demo0GraphProvider(GraphProvider[Demo0DefaultState]):

    def __init__(self):
        # embedding = OllamaEmbeddings(
        #     model="nomic-embed-text",
        #     base_url="http://localhost:11434"
        # )
        embedding = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        # Test the model
        print(embedding.embed_query("test connection"))
        print("✅ Successfully loaded embedding model")
        self.embedding = embedding
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            temperature=0
        )
        self.known_banks = ["LPBANK", "MBBANK", "VPBANK", "TECHCOMBANK"]

    def provide(self) -> CompiledStateGraph:
        graph = StateGraph(Demo0DefaultState)
        graph.add_node("supervisor", self.handle_supervisor)
        graph.add_node("query_single_bank", self.handle_querying_single_bank)
        graph.add_node("compare_banks", self.handle_banking_comparison)
        graph.add_node("fallback", self.fallback)
        graph.set_entry_point("supervisor")
        graph.add_conditional_edges("supervisor", self.route_function)
        graph.set_finish_point("query_single_bank")
        graph.set_finish_point("compare_banks")
        graph.set_finish_point("fallback")

        return graph.compile()

    def extract_bank_names(self, question):
        prompt = f"""
        Trích xuất tên các ngân hàng từ câu hỏi bên dưới. Chỉ trả về những tên có trong danh sách sau:
        {', '.join(self.known_banks)}
        Câu hỏi: "{question}"
        Trả về dưới dạng danh sách các tên ngân hàng, phân cách bằng dấu phẩy.
        """
        response = self.llm.invoke(prompt).content
        return [name.strip().upper() for name in response.split(",") if name.strip().upper() in self.known_banks]

    def handle_supervisor(self, state):
        incoming_message = state.get("message")
        question = incoming_message.content if incoming_message is not None and incoming_message.content is not None else ""
        bank_names = self.extract_bank_names(question)
        return {"question": question, "banks": bank_names}

    def route_function(self, state):
        bank_names = state["banks"]
        if len(bank_names) == 1:
            return "query_single_bank"
        elif len(bank_names) == 2:
            return "compare_banks"
        else:
            return "fallback"

    def handle_banking_comparison(self, state):
        bank1, bank2 = state["banks"]
        current_question = state.get("question", "")
        bank1_db = Chroma(collection_name=bank1,
                          embedding_function=self.embedding,
                          persist_directory='./rawiq_db')
        bank2_db = Chroma(collection_name=bank2,
                          embedding_function=self.embedding,
                          persist_directory='./rawiq_db')
        retriever_1 = RunnableLambda(
            lambda _: bank1_db.similarity_search(f"tóm tắt thông tin kinh doanh {bank1}"))
        retriever_2 = RunnableLambda(
            lambda _: bank2_db.similarity_search(f"tóm tắt thông tin kinh doanh {bank2}"))

        prompt_template = """
        Bạn là một chuyên gia phân tích tài chính ngân hàng với kinh nghiệm phân tích báo cáo tài chính, đánh giá rủi ro và hiệu quả hoạt động của các ngân hàng.

        ## NHIỆM VỤ:
        So sánh và trả lời câu hỏi dựa trên dữ liệu báo cáo tài chính của **hai ngân hàng** được cung cấp.

        ## NGUYÊN TẮC PHÂN TÍCH:
        1. **Độ chính xác**: Chỉ sử dụng dữ liệu có trong báo cáo
        2. **Tính toán**: Hiển thị công thức và cách tính khi cần thiết
        3. **So sánh**: Đối chiếu từng chỉ số giữa hai ngân hàng, nêu rõ sự khác biệt và xu hướng
        4. **Ngữ cảnh**: Đánh giá trong bối cảnh ngành ngân hàng Việt Nam

        ## CÁC CHỈ SỐ TRỌNG TÂM:
        - **Khả năng sinh lời**: ROA, ROE, NIM, CIR
        - **Chất lượng tài sản**: NPL ratio, Provision coverage ratio
        - **Thanh khoản**: LDR, Liquidity coverage ratio
        - **An toàn vốn**: CAR, Tier 1 ratio
        - **Hiệu quả hoạt động**: Cost-to-income ratio, Asset turnover

        ## DỮ LIỆU PHÂN TÍCH:
        ### {bank1}:
        {context_1}

        ### {bank2}:
        {context_2}

        ## CÂU HỎI:
        {question}

        ## YÊU CẦU TRẢ LỜI:
        1. **Trả lời trực tiếp** câu hỏi với số liệu cụ thể của từng ngân hàng
        2. **Giải thích ngắn gọn** ý nghĩa của chỉ số (nếu cần)
        3. **Đánh giá xu hướng** qua các kỳ (nếu có dữ liệu)
        4. **So sánh rõ ràng** giữa hai ngân hàng, nêu ưu/nhược điểm
        5. **Nhận xét** về mức độ tốt/xấu so với chuẩn ngành (nếu phù hợp)

        ## LƯU Ý:
        - Nếu thiếu thông tin: "Dữ liệu không đủ để phân tích [chỉ số cụ thể]"
        - Số liệu phải chính xác 100%, không ước tính
        - Sử dụng đơn vị và format phù hợp (%, tỷ VND, lần...)
        - Tránh đưa ra lời khuyên đầu tư cụ thể

        Hãy phân tích và trả lời:
        """
        prompt = ChatPromptTemplate.from_template(prompt_template)
        from langchain_core.output_parsers import StrOutputParser

        rag_chain = (
                {
                    "context_1": retriever_1 | format_docs,
                    "context_2": retriever_2 | format_docs,
                    "question": RunnablePassthrough(),
                    "bank1": RunnableLambda(lambda _: bank1),
                    "bank2": RunnableLambda(lambda _: bank2)
                }
                | prompt
                | self.llm
                | StrOutputParser()
        )
        return {"message": rag_chain.invoke(current_question)}

    def handle_querying_single_bank(self, state):
        bank1 = state['banks'][0]
        bank1_db = Chroma(collection_name=bank1,
                          embedding_function=self.embedding,
                          persist_directory='./rawiq_db')
        retriever = bank1_db.as_retriever(search_type="similarity")
        # Prompt template
        prompt = """
        Bạn là một chuyên gia phân tích tài chính ngân hàng với kinh nghiệm phân tích báo cáo tài chính, đánh giá rủi ro và hiệu quả hoạt động của các ngân hàng.

        ## NHIỆM VỤ:
        Phân tích và trả lời câu hỏi dựa trên dữ liệu báo cáo tài chính được cung cấp.

        ## NGUYÊN TẮC PHÂN TÍCH:
        1. **Độ chính xác**: Chỉ sử dụng dữ liệu có trong báo cáo
        2. **Tính toán**: Hiển thị công thức và cách tính khi cần thiết
        3. **So sánh**: Đưa ra nhận xét về xu hướng qua các kỳ (nếu có)
        4. **Ngữ cảnh**: Đánh giá trong bối cảnh ngành ngân hàng Việt Nam

        ## CÁC CHỈ SỐ TRỌNG TÂM:
        - **Khả năng sinh lời**: ROA, ROE, NIM, CIR
        - **Chất lượng tài sản**: NPL ratio, Provision coverage ratio
        - **Thanh khoản**: LDR, Liquidity coverage ratio
        - **An toàn vốn**: CAR, Tier 1 ratio
        - **Hiệu quả hoạt động**: Cost-to-income ratio, Asset turnover

        ## DỮ LIỆU PHÂN TÍCH:
        {context}

        ## CÂU HỎI:
        {question}

        ## YÊU CẦU TRẢ LỜI:
        1. **Trả lời trực tiếp** câu hỏi với số liệu cụ thể
        2. **Giải thích ngắn gọn** ý nghĩa của chỉ số (nếu cần)
        3. **Đánh giá xu hướng** qua các kỳ (nếu có dữ liệu)
        4. **Nhận xét** về mức độ tốt/xấu so với chuẩn ngành (nếu phù hợp)

        ## LƯU Ý:
        - Nếu thiếu thông tin: "Dữ liệu không đủ để phân tích [chỉ số cụ thể]"
        - Số liệu phải chính xác 100%, không ước tính
        - Sử dụng đơn vị và format phù hợp (%, tỷ VND, lần...)
        - Tránh đưa ra lời khuyên đầu tư cụ thể

        Hãy phân tích và trả lời:
        """

        prompt_template = ChatPromptTemplate.from_template(prompt)
        # Build RAG chain
        rag_chain = (
                {"context": retriever | format_docs, "question": RunnablePassthrough()}
                | prompt_template
                | self.llm
                | StrOutputParser()
        )
        current_question = state.get("question", "")
        return {"message": rag_chain.invoke(current_question)}

    def fallback(self, state):
        question = state["question"]
        prompt = f"""Tôi chưa xác định được rõ yêu cầu của bạn. Bạn có thể làm rõ thêm câu hỏi sau không?
        Câu hỏi: {question}"""
        return {"message": self.llm.invoke(prompt)}


class Demo0ChatAgent(ChatAgent):

    def __init__(self, graph: GraphProvider):
        self.graph = graph
        self.mapper = Demo0DefaultStateMapper()

    def predict(self, messages: list[ChatAgentMessage], context: ChatContext | None = None,
                custom_inputs: dict[str, Any] | None = None) -> ChatAgentResponse:
        input_state = self.mapper.map_from_message_to_state(messages)
        state = self.graph.provide().invoke(input_state)
        result = self.mapper.map_from_state_to_message(state)
        return ChatAgentResponse(messages=result)


# graph2 = Demo0ChatAgent(graph=Demo0GraphProvider())
# incoming_message = ChatAgentMessage(role="user", content="so sánh kết quả kinh doanh LPBank và MBBank năm 2024")
# test_result = graph2.predict(messages=[incoming_message])
# print(test_result)
def query_context_with_metadata(db, query_terms: List[str], year: int = 2024,
                                k: int = 10):
    """
    Query vector DB với metadata filter và multiple query terms
    """
    all_results = []

    for query_term in query_terms:
        try:
            # Query với metadata filter
            results = db.similarity_search(
                query=query_term,
                k=k,
                filter={"year": year}  # Filter theo năm trong metadata
            )
            all_results.extend(results)
        except Exception as e:
            print(f"Error querying '{query_term}': {e}")
            continue
    return format_docs(all_results)


def handle_querying_single_bank():
    embedding = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    # Test the model
    print(embedding.embed_query("test connection"))
    print("✅ Successfully loaded embedding model")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        temperature=0
    )
    bank_db = Chroma(collection_name="shb",
                     embedding_function=embedding,
                     persist_directory='./rawiq_db')
    context_queries = {
        "balance_sheet": [
            "BÁO CÁO TÌNH HÌNH TÀI CHÍNH HỢP NHẤT",
            "Bảng cân đối kế toán",
            "tài sản có",
            "nợ phải trả",
            "vốn chủ sở hữu"
        ],
        "income_statement": [
            "BÁO CÁO KẾT QUẢ HOẠT ĐỘNG HỢP NHẤT",
            "thu nhập lãi thuần",
            "chi phí hoạt động",
            "lợi nhuận",
            "chi phí dự phòng"
        ],
        "cash_flow": [
            "BÁO CÁO LƯU CHUYỂN TIỀN TỆ HỢP NHẤT",
            "hoạt động kinh doanh",
            "hoạt động đầu tư",
            "hoạt động tài chính"
        ],
        "off_balance": [
            "CÁC CHỈ TIÊU NGOÀI BÁO CÁO TÌNH HÌNH TÀI CHÍNH",
            "bảo lãnh",
            "cam kết",
            "công cụ tài chính phái sinh"
        ]
    }
    balance_sheet = query_context_with_metadata(db=bank_db, query_terms=context_queries.get("balance_sheet"), year=2023)
    income_statement = query_context_with_metadata(db=bank_db, query_terms=context_queries.get("income_statement"), year=2023)
    cash_flow = query_context_with_metadata(db=bank_db, query_terms=context_queries.get("cash_flow"), year=2023)
    off_balance = query_context_with_metadata(db=bank_db, query_terms=context_queries.get("off_balance"), year=2023)

    # Prompt template
    prompt = """
    Bạn là một chuyên gia phân tích tài chính ngân hàng chuyên nghiệp. Nhiệm vụ của bạn là phân tích các báo cáo tài chính được cung cấp từ vector search và trích xuất thông số theo mô hình đánh giá CAMELS.

## NGUYÊN TẮC QUAN TRỌNG:
- CHỈ sử dụng dữ liệu từ năm báo cáo được chỉ định
- CHỈ lấy số liệu có sẵn trong báo cáo, KHÔNG tự suy diễn
- Nếu không tìm thấy thông tin, ghi "null"
- Đơn vị: giữ nguyên như trong báo cáo gốc
- Trả về format JSON chuẩn

## CONTEXT TỪ VECTOR SEARCH:

**Context 1 - Bảng Cân đối Kế toán:**
{balance_sheet}

**Context 2 - Báo cáo Kết quả Kinh doanh:**
{income_statement}

**Context 3 - Báo cáo Lưu chuyển Tiền tệ:**
{cash_flow}

**Context 4 - Các chỉ tiêu ngoài BCTC:**
{off_balance}

## YÊU CẦU TRÍCH XUẤT:

Dựa trên các context trên, hãy trích xuất dữ liệu theo mô hình CAMELS và trả về JSON với cấu trúc sau:
```json
{{
  "CAPITAL_ADEQUACY": {{
    "total_equity": null,
    "charter_capital": null,
    "share_premium": null,
    "reserves": null,
    "retained_earnings": null,
    "treasury_shares": null,
    "total_assets": null,
    "net_profit_after_tax": null,
    "foreign_exchange_differences": null
  }},

  "ASSET_QUALITY": {{
    "gross_loans_to_customers": null,
    "loan_loss_provision": null,
    "net_loans_to_customers": null,
    "interbank_deposits_loans": null,
    "trading_securities_gross": null,
    "trading_securities_provision": null,
    "investment_securities_afs": null,
    "investment_securities_htm": null,
    "investment_securities_provision": null,
    "long_term_investments": null,
    "fixed_assets_net": null,
    "other_assets": null,
    "interest_and_fees_receivable": null
  }},

  "MANAGEMENT_EFFICIENCY": {{
    "total_operating_expenses": null,
    "staff_costs": null,
    "general_admin_expenses": null,
    "depreciation_amortization": null,
    "other_operating_expenses": null,
    "net_interest_income": null,
    "net_fee_income": null,
    "fx_trading_income": null,
    "securities_trading_income": null,
    "other_operating_income": null,
    "total_operating_income": null
  }},

  "EARNINGS_PROFITABILITY": {{
    "gross_interest_income": null,
    "interest_expenses": null,
    "net_interest_income": null,
    "fee_and_commission_income": null,
    "fee_and_commission_expenses": null,
    "net_trading_income": null,
    "other_income": null,
    "total_operating_income": null,
    "provision_expenses": null,
    "profit_before_tax": null,
    "income_tax_expense": null,
    "net_profit_after_tax": null,
    "earnings_per_share": null
  }},

  "LIQUIDITY_RISK": {{
    "cash_and_cash_equivalents": null,
    "deposits_with_central_bank": null,
    "interbank_deposits": null,
    "interbank_loans": null,
    "trading_securities_net": null,
    "investment_securities_liquid": null,
    "customer_deposits": null,
    "interbank_borrowings": null,
    "issued_debt_securities": null,
    "other_borrowed_funds": null,
    "payables_and_accruals": null
  }},

  "OFF_BALANCE_SHEET": {{
    "loan_commitments": null,
    "guarantees_issued": null,
    "letters_of_credit": null,
    "derivative_instruments": null,
    "contingent_liabilities": null
  }},

  "REPORT_METADATA": {{
    "report_year": null,
    "report_period": null,
    "bank_name": null,
    "currency_unit": null,
    "consolidated_report": null,
    "extraction_date": null
  }}
}}
Chỉ trả về JSON hợp lệ, không cần giải thích thêm.

## QUESTION: {question}
    """
    prompt = ((prompt.replace("{balance_sheet}", balance_sheet).
               replace("{income_statement}", income_statement)).
              replace("{cash_flow}", cash_flow).
              replace("{off_balance}", off_balance))

    prompt_template = ChatPromptTemplate.from_template(prompt)

    # 3. Tạo chain
    chain = ({"question": RunnablePassthrough()} |
             prompt_template
             | llm
             | StrOutputParser()
             )
    return chain.invoke("trích xuất các chỉ số CAMELS cho SHB")


result = handle_querying_single_bank()
print(result)
# mlflow.langchain.autolog()
# chat_agent = Demo0ChatAgent(graph=Demo0GraphProvider())
# mlflow.models.set_model(chat_agent)
