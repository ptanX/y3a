import streamlit as st
from PIL import Image
from dotenv import load_dotenv

from frontend.constants import LOGO_ICO_PATH
from menu import menu_with_redirect

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


if __name__ == "__main__":
    logo_image = Image.open(LOGO_ICO_PATH)
    st.set_page_config(page_title="RawIQ App", page_icon=logo_image)
    initialize_session_state()
    menu_with_redirect()
