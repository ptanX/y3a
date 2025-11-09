import streamlit as st

from frontend.menu import has_permission
from frontend.role_controller import USERS

# LOGIN PAGE
st.title("🔐 Login")

col1, col2, col3 = st.columns([1, 2, 1])

query_params = st.query_params
if query_params is not None:
    if query_params.get("document_id"):
        st.session_state.document_id = query_params.get("document_id")
    if query_params.get("financial_document_id"):
        st.session_state.financial_document_id = query_params.get("financial_document_id")

with col2:
    st.markdown("### Please login to continue")

    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        submitted = st.form_submit_button("Login", use_container_width=True, type="primary")

        if submitted:
            if username and password:
                user_data = USERS.get(username)
                if user_data and user_data["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = user_data["role"]
                    st.session_state.full_name = user_data["full_name"]
                    st.success(f"Login successful! Welcome {user_data['full_name']}")

                    # Navigate to first available page
                    if has_permission("upload"):
                        st.switch_page("pages/upload.py")
                    elif has_permission("details") and "document_id" in st.session_state:
                        st.switch_page("pages/detail.py")
                    else:
                        st.switch_page("pages/chat_agent.py")
                else:
                    st.error("Invalid credentials")
            else:
                st.error("Please enter both username and password")
