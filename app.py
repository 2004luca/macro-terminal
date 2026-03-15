# app.py
# Entry point of the terminal.
# Defines the general layout and navigation between pages.

import streamlit as st

st.set_page_config(
    page_title="Macro Terminal",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Macro Terminal")
st.markdown("*Your personal Bloomberg — powered by Python*")
st.divider()
st.markdown("👈 Select a page from the sidebar to get started.")