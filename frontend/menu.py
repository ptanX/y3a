import streamlit as st

from role_controller import ROLE_PERMISSIONS


def has_permission(page):
    if not st.session_state.logged_in:
        return False
    return page in ROLE_PERMISSIONS.get(st.session_state.role, [])


def get_role_badge(role):
    badges = {
        "admin": "🔴 Admin",
        "manager": "🟡 Manager",
        "user": "🟢 User",
    }
    return badges.get(role, "👤 User")


def authenticated_menu():
    st.sidebar.title("RawIQ")
    st.sidebar.write(f"Xin chào **{st.session_state.full_name}**")

    st.sidebar.divider()

    if has_permission("upload"):
        if st.sidebar.button("📤 Upload", use_container_width=True, key="nav_upload"):
            st.switch_page("pages/upload.py")

    if has_permission("details"):
        if st.sidebar.button("📋 Chi tiết", use_container_width=True, key="nav_details"):
            st.switch_page("pages/detail.py")

    if has_permission("chat_agent"):
        if st.sidebar.button("👥 Chat Agentic", use_container_width=True, key="nav_chat_agent"):
            st.switch_page("pages/chat_agent.py")

    if has_permission("users"):
        if st.sidebar.button("👥 Users", use_container_width=True, key="nav_users"):
            st.switch_page("pages/user.py")

    # Settings page (admin only)
    if has_permission("settings"):
        if st.sidebar.button("⚙️ Settings", use_container_width=True, key="nav_settings"):
            st.switch_page("pages/setting.py")

    st.sidebar.divider()

    if st.sidebar.button("🚪 Đăng xuất", use_container_width=True, key="nav_logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.session_state.full_name = ""
        st.switch_page("pages/login.py")


def unauthenticated_menu():
    st.sidebar.title("Please Login")
    if st.sidebar.button("🔐 Go to Login", use_container_width=True, key="nav_login_sidebar"):
        st.switch_page("pages/login.py")


def menu_with_redirect():
    query_params = st.query_params
    if query_params is not None:
        if query_params.get("document_id"):
            st.session_state.document_id = query_params.get("document_id")
        if query_params.get("financial_document_id"):
            st.session_state.financial_document_id = query_params.get("financial_document_id")
    # Check if logged in and has permission
    if "logged_in" not in st.session_state:
        st.warning("⚠️ Please login first")
        if st.button("Go to Login"):
            st.switch_page("pages/login.py")
        st.stop()

    menu()


def menu():
    if "role" not in st.session_state or st.session_state.role is None or not st.session_state.logged_in:
        unauthenticated_menu()
        return
    authenticated_menu()
