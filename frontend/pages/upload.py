import os
import uuid
from datetime import datetime

import streamlit as st

from frontend.menu import menu_with_redirect, get_role_badge
from src.bidv import e2e_usecases

menu_with_redirect()

# UPLOAD PAGE
st.title("📤 Upload Tài liệu Thủ Tục Vay Vốn")
st.divider()


def submit(upload_record):
    e2e_usecases.execute(upload_record)

    st.success("✅ Đã tiếp nhận yêu cầu thành công. Vui lòng đợi kết quả gửi vào hòm mail!")
    st.write(f"**Mã yêu cầu:** {document_id}")
    st.write(f"**Tên QHKH:** {recipient_name}")
    st.write(f"**Email QHKH:** {recipient_email}")
    st.write(f"**Tài liệu đã tải lên:** {len(uploaded_files)}")
    for uploaded_file in uploaded_files:
        st.write(f"  - {uploaded_file.name}")


with st.form("upload_form"):
    # Tên QHKH field
    recipient_name = st.text_input("Tên QHKH", placeholder="Tên QHKH")

    # Email QHKH field
    recipient_email = st.text_input("Email QHKH", placeholder="Email QHKH")

    # File upload field
    st.write("Upload file KH")
    uploaded_files = st.file_uploader(
        "Choose files",
        accept_multiple_files=True,
        type=['pdf', 'doc', 'docx', 'txt'],
        label_visibility="collapsed"
    )

    # Display uploaded file names
    if uploaded_files:
        st.write("**Selected files:**")
        for uploaded_file in uploaded_files:
            st.write(f"📄 {uploaded_file.name}")

    # Submit button
    submitted = st.form_submit_button("Submit", use_container_width=True, type="primary")

    if submitted:
        if not recipient_name:
            st.error("Vui lòng nhập Tên QHKH")
        elif not recipient_email:
            st.error("Vui lòng nhập Email QHKH")
        elif not uploaded_files:
            st.error("Vui lòng chọn file để upload")
        else:
            # Store uploaded data
            base_url = os.environ.get("BASE_URL", "http://localhost:8501")
            document_id = str(uuid.uuid4())
            upload_record = {
                'document_id': document_id,
                'recipient_name': recipient_name,
                'recipient_email': recipient_email,
                "detail_url": f"{base_url}/detail?document_id={document_id}",
                'files': uploaded_files,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'uploaded_by': st.session_state.username,
                'uploaded_by_name': st.session_state.full_name,
            }

            submit(upload_record)
