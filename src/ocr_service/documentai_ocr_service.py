from src.ocr_service.ocr_service import OCRService, OCRRequest, OCRResult
from src.lending.pdf_text_extractor import DocumentAIExtractor


class DocumentAIOCRService(OCRService):
    """
    Triển khai OCRService dùng Google Cloud Document AI.
    Bọc toàn bộ DocumentAIExtractor hiện có bên dưới interface chuẩn.
    """

    def __init__(
        self,
        project_id: str,
        location: str,
        processor_id: str,
        processor_version: str = None,
    ):
        self._extractor = DocumentAIExtractor(
            project_id=project_id,
            location=location,
            processor_id=processor_id,
            processor_version=processor_version,
        )

    def extract(self, request: OCRRequest) -> OCRResult:
        """Trích xuất toàn bộ văn bản từ tài liệu."""
        try:
            raw = self._extractor.extract_raw_document(
                file_path=request.file_path,
                mime_type=request.mime_type,
            )
            return OCRResult(
                file_path=request.file_path,
                structured_data=raw,
                success=True,
            )
        except Exception as e:
            return OCRResult(
                file_path=request.file_path,
                success=False,
                error_message=str(e),
            )

    def extract_fields(self, request: OCRRequest) -> OCRResult:
        """Trích xuất các fields có cấu trúc - dùng cho bảng biểu kế toán."""
        try:
            normalized = self._extractor.extract_normalized_text(
                file_path=request.file_path
            )
            return OCRResult(
                file_path=request.file_path,
                structured_data=normalized,
                success=True,
            )
        except Exception as e:
            return OCRResult(
                file_path=request.file_path,
                success=False,
                error_message=str(e),
            )
