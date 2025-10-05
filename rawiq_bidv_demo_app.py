import asyncio
import os

import streamlit as st

from src.bidv import full_flow


def process(uploaded_file):
    if not uploaded_file:
        st.error("No files uploaded!")
        return

    # Save the uploaded file to a temporary path
    temp_file_path = os.path.abspath(os.path.join("./temp", uploaded_file.name))
    os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)

    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(uploaded_file.getbuffer())

    asyncio.run(full_flow.execute(temp_file_path))


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

    if st.button("📚 Process Documents"):
        if not uploaded_file:
            st.warning("⚠️ Please upload PDF file first")
        else:
            with st.spinner("🔄 Processing document..."):
                try:
                    process(uploaded_file)
                    st.success(f"✅ Successfully processed {uploaded_file.name} document!")
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
