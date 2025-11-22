from pathlib import Path

import streamlit as st
from PIL import Image
from dotenv import load_dotenv

from menu import menu

load_dotenv()


def initialize_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "role" not in st.session_state:
        st.session_state.role = ""
    if "full_name" not in st.session_state:
        st.session_state.full_name = ""
    if "uploaded_data" not in st.session_state:
        st.session_state.uploaded_data = []
    if "document_id" not in st.session_state:
        st.session_state.document_id = None
    if "financial_document_id" not in st.session_state:
        st.session_state.financial_document_id = None


if __name__ == "__main__":
    # Page configuration
    logo_path = Path(__file__).parent.absolute().joinpath("images").joinpath("logo.jpg")
    logo_image = Image.open(logo_path)

    st.set_page_config(page_title="RawIQ App", page_icon=logo_image, layout="wide")

    initialize_session_state()
    menu()
