import streamlit as st
from PIL import Image

from frontend.constants import LOGO_ICO_PATH
from frontend.menu import has_permission
from frontend.role_controller import USERS
from frontend.utils import build_logo_before_title_html

logo_image = Image.open(LOGO_ICO_PATH)
st.set_page_config(page_title="Login", page_icon=logo_image)

# LOGIN PAGE
col1, col2, col3 = st.columns([1, 2, 1])

query_params = st.query_params
if query_params is not None:
    if query_params.get("document_id"):
        st.session_state.document_id = query_params.get("document_id")

with col2:
    st.markdown(
        build_logo_before_title_html("Đăng nhập"),
        unsafe_allow_html=True,
    )

    with st.form("login_form"):
        username = st.text_input("Tài khoản", placeholder="Nhập tên tài khoản")
        password = st.text_input(
            "Mật khẩu", type="password", placeholder="Nhập mật khẩu"
        )

        submitted = st.form_submit_button(
            "Đăng nhập", use_container_width=True, type="primary"
        )

        if submitted:
            if username and password:
                user_data = USERS.get(username)
                if user_data and user_data["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = user_data["role"]
                    st.session_state.full_name = user_data["full_name"]
                    st.success(
                        f"Đăng nhập thành công! Chào mừng {user_data['full_name']}"
                    )

                    # Navigate to first available page
                    if has_permission("upload"):
                        st.switch_page("pages/upload.py")
                    elif (
                        has_permission("details") and "document_id" in st.session_state
                    ):
                        st.switch_page("pages/detail.py")
                    else:
                        st.switch_page("pages/chat_agent.py")
                else:
                    st.error("Tên tài khoản hoặc mật khẩu không chính xác")
            else:
                st.error("Hãy nhập đầy đủ tên tài khoản và mật khẩu")
