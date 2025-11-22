import io

from PyPDF2 import PdfReader, PdfWriter


def cut_pdf_to_bytes(input_path: str, start_page: int, end_page: int) -> bytes:
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page_num in range(start_page - 1, end_page):  # 0-indexed
        writer.add_page(reader.pages[page_num])
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def get_total_page(input_path: str) -> int:
    reader = PdfReader(input_path)
    return len(reader.pages)
