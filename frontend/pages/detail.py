import streamlit as st

from frontend.menu import menu_with_redirect, has_permission, get_role_badge

menu_with_redirect()

st.set_page_config(page_title="Detail Customer")
st.title("Detail Customer")

st.write("## Detail Customer")
document_id = st.session_state.document_id
if st.session_state.document_id:
    st.write(st.session_state.document_id)

    st.query_params.document_id = document_id

# Get selected record
# selected_id = st.session_state.get('selected_detail_id', 1)
# if selected_id is None:
#     st.warning("No record selected")
#     if st.button("← Back to Details"):
#         st.switch_page("pages/detail.py")
#     st.stop()
#
# record = next((r for r in st.session_state.uploaded_data if r['id'] == selected_id), None)
# if record is None:
#     st.error("Record not found")
#     if st.button("← Back to Details"):
#         st.switch_page("pages/detail.py")
#     st.stop()
#
# # DETAIL CUSTOMER PAGE
# st.title(f"📄 Customer Detail - ID: {record['id']}")
#
# if st.button("← Back to Details"):
#     st.switch_page("pages/detail.py")
#
# st.divider()
#
# # Customer Information Form

with st.form("detail_form"):
    st.markdown("### Thông tin QHTD")

    recipient_name = st.text_input("Name QHTD")
    recipient_email = st.text_input("Email QHTD")

    st.divider()
    st.markdown("### Kết quả bóc tách chi tiết")

    # Sample data table
    import pandas as pd

    # Create sample comparison table
    data = {
        'STT': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        'Chỉ tiêu': [
            'Tên công ty (VN)',
            'Tên công ty (EN)',
            'Tên viết tắt',
            'Địa chỉ trụ sở',
            'Số điện thoại',
            'Vốn điều lệ',
            'Người đại diện pháp luật',
            'Email công ty',
            'Ngành nghề chính',
            'Mã số thuế',
            'Mã số doanh nghiệp/Mã số doanh nghiệp',
            ""
        ],
        'Giấy phép ĐKLD': [
            'CÔNG TY CỔ PHẦN CHỨNG KHOÁN DNSE',
            '',
            'DNSE JSC',
            '',
            'Nhầm, Hà Ba Trưng',
            '2-D1-089-234',
            '3.500.000.000.000',
            '',
            'info@dnse.com.vn',
            '10.000 đồng',
            '',
            '102459106'
        ],
        'Điều lệ': [
            'Công ty Cổ phần Chứng khoán DNSE',
            'DNSE Securities Joint Stock Company',
            'DNSE JSC',
            'Tầng 1, Tầng 3, Tòa Nhà Licogi Tòa',
            'Tầng 6, Tòa Aho, Hải Ba Trưng',
            '024 7108 9234',
            '3.500.000.000.000',
            '',
            'info@dnse.com.vn',
            '10.000 đồng',
            '',
            '102459106'
        ],
        'CSDL nội bộ (DB)': [
            'Công Ty Cổ Phần Chứng Khoản DNSE',
            'DNSE SECURITIES JOINT STOCK COMPANY',
            'DNSE JSC',
            '',
            'Tầng 6, Tác Anh, Hai Ba Trưng',
            '024 7108 9234',
            '3.500.000.000.000',
            '',
            'info@dnse.com.vn',
            '10',
            '5.000.000.000',
            '102459106'
        ],
        'Ý kiến QTHTD': [
            'CÔNG TY CỔ PHẦN CHỨNG KHOÁN DNSE',
            'DNSE Securities Joint Stock Company',
            'DNSE JSC',
            '',
            'Tầng',
            '2-D1-089-234',
            '3.500.000.000.000',
            '',
            'info@dnse.com.vn',
            '10.000 đồng',
            '',
            '102459106'
        ]
    }

    df = pd.DataFrame(data)

    # Display table with highlighting
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=400
    )

    st.info("💡 Các ô màu vàng: Trạng thái cần tra khảo bức tích đượç")
    st.warning("💡 Các ô màu hồng: Trạng thái tin cần kiểm tra")

    # Submit button
    submitted = st.form_submit_button("Submit", use_container_width=True, type="primary")

    if submitted:
        st.success("✅ Data submitted successfully!")
        st.balloons()
