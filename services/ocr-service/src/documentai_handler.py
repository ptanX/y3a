"""
DocumentAIHandler – bọc Google Cloud Document AI bên trong ocr-service.
File này tồn tại độc lập, không phụ thuộc vào src/ của lending-service.
"""

from typing import Any, Dict, List
from collections import defaultdict

from google.cloud import documentai
from google.api_core.client_options import ClientOptions
from google.cloud.documentai_v1 import Document
import json


class DocumentAIHandler:
    def __init__(self, project_id: str, location: str, processor_id: str):
        self.project_id = project_id
        self.location = location
        self.processor_id = processor_id

        api_endpoint = f"{location}-documentai.googleapis.com"
        options = ClientOptions(api_endpoint=api_endpoint)
        self._client = documentai.DocumentProcessorServiceClient(client_options=options)
        self._resource_name = self._client.processor_path(project_id, location, processor_id)

    def extract_fields_from_bytes(self, content: bytes, mime_type: str = "application/pdf") -> Dict[str, Any]:
        """Trích xuất fields có cấu trúc từ bytes."""
        raw_document = documentai.RawDocument(content=content, mime_type=mime_type)
        request = documentai.ProcessRequest(
            name=self._resource_name,
            raw_document=raw_document,
            process_options=documentai.ProcessOptions(),
        )
        result = self._client.process_document(request=request)
        doc_json = Document.to_json(result.document)
        return json.loads(doc_json)

    def extract_text_from_bytes(self, content: bytes, mime_type: str = "application/pdf") -> str:
        """Trích xuất văn bản thô từ bytes."""
        raw_document = documentai.RawDocument(content=content, mime_type=mime_type)
        request = documentai.ProcessRequest(
            name=self._resource_name,
            raw_document=raw_document,
        )
        result = self._client.process_document(request=request)
        return result.document.text
