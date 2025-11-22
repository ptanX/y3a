import streamlit as st

from frontend.menu import menu_with_redirect, get_role_badge
from frontend.role_controller import ROLE_PERMISSIONS

menu_with_redirect()

# SETTINGS PAGE
st.title("⚙️ Settings")
st.write(
    f"Logged in as: **{st.session_state.full_name}** ({get_role_badge(st.session_state.role)})"
)
st.divider()

st.markdown("### Application Settings")

with st.form("settings_form"):
    app_name = st.text_input("Application Name", value="Multi-Page App")
    max_upload_size = st.number_input(
        "Max Upload Size (MB)", value=10, min_value=1, max_value=100
    )
    allow_multiple_files = st.checkbox("Allow Multiple File Uploads", value=True)

    submitted = st.form_submit_button("Save Settings", type="primary")
    if submitted:
        st.success("✅ Settings saved successfully!")

st.divider()

st.markdown("### Role Permissions Matrix")

import pandas as pd

permissions_data = []
for role, perms in ROLE_PERMISSIONS.items():
    permissions_data.append(
        {
            "Role": get_role_badge(role),
            "Upload": "✅" if "upload" in perms else "❌",
            "Details": "✅" if "details" in perms else "❌",
            "Users": "✅" if "users" in perms else "❌",
            "Settings": "✅" if "settings" in perms else "❌",
        }
    )

df = pd.DataFrame(permissions_data)
st.dataframe(df, use_container_width=True, hide_index=True)
