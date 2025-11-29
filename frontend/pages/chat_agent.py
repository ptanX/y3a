import json

import requests
import streamlit as st
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from frontend.constants import LOGO_ICO_PATH
from frontend.menu import menu_with_redirect
from frontend.utils import build_logo_before_title_html
from src.exceptions import EntityNotFound
from src.lending.db.bidv_entity import DocumentationInformation
from src.lending.startup.environment_initialization import DATABASE_PATH

menu_with_redirect()
logo_image = Image.open(LOGO_ICO_PATH)

st.set_page_config(page_title="Lending Chat Agent", page_icon=logo_image)
st.markdown(
    build_logo_before_title_html("Lending Chat Agent"),
    unsafe_allow_html=True,
)
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


def submit_stream(question):
    try:
        engine = create_engine(f"sqlite:///{DATABASE_PATH}")
        session = sessionmaker(bind=engine)()
        entity = session.get(DocumentationInformation, financial_document_id)

        if not entity:
            yield "Không tìm thấy tài liệu với mã {}".format(financial_document_id)
            return

        content = {
            "question": question,
            "document_id": financial_document_id,
            "documents": json.loads(entity.data),
        }

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

        with requests.post(url, headers=headers, json=message, stream=True, timeout=300) as response:
            for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                if chunk:
                    yield chunk
    except EntityNotFound as e:
        yield str(e)
    except Exception as e:
        print(e)
        yield "Error: Could not submit message. Please check your setup."


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
        try:
            response_placeholder = st.empty()
            full_response = ""
            
            for chunk in submit_stream(prompt):
                full_response += chunk
                response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )
        except Exception as e:
            st.error(f"❌ Error processing documents: {e}")

    st.session_state.chat_input_disabled = False
    st.rerun()
