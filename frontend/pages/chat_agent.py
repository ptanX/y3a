import streamlit as st

from frontend.menu import menu_with_redirect

menu_with_redirect()

st.set_page_config(page_title="Lending Chat Agent")
st.title("Lending Chat Agent")
