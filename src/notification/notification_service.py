from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class NotificationMessage:
    """Đối tượng chuẩn hóa dữ liệu thông báo gửi đi."""
    recipient_email: str
    subject: str
    body: str
    body_type: str = "html"  # "html" hoặc "plain"
    sender_email: Optional[str] = None


class NotificationService(ABC):
    """
    Interface trung tâm cho mọi loại thông báo (Email, SMS, Slack...).
    Khi muốn thêm kênh thông báo mới, chỉ cần tạo class
    kế thừa interface này mà không cần sửa business logic.
    """

    @abstractmethod
    def send(self, message: NotificationMessage) -> bool:
        """
        Gửi thông báo đến người nhận.

        Args:
            message: Đối tượng NotificationMessage chứa thông tin cần gửi.

        Returns:
            True nếu gửi thành công, False nếu thất bại.
        """
        pass
