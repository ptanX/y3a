import json
from abc import ABC, abstractmethod
from typing import List

from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.dispatcher.executions_dispatcher import (
    ExecutionInput,
    ExecutionOutput,
    ExecutionDispatcher,
)
from src.ocr.ocr_model import (
    DocumentMetadata,
    DocumentType,
    MetadataPageType,
    DocumentMetadataPageInfo,
)
from src.ocr.utils import cut_pdf_to_bytes

load_dotenv()


async def extract_single_page_raw_metadata(
        execution_input: ExecutionInput,
) -> ExecutionOutput:
    page_number = execution_input.execution_id
    path = execution_input.input_content
    page_content_in_bytes = cut_pdf_to_bytes(
        input_pdf=path, start_page=page_number, end_page=page_number
    )
    prompt = """
        Phân tích trang PDF và trả về JSON:

        Nếu là MỤC LỤC:
        {
          "page_type": "table_of_contents",
          "table_of_contents": [
            {
              "section_name": "English translation using standard financial terms",
              "from_page": number,
              "to_page": number
            }
          ]
        }
        
        Nếu là NỘI DUNG:
        {
          "page_type": "content", 
          "raw_content": "toàn bộ văn bản"
        }
        
        Thuật ngữ chuẩn:
        - Thông tin chung → General Information
        - Báo cáo của Ban Tổng Giám đốc → Board of Directors Report  
        - Báo cáo kiểm toán độc lập → Independent Auditor's Report
        - Báo cáo tình hình tài chính hợp nhất → Consolidated Financial Statements
        - Báo cáo kết quả hoạt động hợp nhất → Consolidated Income Statement
        - Báo cáo lưu chuyển tiền tệ hợp nhất → Consolidated Cash Flow Statement
        - Thuyết minh báo cáo tài chính hợp nhất → Notes to Consolidated Financial Statements
        
        Chỉ trả về JSON thuần:
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
    print(response.text)
    output = json.loads(response.text.replace("```json", "").replace("```", "").strip())
    return ExecutionOutput(
        handler_name=execution_input.handler_name,
        execution_id=execution_input.execution_id,
        output_content=output,
    )


async def retrieve_securities_financial_report(execution_dispatcher: ExecutionDispatcher,
                                               path: str) -> List[DocumentMetadata]:
    list_inputs = []
    for i in range(1, 11):
        execution_input = ExecutionInput(
            handler_name="extract_single_page_metadata",
            execution_id=i,
            input_content=path,
        )
        list_inputs.append(execution_input)
    results = await execution_dispatcher.dispatch(list_inputs=list_inputs)
    table_of_contents = get_table_of_contents(results)
    if is_table_of_contents(table_of_contents) is True:
        return retrieve_securities_financial_metadata_from_toc(
            toc_page=table_of_contents.get("page"),
            toc=table_of_contents.get("table_of_contents"),
        )
    return []


def is_table_of_contents(table_of_contents):
    return table_of_contents.get("is_table_of_contents")


def retrieve_securities_financial_metadata_from_toc(toc_page, toc) -> List[DocumentMetadata]:
    results = []
    for content in toc:
        section_name = content.get("section_name")
        if section_name is not None and "financial" in section_name.lower() and "notes" not in section_name.lower():
            page_range = DocumentMetadataPageInfo(
                from_page=toc_page + content.get("from_page"),
                to_page=toc_page + content.get("to_page"),
            )
            document_metadata = DocumentMetadata(
                component_type="financial_statement", page_info=page_range
            )
            results.append(document_metadata)
        elif section_name is not None and "income" in section_name.lower() and "notes" not in section_name.lower():
            page_range = DocumentMetadataPageInfo(
                from_page=toc_page + content.get("from_page"),
                to_page=toc_page + content.get("to_page"),
            )
            document_metadata = DocumentMetadata(
                component_type="income_statement", page_info=page_range
            )
            results.append(document_metadata)
    return results

# def retrieve_securities_financial_metadata_from_raw(raw_inputs: List[ExecutionOutput]) -> List[DocumentMetadata]:
#     for raw_input in raw_inputs:
#         if "KPMG" in raw_input.output_content.get("raw_content", ""):
#             return []


def get_table_of_contents(raw_page_contents: List[ExecutionOutput]):
    for execution_output in raw_page_contents:
        if MetadataPageType.TABLE_OF_CONTENTS.value == execution_output.output_content.get("page_type"):
            return {
                "is_table_of_contents": True,
                "page": execution_output.execution_id,
                "table_of_contents": execution_output.output_content.get("table_of_contents"),
            }
    return {"is_table_of_contents": False}


class DocumentationMetadataRetriever(ABC):

    @abstractmethod
    def retrieve(self, path: str) -> DocumentMetadata:
        pass


class LocalDocumentationMetadataRetriever(DocumentationMetadataRetriever):

    def __init__(self, execution_dispatcher: ExecutionDispatcher):
        self.execution_dispatcher = execution_dispatcher

    async def retrieve(self, path: str) -> List[DocumentMetadata]:
        if "dkdn" in path:
            return [DocumentMetadata(component_type=DocumentType.BUSINESS_REGISTRATION.value)]
        elif "dl" in path:
            return [DocumentMetadata(component_type=DocumentType.COMPANY_CHARTER.value)]
        elif "bctc" in path:
            return await retrieve_securities_financial_report(self.execution_dispatcher, path)
        else:
            raise ValueError(f"path: {path} is invalid type")

# if __name__ == "__main__":
#     input_path = (
#         "/Users/binhnt8/Desktop/work/learning/code/y3a/documentations/bctc_2023.pdf"
#     )
#     execution_dispatcher = (
#         ExecutionDispatcherBuilder()
#             .set_dispatcher(
#             name="extract_single_page_metadata",
#             handler=extract_single_page_raw_metadata,
#         )
#             .build()
#     )
#     metadata_retriever = LocalDocumentationMetadataRetriever(
#         execution_dispatcher=execution_dispatcher
#     )
#     doc_metadata = asyncio.run(metadata_retriever.retrieve(path=input_path))
#     print(doc_metadata)
