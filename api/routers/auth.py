"""
Auth Router – Xác thực người dùng.
POST /api/auth/login   → Đăng nhập, nhận JWT token
POST /api/auth/logout  → Đăng xuất
GET  /api/auth/me      → Lấy thông tin user hiện tại
"""

import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel

# Import user database từ role_controller cũ
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent.parent))
from frontend.role_controller import USERS, ROLE_PERMISSIONS

router = APIRouter()
security = HTTPBearer()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "rawiq-default-secret-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 giờ


# ── Models ────────────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    full_name: str
    permissions: list[str]


class UserInfo(BaseModel):
    username: str
    role: str
    full_name: str
    permissions: list[str]


# ── Helpers ───────────────────────────────────────────────────────────────────
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None or username not in USERS:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token không hợp lệ.")
        user = USERS[username]
        return {
            "username": username,
            "role": user["role"],
            "full_name": user["full_name"],
            "permissions": ROLE_PERMISSIONS.get(user["role"], []),
        }
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token hết hạn hoặc không hợp lệ.")


# ── Endpoints ─────────────────────────────────────────────────────────────────
@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    """Đăng nhập bằng username/password, nhận JWT token."""
    user = USERS.get(request.username)
    if not user or user["password"] != request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai tên đăng nhập hoặc mật khẩu."
        )
    token = create_access_token(
        data={"sub": request.username, "role": user["role"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return LoginResponse(
        access_token=token,
        role=user["role"],
        full_name=user["full_name"],
        permissions=ROLE_PERMISSIONS.get(user["role"], []),
    )


@router.get("/me", response_model=UserInfo)
def get_me(current_user: dict = Depends(get_current_user)):
    """Lấy thông tin user đang đăng nhập."""
    return UserInfo(**current_user)
