import json
import os

import requests
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.bidv import full_flow
from src.bidv.db.bidv_entity import DocumentationInformation
from src.bidv.startup.environment_initialization import DATABASE_PATH
from src.exceptions import EntityNotFound


def process(uploaded_file, email_input):
    if not uploaded_file:
        st.error("No files uploaded!")
        return

    # Save the uploaded file to a temporary path
    temp_file_path = os.path.abspath(os.path.join("./temp", uploaded_file.name))
    os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)

    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(uploaded_file.getbuffer())

    full_flow.execute(temp_file_path, email_input)


def submit(question, document_id):
    try:
        engine = create_engine(f"sqlite:///{DATABASE_PATH}")
        session = sessionmaker(bind=engine)()
        entity = session.get(DocumentationInformation, document_id)

        if not entity:
            raise EntityNotFound(f"Not found Document with id=[{document_id}]")

        content = {
            "question": question,
            "document_id": document_id,
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


def main():
    st.set_page_config(
        page_title="Rawiq",
        page_icon="🧬",
        layout="wide"
    )

    st.header("🧬 Rawiq Insight Retrieval System")

    # Main query interface
    st.subheader("📄 Document Management")
    uploaded_file = st.file_uploader(
        "Upload PDFs:",
        type=["pdf"],
        accept_multiple_files=False,
        help="Add document to start analyzing."
    )

    col1, col2 = st.columns(2)

    with col1:
        email_input = st.text_input(
            "Email",
            placeholder="Email",
            label_visibility="collapsed"
        )

    with col2:
        process_button = st.button("📚 Process Documents")

    if process_button:
        if not uploaded_file:
            st.warning("⚠️ Please upload PDF file first")
        else:
            with st.spinner("🔄 Processing document..."):
                try:
                    process(uploaded_file, email_input)
                    st.success(
                        f"Đã tiếp nhận yêu cầu thành công. Vui lòng đợi kết quả gửi vào hòm mail {email_input}")
                except Exception as e:
                    st.error(f"❌ Error processing documents: {e}")

    query = st.text_area(
        "💡 Enter your  question:",
        placeholder="e.g., Tình hình tài chính của công ty cổ phần chứng khoán DNSE?",
        height=100
    )

    col3, col4 = st.columns(2)
    with col3:
        document_id = st.text_input("Document ID", placeholder="Mã tài liệu",
                                    label_visibility="collapsed")
    with col4:
        submit_button = st.button("🚀 Submit Query", type="primary")

    if submit_button:
        if not document_id:
            st.warning("⚠️ Hãy nhập vào mã tài liệu")
        else:
            with st.spinner("🔄 Analyze document..."):
                try:
                    result = submit(query, document_id)
                    st.success("✅ Response generated!")
                    st.markdown("### 📋 Answer:")
                    st.write(result)
                except Exception as e:
                    st.error(f"❌ Error processing documents: {e}")

    # Sidebar configuration
    with st.sidebar:
        st.title("Documentations")
        # Using object notation
        add_selectbox = st.sidebar.selectbox(
            "What would you like to be demonstrated?",
            ("Lending", "Chat Agent")
        )
        st.markdown("---")

    # Footer
    st.markdown("---")

    st.markdown(
        "<div style='text-align: center; color: #666; margin-top: 2rem;'>"
        "Built with ❤️ using AI"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
