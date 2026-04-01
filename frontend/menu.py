"""
menu.py – Sidebar navigation được render ĐỘNG từ Plugin Registry.
Thêm plugin mới không cần sửa file này, chỉ cần:
1. Tạo thư mục plugins/<id>/manifest.json
2. Bật plugin trong plugin_registry/registry.json
"""
import sys
from pathlib import Path
from typing import Union

import streamlit as st
from PIL import Image

# Đảm bảo plugin_registry import được từ Streamlit
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from role_controller import ROLE_PERMISSIONS
from plugin_registry.plugin_loader import plugin_loader


def display_logo():
    logo_path = Path(__file__).parent.absolute().joinpath("images").joinpath("logo.jpg")
    logo_image = Image.open(str(logo_path))
    st.logo(str(logo_path), size="large", icon_image=logo_image)


def has_permission(page: str) -> bool:
    if not st.session_state.get("logged_in", False):
        return False
    return page in ROLE_PERMISSIONS.get(st.session_state.get("role", ""), [])


def authenticated_menu():
    st.sidebar.title("RawIQ")
    st.sidebar.write(f"Xin chào **{st.session_state.get('full_name', '')}**")
    st.sidebar.divider()

    # ── Nạp plugin và render menu ĐỘNG ────────────────────────────────────────
    plugins = plugin_loader.load_all()

    if not plugins:
        st.sidebar.warning("⚠️ Chưa có plugin nào được kích hoạt.")
    else:
        for plugin in plugins:
            # Mỗi plugin có thể có nhiều trang con
            _render_plugin_pages(plugin)

    # ── Logout (luôn luôn hiển thị) ────────────────────────────────────────────
    st.sidebar.divider()
    if st.sidebar.button("Đăng xuất", use_container_width=True, key="nav_logout"):
        for key in ["logged_in", "username", "role", "full_name", "document_id"]:
            st.session_state[key] = None if key == "document_id" else (
                False if key == "logged_in" else ""
            )
        st.switch_page("pages/login.py")


def _render_plugin_pages(plugin):
    """Render tất cả các trang con của một plugin vào sidebar."""
    import json
    manifest_path = PROJECT_ROOT / "plugins" / plugin.id / "manifest.json"
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
        pages = manifest_data.get("pages", [])
    except Exception:
        # Fallback: dùng nav_page chính của plugin
        pages = [{"id": plugin.id, "label": f"{plugin.icon} {plugin.nav_label}",
                   "path": plugin.nav_page, "permission": plugin.required_permission}]

    for page in pages:
        permission = page.get("permission", plugin.required_permission)
        if has_permission(permission):
            btn_key = f"nav_{plugin.id}_{page['id']}"
            if st.sidebar.button(page["label"], use_container_width=True, key=btn_key):
                # Chuyển hướng tới đúng page file của plugin
                page_path = page["path"].replace("frontend/", "")
                st.switch_page(page_path)


def unauthenticated_menu():
    st.switch_page("pages/login.py")


def menu_with_redirect(page_name: Union[str, None]):
    st.session_state.redirect_to = page_name

    query_params = st.query_params
    if query_params and query_params.get("document_id"):
        st.session_state.document_id = query_params.get("document_id")

    if "logged_in" not in st.session_state:
        st.switch_page("pages/login.py")

    menu()


def menu():
    if (
        "role" not in st.session_state
        or st.session_state.role is None
        or not st.session_state.get("logged_in", False)
    ):
        unauthenticated_menu()
    authenticated_menu()
