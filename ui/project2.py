"""Project 2 UI."""

import streamlit as st
import plotly.graph_objects as go

from project2_portfolio import analyzer, health_score, insights
from shared.narrative import NarrativeEngine


def render():
    st.title("Project 2 - AI Investment Assistant")
    a = analyzer.analyze()
    h = health_score.score(a)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total value", f"Rs {a['total']:,.0f}")
    c2.metric("Portfolio XIRR", f"{a['portfolio_xirr']:.2f}%", a["as_of"])
    c3.metric("HHI", f"{a['hhi']:.3f}")
    c4.metric("Health Score", f"{h['total']:.0f}/100", h["weakest"])

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Health Score breakdown")
        keys = list(h["breakdown"].keys())
        vals = list(h["breakdown"].values())
        colors = ["#2E75B6" if k != h["weakest"] else "#C0392B"
                  for k in keys]
        fig = go.Figure()
        fig.add_bar(x=keys, y=vals, marker_color=colors,
                    text=[f"{v:.0f}" for v in vals], textposition="auto")
        fig.update_layout(yaxis_range=[0, 100], height=340,
                          margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
        if h.get("placeholders"):
            st.caption("Placeholders: " + ", ".join(h["placeholders"]))
    with col2:
        st.subheader("Sector allocation")
        sectors = a["sectors"]
        fig = go.Figure(data=go.Pie(
            labels=list(sectors.keys()),
            values=list(sectors.values()), hole=0.4))
        fig.update_layout(height=340, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top holdings (direct vs look-through)")
    c1, c2 = st.columns(2)
    with c1:
        st.caption("Direct")
        st.table([{"Symbol": sym, "Weight": f"{w * 100:.1f}%",
                   "XIRR": f"{a['per_xirr'].get(sym, 0):.2f}%"}
                  for sym, w in a["top3"]])
    with c2:
        st.caption("Look-through")
        st.table([{"Symbol": sym, "Weight": f"{w * 100:.1f}%"}
                  for sym, w in (a.get("eff_top3") or [])])

    st.subheader("Insights")
    for card in insights.generate(a, h):
        with st.container(border=True):
            st.markdown(f"**{card['title']}** - priority {card['priority']}")
            st.caption(f"Why: {card['why']}")
            st.caption(f"Action: {card['action']}")

    st.subheader("AI Lens")
    ne = NarrativeEngine(use_llm=True)
    narrative = ne.synthesize(
        "Your portfolio totals {total} with XIRR of {xirr} percent. "
        "Health score is {health} out of 100. The weakest component "
        "is {weak} at {weakval}.",
        {
            "total": f"{a['total']:,.0f}",
            "xirr": a["portfolio_xirr"],
            "health": h["total"],
            "weak": h["weakest"],
            "weakval": h["breakdown"][h["weakest"]],
            "confidence": "medium",
        })
    st.info(narrative["text"])
    st.caption(f"Source: {narrative['source']}")
