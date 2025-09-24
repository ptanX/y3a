import os
import re

import nltk
from PyPDF2 import PdfReader, PdfWriter
from chromadb import Settings, Client
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_ollama import OllamaEmbeddings, ChatOllama
import fitz
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from nltk import sent_tokenize
from google import genai
from google.genai import types
import pathlib

# nltk.download('punkt_tab')

nltk.download('punkt_tab')

# os.environ["GOOGLE_API_KEY"] = "MAY_THANG_HACKER_NGHI_TAO_NGU_MA_POST_TOKEN_AH"


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
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "source": doc.metadata.get("source", ""),
                    "page": doc.metadata.get("page", i + 1),
                    "chunk_id": f"{i + 1}_{j}"
                }
            })
    return chunks


def store_chunks(db, chunks):
    documents = [
        Document(
            page_content=chunk["text"],
            metadata={
                "page": chunk["metadata"]["page"],
                "chunk_id": chunk["metadata"]["chunk_id"]
            }
        )
        for chunk in chunks
    ]
    db.add_documents(documents=documents)


MAPPING_COLLECTION = {
    "LPB_Baocaothuongnien_2024.pdf": "LPBANK",
    "MBB_Baocaothuongnien_2024.pdf": "MBBANK"
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
        db = Chroma(collection_name=collection_name,
                    embedding_function=embedding,
                    persist_directory='./rawiq_db')
        file_path = os.path.join(documentations_path, filename)
        # Check if it's a file (not a subfolder)
        if os.path.isfile(file_path):
            print(f'######### File Path: {file_path} ############')
            loader = PyPDFLoader(file_path)
            chunks = split_documents_semantically(loader.load())
            store_chunks(db, chunks)


# def check_table_contents():
#     llm = ChatGoogleGenerativeAI(
#             model="gemini-2.5-pro",
#             temperature=0
#         )
#     prompt_template = """
#             Bạn là một trợ lý AI chuyên phân tích tài liệu PDF báo cáo tài chính.
#
#             Dưới đây là nội dung được trích xuất từ một hoặc nhiều trang PDF. Nhiệm vụ của bạn là:
#
#             1. Xác định xem nội dung có phải là **mục lục** của {question} hay không.
#             2. Nếu đúng là mục lục, hãy trích xuất các **chương**, **tiêu đề chính**, và **tiêu đề phụ** (nếu có) theo cấu trúc sau:
#     [
#       {{
#         "chapter": "Tên chương",
#         "sections": [
#           "Tiêu đề phụ 1",
#           "Tiêu đề phụ 2",
#           ...
#         ]
#       }},
#       ...
#     ]
#             3. Nếu **không phải mục lục**, hãy trả lời rõ ràng: “Không phải mục lục.” — không được suy diễn hoặc giả định.
#
#             Mục lục thường có các đặc điểm như:
#             - Có từ khóa như “CHƯƠNG”, “MỤC LỤC”, “Nội dung”, “Thông tin”, “Báo cáo…”
#             - Có cấu trúc liệt kê theo thứ tự, có thể kèm số trang hoặc dấu “∙”, “-”, “•”
#             - Có nhiều tiêu đề ngắn gọn liên tiếp
#
#             Dưới đây là nội dung cần phân tích:
#             NGÂN HÀNG
# THƯƠNG MẠI CỔ
# PHẦN LỘC PHÁT VIỆT
# NAM
# Digitally signed by NGÂN
# HÀNG THƯƠNG MẠI CỔ
# PHẦN LỘC PHÁT VIỆT NAM
# Date: 2025.04.18 23:28:57
# +07'00'
# B ÁO  C ÁO  TH ƯỜN G  N IÊ N  2 024
#             """
#     prompt = ChatPromptTemplate.from_template(prompt_template)
#     chain = ({"question": RunnablePassthrough()} | prompt | llm | StrOutputParser())
#     response = chain.invoke("Báo cáo thường niên LPBANK năm 2024")
#     print(response)


# check_table_contents()

def cut_pdf(input_pdf, output_pdf, start_page, end_page):
    """Extracts pages from start_page to end_page (inclusive) into a new PDF."""
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page_num in range(start_page - 1, end_page):  # 0-indexed
        writer.add_page(reader.pages[page_num])

    with open(output_pdf, "wb") as f_out:
        writer.write(f_out)


# cut_pdf("./landing/banking_financial_report/shb/2024.pdf", "./landing/banking_financial_report/shb/2024_fine_grain.pdf", start_page=7, end_page=12)


banking_report_filepath = pathlib.Path(
    '/Users/binhnt8/Desktop/work/learning/code/y3a/landing/banking_financial_report/shb/2024_fine_grain.pdf')


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
                mime_type='application/pdf',
            ),
            prompt])
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
    if re.match(r'^[|\-:\s]+$', line) and '|' in line:
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
        if current_chunk and len(current_chunk + "\n\n" + paragraph) > semantic_splitter._chunk_size:
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


def chunk_the_extracted_report():
    with open("landing/banking_financial_report/vpb/extracted_2024.md", "r", encoding="utf-8") as f:
        markdown_text = f.read()

    headers_to_split_on = [
        ("###", "BÁO CÁO TÌNH HÌNH TÀI CHÍNH HỢP NHẤT"),
        ("###", "BÁO CÁO LƯU CHUYỂN TIỀN TỆ HỢP NHẤT"),
        ("###", "CÁC CHỈ TIÊU NGOÀI BÁO CÁO TÌNH HÌNH TÀI CHÍNH HỢP NHẤT"),
        ("###", "BÁO CÁO LƯU CHUYỂN TIỀN TỆ HỢP NHẤT")
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
                final_chunks.append(Document(
                    page_content=section_content,
                    metadata={**doc.metadata, "content_type": "table"}
                ))
            else:
                # Apply semantic chunking to regular text
                sub_chunks = smart_split_text(section_content, semantic_splitter)
                for chunk in sub_chunks:
                    if chunk.strip():
                        final_chunks.append(Document(
                            page_content=chunk,
                            metadata={**doc.metadata, "content_type": "text"}
                        ))

    print(f"Total chunks created: {len(final_chunks)}")

    # Display results
    for i, doc in enumerate(final_chunks):
        print(f"\n--- Chunk {i + 1} ---")
        print(f"Metadata: {doc.metadata}")
        print(f"Content ({doc.page_content}):")
        print()

    return final_chunks


chunk_the_extracted_report()
# extract_information_from_report(banking_report_filepath)
