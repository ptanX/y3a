import streamlit as st

from frontend.menu import menu_with_redirect, get_role_badge
from frontend.role_controller import USERS, ROLE_PERMISSIONS

menu_with_redirect()

# USERS PAGE
st.title("👥 User Management")
st.write(
    f"Logged in as: **{st.session_state.full_name}** ({get_role_badge(st.session_state.role)})"
)
st.divider()

st.markdown("### Registered Users")

for username, user_data in USERS.items():
    with st.expander(
        f"{get_role_badge(user_data['role'])} - {user_data['full_name']} (@{username})"
    ):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Username:** {username}")
            st.write(f"**Full Name:** {user_data['full_name']}")
        with col2:
            st.write(f"**Role:** {user_data['role']}")
            st.write(
                f"**Permissions:** {', '.join(ROLE_PERMISSIONS[user_data['role']])}"
            )
