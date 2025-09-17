import os
import uuid
from typing import Any

from langchain_chroma import Chroma
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

os.environ["GOOGLE_API_KEY"] = "MAY_THANG_HACKER_NGHI_TAO_NGU_MA_POST_TOKEN_AH"


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
        embedding = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url="http://localhost:11434"
        )
        # embedding = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        # Test the model
        print(embedding.embed_query("test connection"))
        print("✅ Successfully loaded embedding model")
        self.embedding = embedding
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
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

mlflow.langchain.autolog()
chat_agent = Demo0ChatAgent(graph=Demo0GraphProvider())
mlflow.models.set_model(chat_agent)
