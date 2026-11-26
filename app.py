"""Streamlit entry point. Run: python -m streamlit run app.py"""

import streamlit as st

st.set_page_config(
    page_title="AI Trading Suite",
    page_icon="\U0001F4C8",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui import home, project1, project2, project3

PAGES = {
    "Home": home,
    "Project 1 - Options Assistant": project1,
    "Project 2 - Portfolio Assistant": project2,
    "Project 3 - Chart Intelligence": project3,
}

with st.sidebar:
    st.title("AI Trading Suite")
    st.caption("Deepanshu Sharma - IIT Guwahati")
    st.divider()
    page = st.radio("Navigate", list(PAGES.keys()),
                    label_visibility="collapsed")
    st.divider()
    st.caption(
        "Deterministic engines compute every number. Narratives use "
        "Gemini via REST when a key is configured, template otherwise."
    )

PAGES[page].render()
