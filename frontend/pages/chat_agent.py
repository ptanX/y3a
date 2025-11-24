import json
from pathlib import Path

import requests
import streamlit as st
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from frontend.menu import menu_with_redirect, display_logo
from frontend.utils import get_base64_image
from src.lending.db.bidv_entity import DocumentationInformation
from src.lending.startup.environment_initialization import DATABASE_PATH
from src.exceptions import EntityNotFound

menu_with_redirect()
logo_path = Path(__file__).parent.parent.joinpath("images").joinpath("logo.jpg").absolute()
logo_image = Image.open(logo_path)

st.set_page_config(page_title="Lending Chat Agent", page_icon=logo_image)
# st.title("Lending Chat Agent")
logo_base64 = get_base64_image(logo_path)
st.markdown(f"""
    <style>
    .logo-title-container {{
        display: flex;
        align-items: center;
        gap: 15px;
    }}
    .logo-title-container img {{
        width: 60px;
        height: auto;
    }}
    .logo-title-container h1 {{
        margin: 0;
        font-size: 2.5rem;
    }}
    </style>

    <div class="logo-title-container">
        <img src="data:image/jpeg;base64,{logo_base64}" alt="Logo">
        <h1>Lending Chat Agent</h1>
    </div>
""", unsafe_allow_html=True)
st.divider()

financial_document_id = st.session_state.financial_document_id
if not financial_document_id:
    st.write("Không tìm thấy mã tài liệu")
    st.stop()

st.query_params.financial_document_id = financial_document_id

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_input_disabled" not in st.session_state:
    st.session_state.chat_input_disabled = False

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def submit(question):
    try:
        engine = create_engine(f"sqlite:///{DATABASE_PATH}")
        session = sessionmaker(bind=engine)()
        entity = session.get(DocumentationInformation, financial_document_id)

        if not entity:
            st.write(f"Không tìm thấy tài liệu với mã {financial_document_id}")

        content = {
            "question": question,
            "document_id": financial_document_id,
            "documents": json.loads(entity.data),
        }

        # Prompt template
        message = {
            "inputs": {
                "messages": [
                    {
                        "role": "user",
                        "content": json.dumps(
                            content, ensure_ascii=False, separators=(",", ":")
                        ),
                    }
                ]
            }
        }
        url = "http://127.0.0.1:8080/invocations"
        headers = {"Content-Type": "application/json"}

        response = requests.request(
            "POST", url, headers=headers, data=json.dumps(message), timeout=300
        )
        return response.json().get("predictions").get("messages")[0].get("content")
        # return "Hello"
    except EntityNotFound as e:
        return str(e)
    except Exception as e:
        print(e)
        return "Error: Could not submit message. Please check your setup."


def disable_chat_input():
    st.session_state.chat_input_disabled = True


if prompt := st.chat_input(
    "How can I help you today?",
    disabled=st.session_state.chat_input_disabled,
    on_submit=disable_chat_input,
):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Đang tiến hành phân tích dữ liệu..."):
            try:
                response = submit(prompt)
                st.markdown(response, unsafe_allow_html=True)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )
            except Exception as e:
                st.error(f"❌ Error processing documents: {e}")

    st.session_state.chat_input_disabled = False
    st.rerun()
