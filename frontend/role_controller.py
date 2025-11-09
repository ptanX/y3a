from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    CUSTOMER_RELATION = "customer_relation"
    CREDIT_MANAGER = "credit_manager"


# User database with roles
USERS = {
    "admin": {
        "password": "admin123",
        "role": "admin",
        "full_name": "Administrator"
    },
    "manager": {
        "password": "manager123",
        "role": "manager",
        "full_name": "Manager User"
    },
    "user": {
        "password": "user123",
        "role": "user",
        "full_name": "Regular User"
    },
}

# Role permissions
ROLE_PERMISSIONS = {
    "admin": ["upload", "details", "users", "settings"],
    "manager": ["details", "chat_agent"],
    "user": ["upload"],
}
