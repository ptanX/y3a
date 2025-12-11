import json

import pandas as pd
import streamlit as st
from PIL import Image

from business_customer_loan_validation import (
    calculate_financial_metrics,
    build_financial_table_output,
)
from frontend.constants import LOGO_ICO_PATH, DICTIONARY_MAPPING
from frontend.menu import menu_with_redirect
from frontend.utils import build_logo_before_title_html
from src.lending.agent.mapping import DIMENSIONAL_MAPPING
from src.lending.services.db_service import query_document_information_by_id

menu_with_redirect()
logo_image = Image.open(LOGO_ICO_PATH)

# Streamlit App
st.set_page_config(
    page_title="Thông Tin Tài Chính Cơ Bản", page_icon=logo_image, layout="wide"
)
st.markdown(
    build_logo_before_title_html("Thông Tin Tài Chính Cơ Bản"),
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

if "data" not in st.session_state:
    st.session_state.data = json.loads(document_entity.data)

MAPPING = {
    "extracted_data": "Dữ liệu thô",
    "revenue_profit_table": "Sản lượng và Doanh thu",
    "financial_overview_table": "Tình hình Tài chính Cơ bản",
    "liquidity_ratios_table": "Khả năng Thanh toán",
    "operational_efficiency_table": "Hiệu quả Hoạt động",
    "leverage_table": "Cân nợ và Cơ cấu Vốn",
    "profitability_table": "Doanh thu và Lợi nhuận",
    "balance_sheet_horizontal": "Bảng cân đối kế toán (so sánh ngang)",
    "income_statement_horizontal": "Báo cáo kết quả kinh doanh (so sánh ngang)",
}

selected_label = st.selectbox(
    "Lựa chọn báo cáo:",
    options=list(MAPPING.values()),
)


def get_sample_data():
    with open("/Users/anhdv7/Desktop/practice/y3a/temp/final_result2.json", "r") as f:
        data = json.load(f)
    return data


def build_display_dataframe(selected_table, data_table):
    financial_metrics = calculate_financial_metrics(data_table)
    mapping = DIMENSIONAL_MAPPING.get(selected_table)
    financial_table_metrics = build_financial_table_output(
        financial_metrics=financial_metrics, mapping=mapping, reverse_order=False
    )
    df = pd.DataFrame(
        financial_table_metrics["data"], columns=financial_table_metrics["columns"]
    )
    df_display = df.fillna("-")
    return df_display


def render_common_statistics(selected_table):
    st.subheader(MAPPING.get(selected_table))
    data = st.session_state.data["base_information"]["financial_documents"]
    sorted_data = sorted(data, key=lambda x: x["report_date"])
    df = build_display_dataframe(selected_table, sorted_data)
    st.dataframe(df, hide_index=True, width="stretch")


def convert_legal_to_dataframe(data_dict):
    """Chuyển đổi legal documents thành DataFrame"""
    rows = []

    for key, value in data_dict.items():
        vn_name = DICTIONARY_MAPPING.get(key, key)

        if isinstance(value, list):
            value_str = "\n".join([f"• {item}" for item in value])
        elif isinstance(value, dict):
            continue
        else:
            value_str = str(value)

        rows.append({"Chỉ tiêu": vn_name, "Giá trị": value_str})

    return pd.DataFrame(rows)


def convert_financial_to_dataframe(fields_list):
    """Chuyển đổi financial documents thành DataFrame từ fields"""
    rows = []

    for field in fields_list:
        description = field.get("description") or DICTIONARY_MAPPING.get(
            field.get("name"), field.get("name", "-")
        )
        value = field.get("value", "-")

        rows.append({"Chỉ tiêu": description, "Giá trị": value})

    return pd.DataFrame(rows)


def render_extracted_data():
    data = st.session_state.data["base_information"]

    tab1, tab2 = st.tabs(["Giấy chứng nhận đăng ký kinh doanh", "Báo cáo Tài chính"])
    with tab1:
        st.subheader("Giấy chứng nhận đăng ký kinh doanh")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Thông tin Doanh nghiệp")
            df_business = convert_legal_to_dataframe(
                data["legal_documents"]["business_registration_cert"]["business_info"]
            )
            st.dataframe(
                df_business, use_container_width=True, hide_index=True, height=400
            )

        with col2:
            st.markdown("#### Thông tin Người đại diện pháp luật")
            df_legal = convert_legal_to_dataframe(
                data["legal_documents"]["business_registration_cert"]["legal_rep_info"]
            )
            st.dataframe(
                df_legal, use_container_width=True, hide_index=True, height=400
            )

        st.divider()
        st.subheader("Điều lệ công ty")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Thông tin Doanh nghiệp")
            df_charter_business = convert_legal_to_dataframe(
                data["legal_documents"]["company_charter"]["business_info"]
            )
            st.dataframe(
                df_charter_business,
                use_container_width=True,
                hide_index=True,
                height=400,
            )

        with col2:
            st.markdown("#### Thông tin Người đại diện pháp luật")
            df_charter_legal = convert_legal_to_dataframe(
                data["legal_documents"]["company_charter"]["legal_rep_info"]
            )
            st.dataframe(
                df_charter_legal, use_container_width=True, hide_index=True, height=400
            )
    with tab2:
        st.header("Báo cáo Tài chính")

        financial_docs = data.get("financial_documents", [])
        if financial_docs:
            for company_data in financial_docs:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Công ty", company_data["company"].upper())
                with col2:
                    st.metric("Ngày báo cáo", company_data["report_date"])

                reports = company_data.get("reports", [])

                if reports:
                    for idx, report in enumerate(reports):
                        st.subheader(
                            f"{report.get('description', report.get('report_name', ''))}"
                        )

                        # Lấy fields và chuyển thành DataFrame
                        fields = report.get("fields", [])

                        if fields:
                            df_financial = convert_financial_to_dataframe(fields)

                            st.dataframe(
                                df_financial,
                                use_container_width=True,
                                hide_index=True,
                                height=600,
                            )
                        else:
                            st.warning("Không có dữ liệu trong báo cáo này")
                else:
                    st.warning("Không có báo cáo nào")
        else:
            st.warning("Không có dữ liệu tài chính")


selected_key = [k for k, v in MAPPING.items() if v == selected_label][0]
if selected_key == "extracted_data":
    render_extracted_data()
else:
    render_common_statistics(selected_key)
