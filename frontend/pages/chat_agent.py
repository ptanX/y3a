import json

import requests
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from frontend.menu import menu_with_redirect
from src.bidv.db.bidv_entity import DocumentationInformation
from src.bidv.startup.environment_initialization import DATABASE_PATH
from src.exceptions import EntityNotFound

menu_with_redirect()

st.set_page_config(page_title="👥 Lending Chat Agent")
st.title("Lending Chat Agent")

financial_document_id = st.session_state.financial_document_id
if not financial_document_id:
    st.write("Không tìm thấy mã tài liệu")
    st.stop()

st.query_params.financial_document_id = financial_document_id


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
                        "content": json.dumps(content, ensure_ascii=False, separators=(',', ':')),
                    }
                ]
            }
        }
        url = "http://127.0.0.1:8080/invocations"
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=json.dumps(message), timeout=300)
        return response.json().get("predictions").get("messages")[0].get("content")
    except EntityNotFound as e:
        return str(e)
    except Exception as e:
        print(e)
        return "Error: Could not submit message. Please check your setup."


query = st.text_area(
    "💡 Enter your  question:",
    placeholder="e.g., Tình hình tài chính của công ty cổ phần chứng khoán DNSE?",
    height=150
)

_, right_col = st.columns([9, 3])
with right_col:
    submit_button = st.button("🚀 Submit Query", type="primary", width="stretch")

if submit_button:
    with st.spinner("🔄 Analyze document..."):
        try:
            result = submit(query)
            st.success("✅ Response generated!")
            st.markdown("### 📋 Answer:")
            st.write(result)
        except Exception as e:
            st.error(f"❌ Error processing documents: {e}")
