import json
import uuid
from typing import Any, List

import mlflow
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph.state import CompiledStateGraph, StateGraph
from mlflow.pyfunc import ChatAgent
from mlflow.types.agent import ChatAgentMessage, ChatContext, ChatAgentResponse

from banking_formular import CapitalAdequacyCalculator, AssetQualityCalculator, ManagementCompetenceCalculator, \
    EarningStrengthCalculator
from graph.graph_provider import GraphProvider
from state.mapper import StateMapper
from state.type import DefaultState


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


def format_docs(docs):
    """Formats a list of document objects into a single string."""
    return "\n\n".join(doc.page_content for doc in docs)


class Demo0EnhancedState(DefaultState):
    question: str
    question_topic: str
    banks: list[str]
    source_bank: str
    dest_banks: list[str]


class Demo0EnhancedStateMapper(StateMapper[DefaultState, list[ChatAgentMessage]]):

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


class Demo0EnhancedGraphProvider(GraphProvider[Demo0EnhancedState]):

    def __init__(self):
        # embedding = OllamaEmbeddings(
        #     model="nomic-embed-text",
        #     base_url="http://localhost:11434"
        # )
        # embedding = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        # Test the model
        # self.embedding = embedding
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            temperature=0
        )
        self.known_banks = ["SHB", "MBB", "VPB", "TCB"]

    def provide(self) -> CompiledStateGraph:
        graph = StateGraph(Demo0EnhancedState)
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

    def extract_question_topic(self, question):
        prompt = f"""
            Bạn là chuyên gia tài chính ngân hàng. Hãy phân tích câu hỏi sau và xác định nó thuộc chủ đề nào trong số các chủ đề sau:
            
            ["capital", "asset_quality", "management", "earnings", "liquidity", "comprehensive"]
            
            Quy tắc phân loại:
            - Nếu câu hỏi liên quan đến vốn, tỷ lệ an toàn vốn, CAR → "capital"
            - Nếu liên quan đến nợ xấu, tài sản đảm bảo, phân loại nợ → "asset_quality"
            - Nếu liên quan đến chi phí, quản trị, hiệu quả hoạt động → "management"
            - Nếu liên quan đến lợi nhuận, ROA, ROE → "earnings"
            - Nếu liên quan đến thanh khoản, khả năng chi trả, tỷ lệ LDR → "liquidity"
            - Nếu yêu cầu phân tích tổng hợp báo cáo tài chính → "comprehensive"
            - Nếu không thuộc các nhóm trên → trả về "fallback"
            
            Câu hỏi: {question}
            
            Chủ đề tương ứng:
        """
        return self.llm.invoke(prompt).content

    def handle_supervisor(self, state):
        incoming_message = state.get("message")
        question = incoming_message.content if incoming_message is not None and incoming_message.content is not None else ""
        bank_names = self.extract_bank_names(question)
        question_topic = self.extract_question_topic(question)
        return {"question": question, "banks": bank_names, "question_topic": question_topic}

    def route_function(self, state):
        bank_names = state["banks"]
        if len(bank_names) == 1:
            return "query_single_bank"
        elif len(bank_names) == 2:
            return "compare_banks"
        else:
            return "fallback"

    def handle_banking_comparison(self, state):
        with open('banking_index.json', 'r', encoding='utf-8') as file:
            banking_index = json.load(file)
        capital_calc = CapitalAdequacyCalculator()
        asset_calc = AssetQualityCalculator()
        mgmt_calc = ManagementCompetenceCalculator()
        earn_calc = EarningStrengthCalculator()

        bank1, bank2 = state['banks'][0], state['banks'][1]
        data1, data2 = banking_index[bank1], banking_index[bank2]

        results = {
            bank1: {
                "capital": capital_calc.comprehensive_capital_analysis(data1),
                "asset": asset_calc.comprehensive_asset_quality_analysis(data1),
                "management": mgmt_calc.comprehensive_management_analysis(data1),
                "earnings": earn_calc.comprehensive_earning_analysis(data1),
            },
            bank2: {
                "capital": capital_calc.comprehensive_capital_analysis(data2),
                "asset": asset_calc.comprehensive_asset_quality_analysis(data2),
                "management": mgmt_calc.comprehensive_management_analysis(data2),
                "earnings": earn_calc.comprehensive_earning_analysis(data2),
            }
        }

        prompt_template = """
        	Bạn là chuyên gia phân tích ngân hàng theo mô hình CAMELS.  
        Dữ liệu đầu vào gồm kết quả phân tích của 2 ngân hàng:
        {results}
    
        Câu hỏi:
        **QUESTION:** 
        {question}
    
        YÊU CẦU OUTPUT:  
        1. Trả về báo cáo so sánh theo định dạng Markdown.  
        2. Gồm 3 phần:  
           - **BẢNG SO SÁNH CAMELS** (Bank A vs Bank B, theo từng chỉ tiêu chính)  
           - **Nhận xét chi tiết theo từng cấu phần (C, A, M, E)**, chỉ ra ngân hàng nào tốt hơn và vì sao.  
           - **Nhận xét tổng thể**: ngân hàng nào có sức khỏe tài chính tốt hơn, điểm mạnh – điểm yếu của từng bên, khuyến nghị.  
    
        ---
        # HƯỚNG DẪN PHÂN TÍCH (chỉ để tham chiếu, KHÔNG in ra trong output):
    
        ## Capital Adequacy
        - **Tốc độ tăng trưởng vốn (CAGR):** ≥15% rất tốt; 10–15% tốt; 5–10% chấp nhận; <5% kém.  
        - **Leverage Ratio:** 12–20 tốt; <12 vốn dư thừa; >20 vốn mỏng, rủi ro cao.  
        - **ICCR:** ≥15% mạnh; 5–15% ổn định; <5% phụ thuộc vốn ngoài.  
        - **Xu hướng:** cải thiện / ổn định / suy giảm.  
    
        ## Asset Quality
        - **Tổng tài sản:** 10–15%/năm ổn định; >15% nóng; <10% thấp.  
        - **Dư nợ tín dụng:** ≤ room NHNN, nợ xấu <3% là tốt.  
        - **Danh mục đầu tư:** tỷ trọng hợp lý, đa dạng hóa tốt.  
        - **Đa dạng hóa (HHI):** ≥0,7 tốt; 0,5–0,7 ổn định; <0,5 tập trung rủi ro.  
        - **Nợ xấu (NPL):** <3% tốt; 3–5% cảnh báo; >5% xấu.  
        - **Dư nợ/TS:** 50–70% tốt; <40% hoặc >80% xấu.  
    
        ## Management
        ### a) CIR (Cost-to-Income Ratio)
        - Tốt: CIR <40% → quản lý chi phí tốt, hiệu quả.  
        - Ổn định: 40–50%.  
        - Xấu: >50% → chi phí cao, hiệu quả thấp.  
        - Thông lệ quốc tế: nhiều ngân hàng lớn duy trì CIR ~35–45%.  
        - Tại Việt Nam: nhóm top (VCB, TCB, MBB) ~30–40%; nhóm quốc doanh (BIDV, CTG) thường 45–55%.  
    
        ### b) OPEX/Tổng tài sản
        - Tốt: <2% → ngân hàng sử dụng tài sản hiệu quả, chi phí thấp.  
        - Ổn định: 2–3%.  
        - Xấu: >3% → chi phí vận hành cao, làm giảm khả năng sinh lời.  
    
        ## Earnings
        ### a) Phương pháp Dupont
        - **PM – Profit Margin:** >25% tốt; 15–25% ổn định; <15% xấu.  
        - **AU – Asset Utilization:** >5% tốt; 3–5% ổn định; <3% xấu.  
        - **EM – Equity Multiplier:** 8–12 tốt; 12–15 ổn định; >15 xấu.  
        - **ROE:** >18% tốt; 12–18% ổn định; <12% thấp.  
        - ROE cao bền vững = PM tốt + AU cao + EM hợp lý.  
        - ROE cao nhờ EM → rủi ro.  
        - ROE thấp do PM thấp → biên lợi nhuận kém.  
        - ROE thấp do AU thấp → sử dụng tài sản kém hiệu quả.  
    
        ### b) NIM
        - Cao (≥3,5%) → CASA mạnh, chi phí vốn thấp, hiệu quả cho vay tốt.  
        - Trung bình (2,5–3,5%) → ổn định, phù hợp chuẩn ngành VN.  
        - Thấp (<2,5%) → thường ở Big4, chi phí vốn cao.  
    
        ### c) Số ngày lãi phải thu
        - Tốt: <30 ngày → thu lãi tốt, ít rủi ro.  
        - Ổn định: 30–60 ngày → bình thường, cần giám sát.  
        - Xấu: >60 ngày → khách hàng chậm trả, rủi ro tín dụng.  
        """
        from langchain_core.output_parsers import StrOutputParser

        question = state.get("question", "")
        prompt_template = ChatPromptTemplate.from_template(prompt_template)
        # Build RAG chain
        rag_chain = (
                {"results": lambda _: results, "question": RunnablePassthrough()}
                | prompt_template
                | self.llm
                | StrOutputParser()
        )
        return {"message": rag_chain.invoke(question)}

    def analyze_single_bank_ca(self, state, banking_index):
        capital_adequacy_calculator = CapitalAdequacyCalculator()
        bank_data = banking_index[state['banks'][0]]
        system_prompt = """
                        Dựa trên dữ liệu capital adequacy sau và câu hỏi, tạo bảng phân tích markdown:

                        **CAPITAL ADEQUACY DATA:**
                        {capital_adequacy}

                        **QUESTION:** 
                        {question}

                        Tạo OUTPUT theo format SAU:

                        ## BẢNG CHỈ SỐ MỨC ĐỘ AN TOÀN VỐN

                        | **Chỉ tiêu** | **2022** | **2023** | **2024** | **Chuẩn NHNN/Basel** | **Đánh giá** |
                        |--------------|----------|----------|----------|---------------------|--------------|
                        | CAGR VCSH | [%] | - | - | ≥10% | [assessment] |
                        | Hệ số đòn bẩy (L) | [x] | [x] | [x] | 12–20 lần | [assessment] |
                        | ICCR | [%] | [%] | [%] | ≥ tốc độ tăng RWA | [assessment] |
                        | CAR Tier 1 | N/A | N/A | N/A | ≥6% (NHNN) | Không có dữ liệu |
                        | CAR tổng | N/A | N/A | N/A | ≥8% (NHNN), ≥10,5% (Basel III) | Không có dữ liệu |

                        ## PHÂN TÍCH CHI TIẾT:

                        ### 1. Tốc độ tăng trưởng vốn:
                        [Phân tích yearly_growth_rates và CAGR - xu hướng, so sánh với chuẩn 10%, ý nghĩa]

                        ### 2. Cấu trúc vốn và rủi ro tài chính:
                        [Phân tích leverage_ratios qua các năm - xu hướng, so với ngưỡng 12-20, tác động]

                        ### 3. Khả năng tự bổ sung vốn:
                        [Phân tích ICCR - khả năng sinh vốn nội tại, bền vững tăng trưởng]

                        **Nhận xét tổng thể:**
                        [Tổng hợp 3-4 câu bao gồm:
                        - Đánh giá tổng quan về độ an toàn vốn
                        - Điểm mạnh và điểm yếu chính  
                        - Xu hướng phát triển qua 3 năm
                        - Khuyến nghị cho chiến lược vốn tương lai]

                        **HƯỚNG DẪN PHÂN TÍCH:**

                        1. **Với CAGR:**
                           - Rất tốt (≥15%): "Tăng trưởng vốn rất mạnh"
                           - Tốt (10-15%): "Tăng trưởng vốn ổn định, đạt chuẩn ngành" 
                           - Chấp nhận (5-10%): "Tăng trưởng vốn chậm nhưng dương"
                           - Kém (<5%): "Tăng trưởng vốn quá thấp"

                        2. **Với Leverage Ratio:**
                           - Tốt (12-20): "Cấu trúc vốn cân bằng, rủi ro kiểm soát"
                           - Thấp (<12): "Vốn dư thừa, chưa tối ưu hiệu quả"
                           - Cao (>20): "Vốn mỏng, rủi ro tài chính tăng cao"

                        3. **Với ICCR:**
                           - Cao (≥15%): "Khả năng tự bổ sung vốn mạnh"
                           - Trung bình (5-15%): "Khả năng tự bổ sung vốn ổn định"
                           - Thấp (<5%): "Phụ thuộc nguồn vốn bên ngoài"

                        4. **Xu hướng:**
                           - Cải thiện: "Xu hướng tích cực"
                           - Ổn định: "Duy trì ổn định"  
                           - Giảm sút: "Có dấu hiệu suy giảm"
                            """
        capital_adequacy = json.dumps(capital_adequacy_calculator.comprehensive_capital_analysis(bank_data))
        question = state.get("question", "")
        prompt_template = ChatPromptTemplate.from_template(system_prompt)
        # Build RAG chain
        rag_chain = (
                {"capital_adequacy": lambda _: capital_adequacy, "question": RunnablePassthrough()}
                | prompt_template
                | self.llm
                | StrOutputParser()
        )
        return {"message": rag_chain.invoke(question)}

    def analyze_single_bank_asset(self, state, banking_index):
        asset_quality_calculator = AssetQualityCalculator()
        bank_data = banking_index[state['banks'][0]]
        system_prompt = """
                    Bạn là chuyên gia phân tích ngân hàng theo mô hình CAMELS.  
                    Dữ liệu đầu vào (Asset Quality) có dạng JSON:
                    {asset_quality}
                    
                    Dựa trên dữ liệu asset quality data trên và câu hỏi:
                    
                    **QUESTION:** 
                    {question}
                                        
                    YÊU CẦU OUTPUT:  
                    1. Trả về báo cáo theo định dạng Markdown.  
                    2. Gồm 2 phần:  
                    - **BẢNG CHỈ SỐ CHẤT LƯỢNG TÀI SẢN** (theo format dưới đây)  
                    - **Phân tích chi tiết & Nhận xét tổng thể** (3–5 đoạn, tổng hợp xu hướng, điểm mạnh, điểm yếu, khuyến nghị)  
                    3. KHÔNG in lại phần HƯỚNG DẪN PHÂN TÍCH dưới đây, chỉ dùng để tham chiếu nội bộ.
                    ---
                    
                    ## BẢNG CHỈ SỐ CHẤT LƯỢNG TÀI SẢN

                    | **Chỉ tiêu**                 | **2022** | **2023** | **2024** | **Ngưỡng chuẩn** | **Đánh giá** |
                    |-------------------------------|----------|----------|----------|------------------|--------------|
                    | Tăng trưởng Tổng tài sản      | –        | [growth_rate 2022-2023]% | [growth_rate 2023-2024]% | 10–15%/năm | … |
                    | Tăng trưởng dư nợ tín dụng    | –        | [growth_rate 2022-2023]% | [growth_rate 2023-2024]% | ≤ room NHNN | … |
                    | Dư nợ/Tổng tài sản            | [ratio 2022]% | [ratio 2023]% | [ratio 2024]% | 50–70% | … |
                    | Tỷ lệ nợ xấu (NPL)            | [npl 2022]% | [npl 2023]% | [npl 2024]% | <3% | … |
                    ---
                    
                    ## HƯỚNG DẪN PHÂN TÍCH:
                    
                    ### a) Quy mô, tốc độ tăng trưởng
                    - **Tổng tài sản**  
                    - Tốt: tăng trưởng ổn định, phù hợp vốn chủ sở hữu, không quá nóng  
                    - Ổn định: ~10–15%/năm (bình quân ngành NHTM VN)  
                    - Xấu: tăng quá nhanh không tương xứng vốn (giảm CAR) hoặc giảm liên tục  
                    
                    - **Dư nợ tín dụng**  
                    - Tốt: tăng trưởng trong room NHNN, nợ xấu <3%  
                    - Ổn định: ~10–14%/năm  
                    - Xấu: tăng quá nhanh, vượt room, kéo theo nợ xấu tăng  
                    
                    - **Danh mục đầu tư**  
                    - Quy mô = CK kinh doanh + CK đầu tư (HTM, AFS) + góp vốn dài hạn  
                    - Đánh giá theo tỷ trọng so với tổng tài sản và xu hướng tăng trưởng  
                    
                    ### b) Tính đa dạng hóa
                    - **Tài sản**  
                    - Tốt: HHI ≥0,7 (phân bổ đều)  
                    - Ổn định: 0,5–0,7  
                    - Xấu: <0,5 (tập trung vào 1–2 khoản mục, ví dụ >70% là tín dụng)  
                    
                    - **Dư nợ tín dụng**  
                    - Tốt: không ngành nào >30%, HHI ≥0,7  
                    - Ổn định: 30–40% một số ngành, HHI 0,5–0,7  
                    - Xấu: >50% tập trung 1 ngành (BĐS, VLXD…), HHI <0,5  
                    
                    - **Danh mục đầu tư**  
                    - Tốt: >50% TPCP, phần còn lại phân tán  
                    - Ổn định: 1–2 nhóm lớn (TPCP + TPDN), HHI 0,5–0,7  
                    - Xấu: >50% TPDN/BĐS hoặc cổ phiếu, HHI <0,5  
                    
                    ### c) Các chỉ tiêu rủi ro tín dụng
                    - **Dư nợ/Tổng tài sản**  
                    - Tốt: 50–70%  
                    - Ổn định: 40–50% hoặc 70–80%  
                    - Xấu: <40% hoặc >80%  
                    
                    - **Tỷ lệ nợ quá hạn**  
                    - Tốt: <3%  
                    - Ổn định: 3–5%  
                    - Xấu: >5%  
                    
                    - **Tỷ lệ nợ xấu (NPL)**  
                    - Tốt: <3%  
                    - Ổn định: 3–5%  
                    - Xấu: >5%  
                    
                    - **Tình hình bảo đảm khoản vay**  
                    - Tốt: >80% dư nợ có TSĐB  
                    - Ổn định: 60–80%  
                    - Xấu: <60%  
                    
                    - **Mức độ tập trung tín dụng**  
                    - Tốt: 20–30% tổng tài sản  
                    - Ổn định: biến động nhẹ, phù hợp ALM  
                    - Xấu: >40% tổng tài sản  
                """
        asset_quality = json.dumps(asset_quality_calculator.comprehensive_asset_quality_analysis(bank_data))
        question = state.get("question", "")
        prompt_template = ChatPromptTemplate.from_template(system_prompt)
        # Build RAG chain
        rag_chain = (
                {"asset_quality": lambda _: asset_quality, "question": RunnablePassthrough()}
                | prompt_template
                | self.llm
                | StrOutputParser()
        )
        return {"message": rag_chain.invoke(question)}

    def analyze_single_bank_management(self, state, banking_index):
        management_competence_calculator = ManagementCompetenceCalculator()
        bank_data = banking_index[state['banks'][0]]
        system_prompt = """
                        Bạn là chuyên gia phân tích ngân hàng theo mô hình CAMELS.  
                        Dữ liệu đầu vào (Management Competence) có dạng JSON:
                        {management_results}
                        
                        Câu hỏi:
                        **QUESTION:** 
                        {question}
                        
                        YÊU CẦU OUTPUT:  
                        1. Trả về báo cáo theo định dạng Markdown.  
                        2. Gồm 3 phần:  
                           - **BẢNG CHỈ SỐ KHẢ NĂNG QUẢN TRỊ** (chỉ gồm các chỉ tiêu có dữ liệu)  
                           - **Nhận xét tổng thể** (3–5 câu, tổng hợp xu hướng, điểm mạnh, điểm yếu, khuyến nghị)  
                           - **HƯỚNG DẪN PHÂN TÍCH** (khung chuẩn để tham chiếu khi đánh giá) 
                        3. KHÔNG in lại phần HƯỚNG DẪN PHÂN TÍCH dưới đây, chỉ dùng để tham chiếu nội bộ. 
                        
                        ---
                        
                        ## BẢNG CHỈ SỐ KHẢ NĂNG QUẢN TRỊ
                        
                        | **Chỉ tiêu**                        | **2022** | **2023** | **2024** | **Ngưỡng chuẩn** | **Đánh giá** |
                        |-------------------------------------|----------|----------|----------|------------------|--------------|
                        | CIR (Cost-to-Income Ratio)          | [cir 2022]% | [cir 2023]% | [cir 2024]% | <40% tốt; 40–50% ổn định; >50% xấu | … |
                        | OPEX/Tổng tài sản                   | [opex_assets 2022]% | [opex_assets 2023]% | [opex_assets 2024]% | <2% tốt; 2–3% ổn định; >3% xấu | … |
                        
                        ---
                        
                        ## Nhận xét tổng thể:
                        - Đánh giá xu hướng CIR qua 3 năm, so với chuẩn quốc tế và Việt Nam.  
                        - Đánh giá mức độ hiệu quả sử dụng tài sản qua chỉ số OPEX/Tổng tài sản.  
                        - Nhận định tổng quan về khả năng quản trị chi phí, hiệu quả vận hành.  
                        - Đưa ra khuyến nghị cải thiện (nếu CIR cao, hoặc OPEX/TS vượt chuẩn).  
                        
                        ---
                        
                        ## HƯỚNG DẪN PHÂN TÍCH:
                        
                        ### a) CIR (Cost-to-Income Ratio)
                        - **Tốt**: CIR < 40% → quản lý chi phí tốt, hiệu quả.  
                        - **Ổn định**: 40–50%.  
                        - **Xấu**: >50% → chi phí cao, hiệu quả thấp.  
                        - **Thông lệ quốc tế**: nhiều ngân hàng lớn duy trì CIR ~35–45%.  
                        - **Tại Việt Nam**: nhóm top (VCB, TCB, MBB) ~30–40%; nhóm quốc doanh (BIDV, CTG) thường 45–55%.  
                        
                        ### b) OPEX/Tổng tài sản
                        - **Tốt**: <2% → ngân hàng sử dụng tài sản hiệu quả, chi phí thấp.  
                        - **Ổn định**: 2–3%.  
                        - **Xấu**: >3% → chi phí vận hành cao, làm giảm khả năng sinh lời.  

                        """
        management_results = json.dumps(management_competence_calculator.comprehensive_management_analysis(bank_data))
        question = state.get("question", "")
        prompt_template = ChatPromptTemplate.from_template(system_prompt)
        # Build RAG chain
        rag_chain = (
                {"management_results": lambda _: management_results, "question": RunnablePassthrough()}
                | prompt_template
                | self.llm
                | StrOutputParser()
        )
        return {"message": rag_chain.invoke(question)}

    def analyze_single_bank_earning_strength(self, state, banking_index):
        earning_strength_calculator = EarningStrengthCalculator()
        bank_data = banking_index[state['banks'][0]]
        system_prompt = """
                        Bạn là chuyên gia phân tích ngân hàng theo mô hình CAMELS.  
                        Dữ liệu đầu vào (Earning Strength) có dạng JSON:
                        {earning_results}
                        
                        Câu hỏi:
                        **QUESTION:** 
                        {question}
                        
                        YÊU CẦU OUTPUT:  
                        1. Trả về báo cáo theo định dạng Markdown.  
                        2. Gồm 3 phần:  
                           - **BẢNG CHỈ SỐ KHẢ NĂNG SINH LỜI** (chỉ gồm các chỉ tiêu có dữ liệu)  
                           - **Nhận xét tổng thể** (3–5 câu, tổng hợp xu hướng, điểm mạnh, điểm yếu, khuyến nghị)  
                           - **HƯỚNG DẪN PHÂN TÍCH** (khung chuẩn để tham chiếu khi đánh giá)  
                        3. KHÔNG in lại phần HƯỚNG DẪN PHÂN TÍCH dưới đây, chỉ dùng để tham chiếu nội bộ.
                        ---
                        
                        ## BẢNG CHỈ SỐ KHẢ NĂNG SINH LỜI
                        
                        | **Chỉ tiêu**                  | **2022** | **2023** | **2024** | **Ngưỡng chuẩn** | **Đánh giá** |
                        |--------------------------------|----------|----------|----------|------------------|--------------|
                        | PM – Profit Margin (%)         | [pm 2022] | [pm 2023] | [pm 2024] | >25% tốt; 15–25% ổn định; <15% xấu | … |
                        | AU – Asset Utilization (%)     | [au 2022] | [au 2023] | [au 2024] | >5% tốt; 3–5% ổn định; <3% xấu | … |
                        | EM – Equity Multiplier (lần)   | [em 2022] | [em 2023] | [em 2024] | 8–12 tốt; 12–15 ổn định; >15 xấu | … |
                        | ROE (%)                        | [roe 2022] | [roe 2023] | [roe 2024] | >18% tốt; 12–18% ổn định; <12% thấp | … |
                        | NIM (%)                        | [nim 2022] | [nim 2023] | [nim 2024] | ≥3,5% cao; 2,5–3,5% ổn định; <2,5% thấp | … |
                        | Số ngày lãi phải thu (ngày)    | [days_ir 2022] | [days_ir 2023] | [days_ir 2024] | <30 tốt; 30–60 ổn định; >60 xấu | … |
                        
                        ---
                        
                        ## Nhận xét tổng thể:
                        - Đánh giá xu hướng ROE qua 3 năm, phân tích xem đến từ PM, AU hay EM.  
                        - Đánh giá NIM so với chuẩn ngành.  
                        - Đánh giá số ngày lãi phải thu, xem có rủi ro tín dụng tiềm ẩn không.  
                        - Đưa ra kết luận tổng thể: mức độ sinh lời, điểm mạnh, điểm yếu, khuyến nghị.  
                        
                        ---
                        
                        ## HƯỚNG DẪN PHÂN TÍCH:
                        
                        ### a) Phương pháp Dupont
                        - **PM – Profit Margin**  
                          - Tốt: >25% → quản lý chi phí tốt, NIM cao, CIR thấp.  
                          - Ổn định: 15–25%.  
                          - Xấu: <15% → chi phí cao, NIM thấp, trích lập dự phòng nhiều.  
                        
                        - **AU – Asset Utilization**  
                          - Tốt: >5% → tài sản sinh lời tốt.  
                          - Ổn định: 3–5%.  
                          - Xấu: <3% → tài sản kém hiệu quả.  
                        
                        - **EM – Equity Multiplier**  
                          - Tốt: 8–12 lần → hợp lý.  
                          - Ổn định: 12–15 lần → chấp nhận được nhưng rủi ro tăng.  
                          - Xấu: >15 lần → vốn mỏng, phụ thuộc nợ.  
                        
                        - **ROE**  
                          - >18% → tốt.  
                          - 12–18% → ổn định.  
                          - <12% → thấp.  
                          - ROE cao bền vững = PM tốt + AU cao + EM hợp lý.  
                          - ROE cao nhờ EM → rủi ro.  
                          - ROE thấp do PM thấp → biên lợi nhuận kém.  
                          - ROE thấp do AU thấp → sử dụng tài sản kém hiệu quả.  
                        
                        ### b) NIM
                        - Cao (≥3,5%) → CASA mạnh, chi phí vốn thấp, hiệu quả cho vay tốt.  
                        - Trung bình (2,5–3,5%) → ổn định, phù hợp chuẩn ngành VN.  
                        - Thấp (<2,5%) → thường ở Big4, chi phí vốn cao.  
                        
                        ### c) Số ngày lãi phải thu
                        - Tốt: <30 ngày → thu lãi tốt, ít rủi ro.  
                        - Ổn định: 30–60 ngày → bình thường, cần giám sát.  
                        - Xấu: >60 ngày → khách hàng chậm trả, rủi ro tín dụng.  
                        """
        earning_results = json.dumps(earning_strength_calculator.comprehensive_earning_analysis(bank_data))
        question = state.get("question", "")
        prompt_template = ChatPromptTemplate.from_template(system_prompt)
        # Build RAG chain
        rag_chain = (
                {"earning_results": lambda _: earning_results, "question": RunnablePassthrough()}
                | prompt_template
                | self.llm
                | StrOutputParser()
        )
        return {"message": rag_chain.invoke(question)}

    def analyze_single_bank_comprehension(self, state, banking_index):
        capital_calculator = CapitalAdequacyCalculator()
        asset_calculator = AssetQualityCalculator()
        management_calculator = ManagementCompetenceCalculator()
        earning_calculator = EarningStrengthCalculator()
        bank_data = banking_index[state['banks'][0]]
        system_prompt = """
                        Bạn là chuyên gia phân tích ngân hàng theo mô hình CAMELS.  
                        Dữ liệu đầu vào gồm kết quả phân tích từng cấu phần:  
                        
                        - **Capital Adequacy (C):**  
                        {capital_results}
                        
                        - **Asset Quality (A):**  
                        {asset_results}
                        
                        - **Management Competence (M):**  
                        {management_results}
                        
                        - **Earning Strength (E):**  
                        {earning_results}
                        
                        Câu hỏi:
                        **QUESTION:** 
                        {question}
                        
                        YÊU CẦU OUTPUT:  
                        1. Trả về báo cáo theo định dạng Markdown.  
                        2. Gồm 3 phần:  
                           - **BẢNG TỔNG HỢP CAMELS** (chỉ tiêu chính của từng cấu phần)  
                           - **Nhận xét chi tiết theo từng cấu phần (C, A, M, E)**  
                           - **Nhận xét tổng thể** (3–5 câu, đánh giá chung sức khỏe tài chính, điểm mạnh, điểm yếu, khuyến nghị)  
                        3. HƯỚNG DẪN PHÂN TÍCH (chỉ để tham chiếu, KHÔNG in ra trong output)
                        
                        ---
                        
                        ## BẢNG TỔNG HỢP CAMELS
                        
                        | **Cấu phần** | **Chỉ tiêu chính** | **2022** | **2023** | **2024** | **Ngưỡng chuẩn** | **Đánh giá** |
                        |--------------|--------------------|----------|----------|----------|------------------|--------------|
                        | Capital Adequacy (C) | CAGR vốn, Leverage, ICCR | … | … | … | CAR ≥ 8% | … |
                        | Asset Quality (A)    | NPL, Loan/Asset, Growth | … | … | … | NPL <3% | … |
                        | Management (M)       | CIR, OPEX/Assets | … | … | … | CIR <40% | … |
                        | Earnings (E)         | PM, AU, EM, ROE, NIM, Days IR | … | … | … | ROE >18% | … |
                        
                        ---
                        
                        ## Nhận xét chi tiết:
                        - **Capital Adequacy (C):** Đánh giá tốc độ tăng trưởng vốn, cấu trúc vốn (leverage), khả năng tự bổ sung vốn (ICCR).  
                        - **Asset Quality (A):** Đánh giá tăng trưởng tài sản, dư nợ, danh mục đầu tư, đa dạng hóa, nợ xấu.  
                        - **Management (M):** Đánh giá hiệu quả quản trị chi phí qua CIR, OPEX/TS.  
                        - **Earnings (E):** Đánh giá khả năng sinh lời qua Dupont (PM, AU, EM, ROE), NIM, số ngày lãi phải thu.  
                        
                        ---
                        
                        ## Nhận xét tổng thể:
                        - Tổng hợp sức khỏe tài chính ngân hàng theo CAMELS.  
                        - Nêu rõ điểm mạnh (ví dụ: vốn an toàn, nợ xấu thấp, NIM cao).  
                        - Nêu điểm yếu (ví dụ: CIR cao, tăng trưởng nóng, ROE phụ thuộc đòn bẩy).  
                        - Đưa ra khuyến nghị (kiểm soát chi phí, đa dạng hóa tài sản, nâng cao hiệu quả sử dụng vốn).  
                        
                        ---
                        
                        # HƯỚNG DẪN PHÂN TÍCH (chỉ để tham chiếu, KHÔNG in ra trong output):
                        
                        ## Capital Adequacy
                        - **Tốc độ tăng trưởng vốn (CAGR):** ≥15% rất tốt; 10–15% tốt; 5–10% chấp nhận; <5% kém.  
                        - **Leverage Ratio:** 12–20 tốt; <12 vốn dư thừa; >20 vốn mỏng, rủi ro cao.  
                        - **ICCR:** ≥15% mạnh; 5–15% ổn định; <5% phụ thuộc vốn ngoài.  
                        - **Xu hướng:** cải thiện / ổn định / suy giảm.  
                        
                        ## Asset Quality
                        - **Tổng tài sản:** 10–15%/năm ổn định; >15% nóng; <10% thấp.  
                        - **Dư nợ tín dụng:** ≤ room NHNN, nợ xấu <3% là tốt.  
                        - **Danh mục đầu tư:** tỷ trọng hợp lý, đa dạng hóa tốt.  
                        - **Đa dạng hóa (HHI):** ≥0,7 tốt; 0,5–0,7 ổn định; <0,5 tập trung rủi ro.  
                        - **Nợ xấu (NPL):** <3% tốt; 3–5% cảnh báo; >5% xấu.  
                        - **Dư nợ/TS:** 50–70% tốt; <40% hoặc >80% xấu.  
                        
                        ## Management
                        ### a) CIR (Cost-to-Income Ratio)
                        - Tốt: CIR <40% → quản lý chi phí tốt, hiệu quả.  
                        - Ổn định: 40–50%.  
                        - Xấu: >50% → chi phí cao, hiệu quả thấp.  
                        - Thông lệ quốc tế: nhiều ngân hàng lớn duy trì CIR ~35–45%.  
                        - Tại Việt Nam: nhóm top (VCB, TCB, MBB) ~30–40%; nhóm quốc doanh (BIDV, CTG) thường 45–55%.  
                        
                        ### b) OPEX/Tổng tài sản
                        - Tốt: <2% → ngân hàng sử dụng tài sản hiệu quả, chi phí thấp.  
                        - Ổn định: 2–3%.  
                        - Xấu: >3% → chi phí vận hành cao, làm giảm khả năng sinh lời.  
                        
                        ## Earnings
                        ### a) Phương pháp Dupont
                        - **PM – Profit Margin:** >25% tốt; 15–25% ổn định; <15% xấu.  
                        - **AU – Asset Utilization:** >5% tốt; 3–5% ổn định; <3% xấu.  
                        - **EM – Equity Multiplier:** 8–12 tốt; 12–15 ổn định; >15 xấu.  
                        - **ROE:** >18% tốt; 12–18% ổn định; <12% thấp.  
                        - ROE cao bền vững = PM tốt + AU cao + EM hợp lý.  
                        - ROE cao nhờ EM → rủi ro.  
                        - ROE thấp do PM thấp → biên lợi nhuận kém.  
                        - ROE thấp do AU thấp → sử dụng tài sản kém hiệu quả.  
                        
                        ### b) NIM
                        - Cao (≥3,5%) → CASA mạnh, chi phí vốn thấp, hiệu quả cho vay tốt.  
                        - Trung bình (2,5–3,5%) → ổn định, phù hợp chuẩn ngành VN.  
                        - Thấp (<2,5%) → thường ở Big4, chi phí vốn cao.  
                        
                        ### c) Số ngày lãi phải thu
                        - Tốt: <30 ngày → thu lãi tốt, ít rủi ro.  
                        - Ổn định: 30–60 ngày → bình thường, cần giám sát.  
                        - Xấu: >60 ngày → khách hàng chậm trả, rủi ro tín dụng.   
                        """
        earning_results = json.dumps(earning_calculator.comprehensive_earning_analysis(bank_data))
        capital_results = json.dumps(capital_calculator.comprehensive_capital_analysis(bank_data))
        asset_results = json.dumps(asset_calculator.comprehensive_asset_quality_analysis(bank_data))
        management_results = json.dumps(management_calculator.comprehensive_management_analysis(bank_data))
        question = state.get("question", "")
        prompt_template = ChatPromptTemplate.from_template(system_prompt)
        # Build RAG chain
        rag_chain = (
                {"earning_results": lambda _: earning_results,
                 "capital_results": lambda _: capital_results,
                 "asset_results": lambda _: asset_results,
                 "management_results": lambda _: management_results,
                 "question": RunnablePassthrough()}
                | prompt_template
                | self.llm
                | StrOutputParser()
        )
        return {"message": rag_chain.invoke(question)}

    def handle_querying_single_bank(self, state):
        with open('banking_index.json', 'r', encoding='utf-8') as file:
            banking_index = json.load(file)
        question_topic = state.get("question_topic", "")
        # ["capital", "asset_quality", "management", "earnings", "liquidity", "comprehensive"]
        if "capital" in question_topic:
            return self.analyze_single_bank_ca(state, banking_index)
        if "asset" in question_topic:
            return self.analyze_single_bank_asset(state, banking_index)
        if "management" in question_topic:
            return self.analyze_single_bank_management(state, banking_index)
        if "earnings" in question_topic:
            return self.analyze_single_bank_earning_strength(state, banking_index)
        if "comprehensive" in question_topic:
            return self.analyze_single_bank_comprehension(state, banking_index)
        else:
            raise Exception("not found")

    def fallback(self, state):
        question = state["question"]
        prompt = f"""Tôi chưa xác định được rõ yêu cầu của bạn. Bạn có thể làm rõ thêm câu hỏi sau không?
        Câu hỏi: {question}"""
        return {"message": self.llm.invoke(prompt)}


class Demo0ChatAgent(ChatAgent):

    def __init__(self, graph: GraphProvider):
        self.graph = graph
        self.mapper = Demo0EnhancedStateMapper()

    def predict(self, messages: list[ChatAgentMessage], context: ChatContext | None = None,
                custom_inputs: dict[str, Any] | None = None) -> ChatAgentResponse:
        input_state = self.mapper.map_from_message_to_state(messages)
        state = self.graph.provide().invoke(input_state)
        result = self.mapper.map_from_state_to_message(state)
        return ChatAgentResponse(messages=result)


# graph2 = Demo0ChatAgent(graph=Demo0EnhancedGraphProvider())
# incoming_message = ChatAgentMessage(role="user",
#                                     content="Hãy so sánh tình hình tài chính VPB và SHB trong 3 năm")
# test_result = graph2.predict(messages=[incoming_message])
# print(test_result)

mlflow.langchain.autolog()
chat_agent = Demo0ChatAgent(graph=Demo0EnhancedGraphProvider())
mlflow.models.set_model(chat_agent)
