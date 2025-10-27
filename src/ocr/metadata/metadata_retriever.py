import io
from abc import ABC, abstractmethod
from typing import Dict

from PyPDF2 import PdfReader, PdfWriter


def cut_pdf_to_bytes(input_pdf: str, start_page: int, end_page: int) -> bytes:
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page_num in range(start_page - 1, end_page):  # 0-indexed
        writer.add_page(reader.pages[page_num])
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


class DocumentationMetadataRetriever(ABC):

    @abstractmethod
    def retrieve(self) -> Dict:
        pass
