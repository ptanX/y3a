import json

import requests
import streamlit as st
from PIL import Image

from frontend.constants import LOGO_ICO_PATH
from frontend.menu import menu_with_redirect
from frontend.utils import build_logo_before_title_html
from src.exceptions import EntityNotFound
from src.lending.services.db_service import query_document_information_by_id

menu_with_redirect()
logo_image = Image.open(LOGO_ICO_PATH)

st.set_page_config(page_title="Lending Chat Agent", page_icon=logo_image)
st.markdown(
    build_logo_before_title_html("Lending Chat Agent"),
    unsafe_allow_html=True,
)
st.divider()

document_id = st.session_state.document_id
if not document_id:
    st.write("Không tìm thấy mã tài liệu")
    st.stop()

st.query_params.document_id = document_id

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
        document_entity = query_document_information_by_id(document_id)
        if not document_entity:
            st.write(f"Không tìm thấy tài liệu với mã {document_id}")

        documents = json.loads(document_entity)["base_information"][
            "financial_documents"
        ]
        content = {
            "question": question,
            "document_id": document_id,
            "documents": documents,
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
