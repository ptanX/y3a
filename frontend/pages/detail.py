import json

import pandas as pd
import streamlit as st
from PIL import Image

from frontend.constants import LOGO_ICO_PATH, Pages
from frontend.menu import menu_with_redirect
from frontend.utils import build_logo_before_title_html
from src.lending import e2e_usecases
from src.lending.constant import REQUIRED_EXTRACTION_FIELDS
from src.lending.services.db_service import query_document_information_by_id

menu_with_redirect(Pages.DETAIL)
logo_image = Image.open(LOGO_ICO_PATH)

# Streamlit App
st.set_page_config(
    page_title="Bảng kiểm tra dữ liệu", page_icon=logo_image, layout="wide"
)
st.markdown(
    build_logo_before_title_html("Kết quả bóc tách chi tiết"),
    unsafe_allow_html=True,
)
st.divider()

document_id = st.session_state.document_id
if not document_id:
    st.write("Không tìm thấy mã tài liệu")
    st.stop()

st.query_params.document_id = document_id

document_entity = query_document_information_by_id(document_id)
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
    "phone": "Số điện thoại",
    "charter_capital": "Vốn điều lệ",
    "legal_rep": "Người đại diện pháp luật",
    "email": "Email công ty",
    "par_value": "Mệnh giá (đồng)",
    "total_shares": "Tổng số cổ phần",
    "business_code": "Mã số thuế/Mã số doanh nghiệp",
}

field_columns_mapping = {
    "full_field_name": "Chỉ tiêu",
    "field_name": "Chỉ tiêu (viết tắt)",
    "business_registration_cert": "Giấy phép ĐKKD",
    "company_charter": "Điều lệ",
    "database_value": "CSDL nội bộ (DB)",
    "is_consistent": "Nhất quán với các tài liệu",
    "is_match_database": "Nhất quán với DB",
    "user_input": "Ý kiến QHKH",
}


def build_extraction_data(data):
    rows = []

    for idx, item in enumerate(data):
        if item["field_name"] not in field_labels_mapping.keys():
            continue
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
            "full_field_name": field_labels_mapping.get(item["field_name"]),
            "field_name": item["field_name"],
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
    length = len(row)
    style = ["background-color: white"] * length
    if not row["user_input"]:
        # Red
        style = ["background-color: #FFCDD2"] * length
    if not row["is_consistent"]:
        # Yellow
        style = ["background-color: #FFF9C4"] * length

    return style


def get_column_config():
    cols = {}
    for key, value in field_columns_mapping.items():
        cols[key] = st.column_config.Column(label=value, disabled=True)

    column_config = {
        **cols,
        "field_name": None,
        "coalesce": None,
        "is_consistent": None,
        "is_match_db": None,
        "user_input": st.column_config.Column(field_columns_mapping.get("user_input")),
    }

    return column_config


if "my_data" not in st.session_state:
    st.session_state.my_data = build_extraction_data(data)


def handle_data_change():
    edited_rows = st.session_state.my_editor["edited_rows"]
    for index, values in edited_rows.items():
        if "user_input" not in values:
            continue
        st.session_state.my_data.at[index, "user_input"] = values["user_input"]


# Display the styled dataframe
st.data_editor(
    st.session_state.my_data.style.apply(highlight_rows, axis=1),
    column_config=get_column_config(),
    width="stretch",
    key="my_editor",
    on_change=handle_data_change,
    height=400,
    hide_index=True,
)


def submit():
    customer_info_result = dict(
        zip(
            st.session_state.my_data["field_name"],
            st.session_state.my_data["user_input"],
        )
    )

    all_keys = list(customer_info_result.keys())
    missing_keys = set(REQUIRED_EXTRACTION_FIELDS) - set(all_keys)
    none_keys = [
        key
        for key, value in customer_info_result.items()
        if value is None or value == ""
    ]

    missing_keys = none_keys + list(missing_keys)
    missing_key_names = [field_labels_mapping[key] for key in missing_keys]

    request_body = {
        "document_id": document_data["document_id"],
        "recipient_name": recipient_name,
        "recipient_email": recipient_email,
        "verification_time": document_data["verification_time"],
        "qhkh_name": document_data["recipient_name"],
        "customer_name": customer_info_result["company_name_vn"],
        "customer_info_result": customer_info_result,
        "missing_key_names": missing_key_names,
    }

    print(request_body)
    e2e_usecases.execute_submit_document(request_body)
    st.success(
        f"✅ Đã tiếp nhận yêu cầu thành công. Vui lòng đợi kết quả gửi vào hòm mail {recipient_email}"
    )


# Display legend
st.markdown("### Chú thích:")
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

    submitted = st.form_submit_button("Submit", width="stretch", type="primary")

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
