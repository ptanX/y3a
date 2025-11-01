import streamlit as st

from frontend.menu import menu_with_redirect, has_permission, get_role_badge
from frontend.role_controller import USERS

# LOGIN PAGE
st.title("🔐 Login")

col1, col2, col3 = st.columns([1, 2, 1])

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
                    else:
                        st.switch_page("pages/detail.py")
                else:
                    st.error("Invalid credentials")
            else:
                st.error("Please enter both username and password")

    st.divider()
    st.markdown("### 💡 Demo Accounts")
    st.markdown("""
        | Username | Password | Role | Access |
        |----------|----------|------|--------|
        | `admin` | `admin123` | 🔴 Admin | Full access |
        | `manager` | `manager123` | 🟡 Manager | Upload, Details, Users |
        | `user` | `user123` | 🟢 User | Upload, Details |
        """)
