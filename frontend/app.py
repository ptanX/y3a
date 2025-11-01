import streamlit as st
from dotenv import load_dotenv

from menu import menu

load_dotenv()

if __name__ == "__main__":
    # Page configuration
    st.set_page_config(page_title="Multi-Page App", layout="wide")

    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'role' not in st.session_state:
        st.session_state.role = ""
    if 'full_name' not in st.session_state:
        st.session_state.full_name = ""
    if 'uploaded_data' not in st.session_state:
        st.session_state.uploaded_data = []
    if 'document_id' not in st.session_state:
        st.session_state.document_id = None

    menu()
