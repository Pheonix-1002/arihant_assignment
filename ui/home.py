"""Landing page."""

import streamlit as st


def render():
    st.title("AI Trading Suite")
    st.subheader("Three AI product prototypes - deterministic core")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### Project 1")
        st.markdown("**AI Options Trading Assistant**")
        st.caption("Chain - View-to-Strategy - Fit Score - Risk Analyzer")
    with c2:
        st.markdown("### Project 2")
        st.markdown("**AI Investment Assistant**")
        st.caption("XIRR - allocation - overlap - Health Score")
    with c3:
        st.markdown("### Project 3")
        st.markdown("**AI Chart Intelligence**")
        st.caption("Indicators - patterns - trend - confluence engine")

    st.divider()
    st.markdown("## How to use")
    st.markdown(
        "1. Use the **sidebar** to navigate between the three projects.\n"
        "2. Interactive inputs everywhere - market view, risk appetite, "
        "symbols, indicator overlays.\n"
        "3. All numbers are computed by deterministic engines "
        "(Black-Scholes, XIRR, indicator math).\n"
        "4. The **AI Lens** shows narrative plus source and confidence."
    )
    st.divider()
    st.info(
        "Deterministic engines run fully offline. When a Gemini API "
        "key is configured (via .streamlit/secrets.toml), the AI Lens "
        "calls the Gemini REST endpoint for narrative prose."
    )
