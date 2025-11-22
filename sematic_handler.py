import os
import re
from typing import List

import nltk
from PyPDF2 import PdfReader, PdfWriter
from google import genai
from google.genai import types
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from nltk import sent_tokenize

from src.chunking.chunking_handler import chunk_the_extracted_report_enhanced

nltk.download("punkt_tab")


def semantic_chunking(text, max_tokens=1024):
    sentences = sent_tokenize(text)
    chunks, current_chunk, current_length = [], [], 0

    for sentence in sentences:
        length = len(sentence.split())
        if current_length + length > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk, current_length = [sentence], length
        else:
            current_chunk.append(sentence)
            current_length += length

    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks


def split_documents_semantically(documents):
    chunks = []
    for i, doc in enumerate(documents):
        semantic_chunks = semantic_chunking(doc.page_content)
        for j, chunk_text in enumerate(semantic_chunks):
            chunks.append(
                {
                    "text": chunk_text,
                    "metadata": {
                        "source": doc.metadata.get("source", ""),
                        "page": doc.metadata.get("page", i + 1),
                        "chunk_id": f"{i + 1}_{j}",
                    },
                }
            )
    return chunks


def store_chunks(db, chunks):
    documents = [
        Document(
            page_content=chunk["text"],
            metadata={
                "page": chunk["metadata"]["page"],
                "chunk_id": chunk["metadata"]["chunk_id"],
            },
        )
        for chunk in chunks
    ]
    db.add_documents(documents=documents)


MAPPING_COLLECTION = {
    "LPB_Baocaothuongnien_2024.pdf": "LPBANK",
    "MBB_Baocaothuongnien_2024.pdf": "MBBANK",
}


def init_predefined_docs_to_db():
    """Processes and adds uploaded PDF files to the database."""
    # embedding = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    documentations_path = "./documentations"

    for filename in os.listdir(documentations_path):
        collection_name = MAPPING_COLLECTION[filename]
        # embedding = OllamaEmbeddings(
        #     model="toshk0/nomic-embed-text-v2-moe:Q6_K",
        #     base_url="http://localhost:11434"
        # )
        embedding = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        # Test the model
        db = Chroma(
            collection_name=collection_name,
            embedding_function=embedding,
            persist_directory="./rawiq_db",
        )
        file_path = os.path.join(documentations_path, filename)
        # Check if it's a file (not a subfolder)
        if os.path.isfile(file_path):
            print(f"######### File Path: {file_path} ############")
            loader = PyPDFLoader(file_path)
            chunks = split_documents_semantically(loader.load())
            store_chunks(db, chunks)


def cut_pdf(input_pdf, output_pdf, start_page, end_page):
    """Extracts pages from start_page to end_page (inclusive) into a new PDF."""
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page_num in range(start_page - 1, end_page):  # 0-indexed
        writer.add_page(reader.pages[page_num])

    with open(output_pdf, "wb") as f_out:
        writer.write(f_out)


# cut_pdf("./landing/banking_financial_report/shb/2024.pdf", "./landing/banking_financial_report/shb/2024_fine_grain.pdf", start_page=7, end_page=12)


# banking_report_filepath = pathlib.Path(
#     '/Users/binhnt8/Desktop/work/learning/code/y3a/landing/banking_financial_report/shb/2024_fine_grain.pdf')


# Retrieve and encode the PDF byte
def extract_information_from_report(filepath):
    client = genai.Client()
    prompt = """
    Hãy trích xuất toàn bộ nội dung văn bản từ file PDF hoặc hình ảnh sau, đặc biệt là các bảng biểu trong báo cáo tài chính.
    
    Yêu cầu:
    1. Nhận diện các phần báo cáo theo tiêu đề chính (ví dụ: "Lưu chuyển tiền thuần từ hoạt động đầu tư", "Lưu chuyển tiền thuần từ hoạt động tài chính").
    2. Gộp các bảng có cùng tiêu đề thành một bảng hợp nhất, bao gồm dữ liệu của cả năm nay và năm trước.
    3. Trình bày lại các bảng dưới định dạng Markdown để dễ phân tích, với các cột rõ ràng: **Chỉ tiêu**, **Năm nay**, **Năm trước**.
    4. Nếu tiêu đề cột là "Năm nay" và "Năm trước", hãy tự động đổi thành năm cụ thể dựa trên năm của báo cáo. Ví dụ: nếu báo cáo là năm 2024, thì "Năm nay" = 2024 và "Năm trước" = 2023.
    5. Nếu tiêu đề cột đã ghi rõ "Năm 2023" và "Năm 2024", thì giữ nguyên như vậy (Năm 2023 = 2023, Năm 2024 = 2024).
    6. Giữ nguyên đơn vị tiền tệ là triệu VND và định dạng số liệu (bao gồm cả dấu ngoặc cho số âm).
    7. Đảm bảo các bảng được căn chỉnh đẹp, dễ đọc và có tiêu đề phụ rõ ràng cho từng phần.
    8. Nếu có nhiều bảng cùng tiêu đề nhưng khác nội dung chi tiết, hãy hợp nhất chúng theo nhóm tiêu đề và trình bày đầy đủ.
    
    Ví dụ định dạng mong muốn:
    
    ### II. Lưu chuyển tiền thuần từ hoạt động đầu tư
    
    | Chỉ tiêu                                                                 | 2024        | 2023        |
    |--------------------------------------------------------------------------|-------------|-------------|
    | Mua sắm tài sản cố định                                                  | (210.732)   | (240.841)   |
    | Tiền thu từ thanh lý, nhượng bán tài sản cố định                         | 2.474       | 1.780       |
    | Tiền chi từ thanh lý, nhượng bán tài sản cố định                         | (1.232)     | (1.895)     |
    | Tiền thu đầu tư, góp vốn vào các đơn vị khác                             | —           | 825.440     |
    | Tiền thu cổ tức và lợi nhuận được chia từ các khoản đầu tư dài hạn      | 29.502      | 4.958       |
    | **Lưu chuyển tiền thuần từ hoạt động đầu tư**                            | **(179.988)**| **589.442** |
    
    Hãy đảm bảo tính chính xác, đầy đủ và trình bày rõ ràng để thuận tiện cho việc phân tích sau này.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(
                data=filepath.read_bytes(),
                mime_type="application/pdf",
            ),
            prompt,
        ],
    )
    print(response.text)


def is_table_line(line):
    """Check if a line is part of a markdown table"""
    line = line.strip()
    if not line:
        return False
    # Table row (starts and ends with |)
    if line.startswith("|") and line.endswith("|"):
        return True
    # Table separator (contains only |, -, :, and spaces)
    if re.match(r"^[|\-:\s]+$", line) and "|" in line:
        return True
    return False


def extract_tables_and_text(content):
    """
    Extract tables and regular text from content, keeping tables intact
    Returns list of (content, is_table) tuples
    """
    lines = content.split("\n")
    sections = []
    current_section = []
    in_table = False

    for line in lines:
        is_table_line_current = is_table_line(line)

        # State transition logic
        if not in_table and is_table_line_current:
            # Starting a new table - save previous section if exists
            if current_section:
                text_content = "\n".join(current_section).strip()
                if text_content:
                    sections.append((text_content, False))
                current_section = []
            in_table = True
            current_section.append(line)
        elif in_table and is_table_line_current:
            # Continue table
            current_section.append(line)
        elif in_table and not is_table_line_current:
            # End of table - save table section
            if current_section:
                table_content = "\n".join(current_section).strip()
                if table_content:
                    sections.append((table_content, True))
                current_section = []
            in_table = False
            if line.strip():  # Only add non-empty lines
                current_section.append(line)
        else:
            # Regular text
            if line.strip() or current_section:  # Preserve structure
                current_section.append(line)

    # Handle remaining content
    if current_section:
        content_text = "\n".join(current_section).strip()
        if content_text:
            sections.append((content_text, in_table))

    return sections


def smart_split_text(text, semantic_splitter):
    """Split text while trying to preserve paragraph structure"""
    # First try to split by double newlines (paragraphs)
    paragraphs = text.split("\n\n")

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        # If adding this paragraph would exceed chunk size, finalize current chunk
        if (
            current_chunk
            and len(current_chunk + "\n\n" + paragraph) > semantic_splitter._chunk_size
        ):
            chunks.append(current_chunk.strip())
            current_chunk = paragraph
        else:
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph

    # Add remaining content
    if current_chunk:
        chunks.append(current_chunk.strip())

    # If any chunk is still too large, use semantic splitter
    final_chunks = []
    for chunk in chunks:
        if len(chunk) > semantic_splitter._chunk_size:
            sub_chunks = semantic_splitter.split_text(chunk)
            final_chunks.extend(sub_chunks)
        else:
            final_chunks.append(chunk)

    return final_chunks


def chunk_the_extracted_report(file_path, year):
    with open(file_path, "r", encoding="utf-8") as f:
        markdown_text = f.read()

    headers_to_split_on = [
        ("###", "BÁO CÁO TÌNH HÌNH TÀI CHÍNH HỢP NHẤT"),
        ("###", "BÁO CÁO LƯU CHUYỂN TIỀN TỆ HỢP NHẤT"),
        ("###", "CÁC CHỈ TIÊU NGOÀI BÁO CÁO TÌNH HÌNH TÀI CHÍNH HỢP NHẤT"),
        ("###", "BÁO CÁO LƯU CHUYỂN TIỀN TỆ HỢP NHẤT"),
    ]

    semantic_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    final_chunks = []

    md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    hierarchical_docs = md_splitter.split_text(markdown_text)

    for doc in hierarchical_docs:
        content = doc.page_content

        # Extract tables and regular text sections
        sections = extract_tables_and_text(content)

        for section_content, is_table in sections:
            if not section_content.strip():
                continue

            if is_table:
                # Keep table intact as a single chunk
                print(f"Found table chunk: {len(section_content)} characters")
                final_chunks.append(
                    Document(
                        page_content=section_content,
                        metadata={**doc.metadata, "year": year},
                    )
                )
            else:
                # Apply semantic chunking to regular text
                sub_chunks = smart_split_text(section_content, semantic_splitter)
                for chunk in sub_chunks:
                    if chunk.strip():
                        final_chunks.append(
                            Document(
                                page_content=chunk,
                                metadata={**doc.metadata, "year": year},
                            )
                        )

    print(f"Total chunks created: {len(final_chunks)}")

    # Display result

    return final_chunks


def chunk_and_store_to_vector_search(file_path, bank, year):
    docs = chunk_the_extracted_report_enhanced(file_path, year)
    embedding = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    # Test the model
    # embedding = OllamaEmbeddings(
    #     model="toshk0/nomic-embed-text-v2-moe:Q6_K",
    #     base_url="http://localhost:11434"
    # )
    db = Chroma(
        collection_name=bank,
        embedding_function=embedding,
        persist_directory="./rawiq_db",
    )
    db.add_documents(docs)


# chunk_and_store_to_vector_search("landing/banking_financial_report/vpb/extracted_2024.md", "vpb", 2024)
# extract_information_from_report(banking_report_filepath)
def format_docs(docs):
    """Formats a list of document objects into a single string."""
    return "\n\n".join(doc.page_content for doc in docs)


def query_context_with_metadata(
    db, query_terms: List[str], year: int = 2024, k: int = 10
):
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
                filter={"year": year},  # Filter theo năm trong metadata
            )
            all_results.extend(results)
        except Exception as e:
            print(f"Error querying '{query_term}': {e}")
            continue
    return format_docs(all_results)


def handle_querying_single_bank(bank, year):
    embedding = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    # embedding = OllamaEmbeddings(
    #     model="toshk0/nomic-embed-text-v2-moe:Q6_K",
    #     base_url="http://localhost:11434"
    # )
    # Test the model
    print(embedding.embed_query("test connection"))
    print("✅ Successfully loaded embedding model")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0)
    bank_db = Chroma(
        collection_name=bank,
        embedding_function=embedding,
        persist_directory="./rawiq_db",
    )
    context_queries = {
        "balance_sheet": [
            "BÁO CÁO TÌNH HÌNH TÀI CHÍNH HỢP NHẤT",
            "Bảng cân đối kế toán",
            "tài sản có",
            "nợ phải trả",
            "vốn chủ sở hữu",
        ],
        "income_statement": [
            "BÁO CÁO KẾT QUẢ HOẠT ĐỘNG HỢP NHẤT",
            "thu nhập lãi thuần",
            "chi phí hoạt động",
            "lợi nhuận",
            "chi phí dự phòng",
        ],
        "cash_flow": [
            "BÁO CÁO LƯU CHUYỂN TIỀN TỆ HỢP NHẤT",
            "hoạt động kinh doanh",
            "hoạt động đầu tư",
            "hoạt động tài chính",
        ],
        "off_balance": [
            "CÁC CHỈ TIÊU NGOÀI BÁO CÁO TÌNH HÌNH TÀI CHÍNH",
            "bảo lãnh",
            "cam kết",
            "công cụ tài chính phái sinh",
        ],
    }
    balance_sheet = query_context_with_metadata(
        db=bank_db, query_terms=context_queries.get("balance_sheet"), year=year
    )
    income_statement = query_context_with_metadata(
        db=bank_db, query_terms=context_queries.get("income_statement"), year=year
    )
    cash_flow = query_context_with_metadata(
        db=bank_db, query_terms=context_queries.get("cash_flow"), year=year
    )
    off_balance = query_context_with_metadata(
        db=bank_db, query_terms=context_queries.get("off_balance"), year=year
    )

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
    prompt = (
        (
            prompt.replace("{balance_sheet}", balance_sheet).replace(
                "{income_statement}", income_statement
            )
        )
        .replace("{cash_flow}", cash_flow)
        .replace("{off_balance}", off_balance)
    )

    prompt_template = ChatPromptTemplate.from_template(prompt)

    # 3. Tạo chain
    chain = (
        {"question": RunnablePassthrough()} | prompt_template | llm | StrOutputParser()
    )
    return chain.invoke("trích xuất các chỉ số CAMELS cho SHB")


print(handle_querying_single_bank("vpb", 2024))
