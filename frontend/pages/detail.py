import json
import os

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from frontend.menu import menu_with_redirect
from src.bidv import e2e_usecases
from src.bidv.db.bidv_entity import DocumentationInformation
from src.bidv.startup.environment_initialization import DATABASE_PATH

menu_with_redirect()

# Streamlit App
st.set_page_config(page_title="Bảng Kiểm Tra Dữ Liệu", layout="wide")
st.title("📊 Kết Quả Bóc Tách Chi Tiết")

document_id = st.session_state.document_id
if not document_id:
    st.write("Không tìm thấy mã tài liệu")
    st.stop()

st.query_params.document_id = document_id

engine = create_engine(f"sqlite:///{DATABASE_PATH}")
session = sessionmaker(bind=engine)()
document_entity = session.get(DocumentationInformation, document_id)
if not document_entity:
    st.write(f"Không tìm thấy tài liệu với mã {document_id}")
    st.stop()

document_data = json.loads(document_entity.data)
data = document_data["validation_results"]

# Field labels mapping
field_labels_mapping = {
    "company_name_vn": "Tên công ty (VN)",
    "company_name_en": "Tên công ty (EN)",
    "company_abbr": "Tên viết tắt",
    "office_address": "Địa chỉ trụ sở",
}

field_columns_mapping = {
    "field": "Chỉ tiêu",
    "business_registration_cert": "Giấy phép ĐKKD",
    "company_charter": "Điều lệ",
    "database_value": "CSDL nội bộ (DB)",
    "is_consistent": "Nhất quán với các tài liệu",
    "is_match_database": "Nhất quán với DB",
    "user_input": "Ý kiến QHKH"
}


def json_to_dataframe(data):
    rows = []

    for idx, item in enumerate(data):
        # Get values from origin_docs
        cert_value = ""
        charter_value = ""

        for doc in item["origin_docs"]:
            if doc["name"] == "business_registration_cert":
                cert_value = doc["value"]
            elif doc["name"] == "company_charter":
                charter_value = doc["value"]

        coalesce = cert_value or charter_value or item["database_value"]
        row = {
            "field": item["field_name"],
            "business_registration_cert": cert_value,
            "company_charter": charter_value,
            "database_value": item["database_value"],
            "is_consistent": item["validation_result"]["is_consistent_across_doc"],
            "is_match_db": item["validation_result"]["is_match_database"],
            "coalesce": coalesce,
            "user_input": coalesce,
        }

        rows.append(row)

    return pd.DataFrame(rows)


def highlight_rows(row):
    style = ['background-color: white'] * (len(row))
    if not row["coalesce"]:
        # Red
        style = ['background-color: #FFCDD2'] * (len(row))
    if not row['is_consistent']:
        # Yellow
        style = ['background-color: #FFF9C4'] * (len(row))

    return style


def get_column_config():
    cols = {}
    for key, value in field_columns_mapping.items():
        cols[key] = st.column_config.Column(label=value, disabled=True)

    column_config = {
        **cols,
        "coalesce": None,
        "is_consistent": None,
        "is_match_db": None,
        "user_input": st.column_config.Column(
            field_columns_mapping.get("user_input")
        )
    }

    return column_config


if "my_data" not in st.session_state:
    df = json_to_dataframe(data)
    st.session_state.my_data = df


def handle_data_change():
    edited_rows = st.session_state.my_editor["edited_rows"]
    for index, values in edited_rows.items():
        st.session_state.my_data.at[index, "user_input"] = values["user_input"]


# Display the styled dataframe
st.data_editor(
    st.session_state.my_data.style.apply(highlight_rows, axis=1),
    column_config=get_column_config(),
    use_container_width=True,
    key="my_editor",
    on_change=handle_data_change,
    height=400
)


def submit():
    customer_info_result = dict(
        zip(st.session_state.my_data["field"], st.session_state.my_data["user_input"]))

    financial_document_id = document_data["financial_document_id"]
    base_url = os.environ.get("BASE_URL", "http://localhost:8501")
    detail_url = f"{base_url}/chat_agent?financial_document_id={financial_document_id}"

    request_body = {
        "document_id": document_data["document_id"],
        "financial_document_id": financial_document_id,
        "recipient_name": recipient_name,
        "recipient_email": recipient_email,
        "verification_time": document_data["verification_time"],
        "qhkh_name": document_data["recipient_name"],
        "customer_info_result": customer_info_result,
        "detail_url": detail_url
    }
    print(request_body)
    e2e_usecases.execute_submit_document(request_body)
    st.success(
        f"✅ Đã tiếp nhận yêu cầu thành công. Vui lòng đợi kết quả gửi vào hòm mail {recipient_email}")


# Display legend
st.markdown("### 📌 Chú thích:")
col1, col2 = st.columns(2)
with col1:
    st.markdown("🟨 Trường thông tin cần kiểm tra")
with col2:
    st.markdown("🟥 Trường thông tin không bóc tách được")
st.markdown("---")

with st.form("detail_form"):
    st.markdown("### Thông tin QTTD")

    recipient_name = st.text_input("Tên QTTD", placeholder="Tên QTTD")
    recipient_email = st.text_input("Email QTTD", placeholder="Email QTTD")

    submitted = st.form_submit_button("Submit", use_container_width=True, type="primary")

    if submitted:
        if not recipient_name:
            st.error("Vui lòng nhập Tên QTTD")
        elif not recipient_email:
            st.error("Vui lòng nhập Email QTTD")
        else:
            with st.spinner("🔄 Processing document..."):
                try:
                    submit()
                except Exception as e:
                    st.error(f"❌Lỗi xử lý yêu cầu: {e}")
