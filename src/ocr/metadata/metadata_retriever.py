import asyncio
import json
from abc import ABC, abstractmethod

from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.dispatcher.executions_dispatcher import ExecutionInput, ExecutionOutput, ExecutionDispatcher
from src.ocr.ocr_model import DocumentMetadata, DocumentType
from src.ocr.utils import cut_pdf_to_bytes

load_dotenv()


async def extract_single_page_raw_metadata(execution_input: ExecutionInput) -> ExecutionOutput:
    page_number = execution_input.handler_input.get("page")
    path = execution_input.handler_input.get("path")
    page_content_in_bytes = cut_pdf_to_bytes(input_pdf=path, start_page=page_number, end_page=page_number)
    prompt = """
        Phân tích trang PDF này và trích xuất thông tin theo định dạng JSON sau:
        
        1. Nếu trang này là MỤC LỤC (chứa danh sách các phần/chương với số trang):
           - Trích xuất thành cấu trúc JSON với key "table_of_contents"
           - Dịch tên mục sang tiếng Anh
           - Mỗi mục bao gồm: tên mục (đã dịch), from_page, to_page (nếu có)
        
        2. Nếu trang này là NỘI DUNG thông thường:
           - Trích xuất toàn bộ văn bản thành "raw_content"
        
        Định dạng JSON trả về:
        
        Cho trang MỤC LỤC:
        {
          "page_type": "table_of_contents",
          "table_of_contents": [
            {
              "section_name": "English translated section name",
              "from_page": số_trang_bắt_đầu,
              "to_page": số_trang_kết_thúc (nếu có)
            }
          ]
        }
        
        Cho trang NỘI DUNG:
        {
          "page_type": "content",
          "raw_content": "toàn_bộ_văn_bản_của_trang"
        }
        
        Yêu cầu:
        - Trích xuất chính xác tất cả văn bản tiếng Việt
        - Dịch tên các mục trong mục lục sang tiếng Anh (section_name)
        - Giữ nguyên định dạng số liệu, ký hiệu đặc biệt
        - Phân loại chính xác loại trang (mục lục hay nội dung)
        - Chỉ trả về JSON, không có văn bản giải thích thêm
        
        Phân tích trang PDF và trả về JSON:
        """

    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(
                data=page_content_in_bytes,
                mime_type="application/pdf",
            ),
            prompt,
        ],
    )
    output = json.loads(
        response.text.replace("```json", "").replace("```", "").strip()
    )
    return ExecutionOutput(handler_name=execution_input.handler_name, handler_output=output)


class DocumentationMetadataRetriever(ABC):

    @abstractmethod
    def retrieve(self, path: str) -> DocumentMetadata:
        pass


class LocalDocumentationMetadataRetriever(DocumentationMetadataRetriever):

    def __init__(self, execution_dispatcher: ExecutionDispatcher):
        self.execution_dispatcher = execution_dispatcher
    def retrieve(self, path: str) -> DocumentMetadata:
        if "dkdn" in path:
            doc_type = DocumentType.BUSINESS_REGISTRATION
        elif "dl" in path:
            doc_type = DocumentType.COMPANY_CHARTER
        elif "bctc" in path:
            doc_type = DocumentType.SECURITIES_FINANCIAL_REPORT
        else:
            raise ValueError(f"path: {path} is invalid type")
        return None

    async def retrieve_financial_report(self, path: str) -> DocumentMetadata:
        list_inputs = []
        for i in range(1, 11):
            execution_input = ExecutionInput(handler_name="extract_single_page_raw_metadata", handler_input={"page": i, path: path})
            list_inputs.append(execution_input)
        results = await self.execution_dispatcher.dispatch(list_inputs=list_inputs)
        return None


