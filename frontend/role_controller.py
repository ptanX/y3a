"""
role_controller.py – Quản lý Role và Permission.
Khi thêm plugin mới, thêm permission key vào ROLE_PERMISSIONS bên dưới.
"""
from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    CUSTOMER_RELATION = "customer_relation"
    CREDIT_MANAGER = "credit_manager"


# User database (production: thay bằng database thực)
USERS = {
    "manager": {
        "password": "manager123",
        "role": "manager",
        "full_name": "Manager User",
    },
    "user": {
        "password": "user123",
        "role": "user",
        "full_name": "Regular User",
    },
}

# ── Role Permissions ─────────────────────────────────────────────────────────
# Mỗi key là permission_id phải khớp với "required_permission" trong manifest.json
# Thêm plugin mới → thêm permission key ở đây và trong manifest.json của plugin
ROLE_PERMISSIONS = {
    # Manager: toàn quyền truy cập mọi plugin và trang
    "manager": [
        # lending-analysis plugin pages
        "details",
        "chat_agent",
        "base_information",
        # esg-risk plugin pages (khi plugin này được enable)
        "esg_risk",
    ],
    # User (Quan hệ Khách hàng): chỉ upload hồ sơ
    "user": [
        # lending-analysis plugin pages
        "upload",
    ],
}
