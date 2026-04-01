from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class OCRRequest:
    """Yêu cầu OCR chuẩn hóa đầu vào."""
    file_path: str
    mime_type: str = "application/pdf"
    options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OCRResult:
    """Kết quả OCR chuẩn hóa đầu ra."""
    file_path: str
    raw_text: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    fields: Optional[List[Dict[str, Any]]] = None
    success: bool = True
    error_message: Optional[str] = None


class OCRService(ABC):
    """
    Interface trung tâm cho mọi loại dịch vụ OCR.
    Khi muốn hoán đổi giữa Google Document AI, Azure Form Recognizer,
    hay một OCR Engine khác, chỉ cần tạo class kế thừa interface này
    mà không cần sửa business logic trong full_flow.py.
    """

    @abstractmethod
    def extract(self, request: OCRRequest) -> OCRResult:
        """
        Trích xuất văn bản và cấu trúc dữ liệu từ tài liệu.

        Args:
            request: OCRRequest chứa đường dẫn file và các tùy chọn.

        Returns:
            OCRResult chứa kết quả trích xuất.
        """
        pass

    @abstractmethod
    def extract_fields(self, request: OCRRequest) -> OCRResult:
        """
        Trích xuất các fields có cấu trúc từ form/bảng biểu.

        Args:
            request: OCRRequest chứa đường dẫn file.

        Returns:
            OCRResult với danh sách fields đã phân tích.
        """
        pass
