import pandas as pd
import streamlit as st

from frontend.menu import menu_with_redirect

menu_with_redirect()

# Streamlit App
st.set_page_config(page_title="Bảng Kiểm Tra Dữ Liệu", layout="wide")
st.title("📊 Bảng Kiểm Tra Dữ Liệu Công Ty")

document_id = st.session_state.document_id
if st.session_state.document_id:
    st.query_params.document_id = document_id

# Sample data
data = [
    {
        "field_name": "company_name_vn",
        "origin_docs": [
            {
                "name": "business_registration_cert",
                "value": "CÔNG TY CỔ PHẦN CHỨNG KHOÁN DNSE"
            },
            {
                "name": "company_charter",
                "value": "Công ty Cổ phần Chứng khoán DNSE"
            }
        ],
        "database_value": "Công ty Cổ phần Chứng khoán DNSE",
        "validation_result": {
            "is_consistent_across_doc": False,
            "is_match_database": True
        }
    },
    {
        "field_name": "company_name_en",
        "origin_docs": [
            {
                "name": "business_registration_cert",
                "value": "DNSE SECURITIES JOINT STOCK COMPANY"
            },
            {
                "name": "company_charter",
                "value": "DNSE Securities Joint Stock Company"
            }
        ],
        "database_value": "DNSE SECURITIES JOINT STOCK COMPANY",
        "validation_result": {
            "is_consistent_across_doc": False,
            "is_match_database": True
        }
    },
    {
        "field_name": "company_abbr",
        "origin_docs": [
            {
                "name": "business_registration_cert",
                "value": "DNSE JSC"
            },
            {
                "name": "company_charter",
                "value": "DNSE Jsc"
            }
        ],
        "database_value": "DNSE JSC",
        "validation_result": {
            "is_consistent_across_doc": False,
            "is_match_database": True
        }
    },
    {
        "field_name": "office_address",
        "origin_docs": [
            {
                "name": "company_charter",
                "value": "Tầng 6, Tòa nhà Pax Sky, số 63-65 Ngô Thì Nhậm, Phường Phạm Đình Hổ, Quận Hai Bà Trưng, Thành phố Hà Nội"
            }
        ],
        "database_value": "Tầng 6 tòa nhà Pax Sky, 63-65 Ngô Thì Nhậm, Phường Phạm Đình Hổ, Quận Hai Bà Trưng, Thành phố Hà Nội, Việt Nam",
        "validation_result": {
            "is_consistent_across_doc": True,
            "is_match_database": False
        }
    },
    {
        "field_name": "phone",
        "origin_docs": [
            {
                "name": "business_registration_cert",
                "value": "024.7108.9234"
            },
            {
                "name": "company_charter",
                "value": "(84-24) 710 89234"
            }
        ],
        "database_value": "024 7108 9234",
        "validation_result": {
            "is_consistent_across_doc": False,
            "is_match_database": False
        }
    },
    {
        "field_name": "email",
        "origin_docs": [
            {
                "name": "business_registration_cert",
                "value": "info@dnse.com.vn"
            },
            {
                "name": "company_charter",
                "value": "info@dnse.com.vn"
            }
        ],
        "database_value": "info@dnse.com.vn",
        "validation_result": {
            "is_consistent_across_doc": True,
            "is_match_database": True
        }
    },
    {
        "field_name": "charter_capital",
        "origin_docs": [
            {
                "name": "business_registration_cert",
                "value": "3.300.000.000.000 đồng"
            },
            {
                "name": "company_charter",
                "value": "3.300.000.000.000 đồng (Ba nghìn ba trăm tỷ đồng)"
            }
        ],
        "database_value": "3,300,000,000,000",
        "validation_result": {
            "is_consistent_across_doc": False,
            "is_match_database": False
        }
    },
    {
        "field_name": "par_value",
        "origin_docs": [
            {
                "name": "business_registration_cert",
                "value": "10.000 đồng"
            },
            {
                "name": "company_charter",
                "value": "10.000 đồng/cổ phần"
            }
        ],
        "database_value": "10,000",
        "validation_result": {
            "is_consistent_across_doc": False,
            "is_match_database": False
        }
    },
    {
        "field_name": "total_shares",
        "origin_docs": [
            {
                "name": "business_registration_cert",
                "value": "330.000.000"
            }
        ],
        "database_value": "330,000,000",
        "validation_result": {
            "is_consistent_across_doc": True,
            "is_match_database": False
        }
    },
    {
        "field_name": "business_code",
        "origin_docs": [
            {
                "name": "business_registration_cert",
                "value": "0102459106"
            }
        ],
        "database_value": "0102459106",
        "validation_result": {
            "is_consistent_across_doc": True,
            "is_match_database": True
        }
    },
    {
        "field_name": "legal_rep",
        "origin_docs": [],
        "database_value": None,
        "validation_result": {
            "is_consistent_across_doc": True,
            "is_match_database": False
        }
    },
    {
        "field_name": "full_name",
        "origin_docs": [
            {
                "name": "business_registration_cert",
                "value": "PHẠM THỊ THANH HOA"
            }
        ],
        "database_value": None,
        "validation_result": {
            "is_consistent_across_doc": True,
            "is_match_database": False
        }
    },
    {
        "field_name": "gender",
        "origin_docs": [
            {
                "name": "business_registration_cert",
                "value": "Nữ"
            }
        ],
        "database_value": None,
        "validation_result": {
            "is_consistent_across_doc": True,
            "is_match_database": False
        }
    },
    {
        "field_name": "position",
        "origin_docs": [
            {
                "name": "business_registration_cert",
                "value": "Tổng giám đốc"
            },
            {
                "name": "company_charter",
                "value": "Tổng giám đốc Công ty"
            }
        ],
        "database_value": None,
        "validation_result": {
            "is_consistent_across_doc": False,
            "is_match_database": False
        }
    },
    {
        "field_name": "birth_date",
        "origin_docs": [
            {
                "name": "business_registration_cert",
                "value": "17/11/1985"
            }
        ],
        "database_value": None,
        "validation_result": {
            "is_consistent_across_doc": True,
            "is_match_database": False
        }
    },
    {
        "field_name": "ethnicity",
        "origin_docs": [
            {
                "name": "business_registration_cert",
                "value": "Kinh"
            }
        ],
        "database_value": None,
        "validation_result": {
            "is_consistent_across_doc": True,
            "is_match_database": False
        }
    },
    {
        "field_name": "nationality",
        "origin_docs": [
            {
                "name": "business_registration_cert",
                "value": "Việt Nam"
            }
        ],
        "database_value": None,
        "validation_result": {
            "is_consistent_across_doc": True,
            "is_match_database": False
        }
    },
    {
        "field_name": "id_type",
        "origin_docs": [
            {
                "name": "business_registration_cert",
                "value": "Thẻ căn cước công dân"
            }
        ],
        "database_value": None,
        "validation_result": {
            "is_consistent_across_doc": True,
            "is_match_database": False
        }
    },
    {
        "field_name": "id_number",
        "origin_docs": [],
        "database_value": None,
        "validation_result": {
            "is_consistent_across_doc": True,
            "is_match_database": False
        }
    },
    {
        "field_name": "issue_date",
        "origin_docs": [
            {
                "name": "business_registration_cert",
                "value": "19/11/2014"
            }
        ],
        "database_value": None,
        "validation_result": {
            "is_consistent_across_doc": True,
            "is_match_database": False
        }
    },
    {
        "field_name": "issue_place",
        "origin_docs": [
            {
                "name": "business_registration_cert",
                "value": "CỤC CẢNH SÁT DKQL CƯ TRÚ VÀ DLQG VỀ DÂN CƯ"
            }
        ],
        "database_value": None,
        "validation_result": {
            "is_consistent_across_doc": True,
            "is_match_database": False
        }
    },
    {
        "field_name": "expiry_date",
        "origin_docs": [],
        "database_value": None,
        "validation_result": {
            "is_consistent_across_doc": True,
            "is_match_database": False
        }
    },
    {
        "field_name": "permanent_address",
        "origin_docs": [],
        "database_value": None,
        "validation_result": {
            "is_consistent_across_doc": True,
            "is_match_database": False
        }
    },
    {
        "field_name": "contact_address",
        "origin_docs": [],
        "database_value": None,
        "validation_result": {
            "is_consistent_across_doc": True,
            "is_match_database": False
        }
    }
]

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
    "user_input": "Ý kiến QTTD"
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


# Callback function to handle changes


if "my_data" not in st.session_state:
    df = json_to_dataframe(data)
    st.session_state.my_data = df

with st.form("detail_form"):
    # def handle_data_change():
    #     st.write("Data in editor has changed!")
    #     # You can access the edited data and changes via st.session_state
    #     # For example, if your data editor has key="my_editor":
    #     # edited_rows = st.session_state.my_editor["edited_rows"]
    #     # inserted_rows = st.session_state.my_editor["inserted_rows"]
    #     # deleted_rows = st.session_state.my_editor["deleted_rows"]
    #     # Process these changes as needed (e.g., update a database)
    #     print(st.session_state.my_editor)


    st.markdown("### Thông tin QHTD")

    recipient_name = st.text_input("Name QHTD")
    recipient_email = st.text_input("Email QHTD")

    # Display the styled dataframe
    st.data_editor(
        st.session_state.my_data.style.apply(highlight_rows, axis=1),
        column_config=get_column_config(),
        use_container_width=True,
        key="my_editor",
        # on_change=handle_data_change,
        height=400
    )

    # Display legend
    st.markdown("### 📌 Chú thích:")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("🟨 Trường thông tin cần kiểm tra")
    with col2:
        st.markdown("🟥 Trường thông tin không bóc tách được")
    st.markdown("---")

    submitted = st.form_submit_button("Submit", use_container_width=True, type="primary")

    if submitted:
        print(dict(zip(st.session_state.my_data["field"], st.session_state.my_data["user_input"])))
        st.success("✅ Data submitted successfully!")
        st.balloons()
