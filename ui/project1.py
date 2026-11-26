"""Project 1 UI."""

import streamlit as st
import plotly.graph_objects as go

from project1_options import data, chain_analyzer, finder, risk
from shared.narrative import NarrativeEngine


@st.cache_data(show_spinner=False)
def get_chain():
    return data.build_chain()


def render():
    st.title("Project 1 - AI Options Trading Assistant")
    chain = get_chain()
    analysis = chain_analyzer.analyze(chain)

    with st.sidebar:
        st.subheader("Your view")
        direction = st.selectbox(
            "Direction", ["bullish", "bearish", "neutral", "volatile"])
        risk_app = st.selectbox(
            "Risk appetite",
            ["conservative", "balanced", "aggressive"], index=1)
        max_loss = st.number_input(
            "Max loss budget (Rs)",
            min_value=1000, max_value=100000, value=10000, step=1000)
        defined_only = st.checkbox("Defined-risk only", value=True)

    view = {"direction": direction, "risk": risk_app,
            "defined_only": defined_only, "max_loss": int(max_loss)}

    st.subheader("Market Regime")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Spot", f"{analysis['spot']:.0f}")
    c2.metric("ATM IV", f"{analysis['atm_iv']:.1f}%",
              f"{analysis['iv_percentile']:.0f}th pctile")
    c3.metric("PCR", f"{analysis['pcr']:.2f}",
              f"z = {analysis['pcr_z']:.2f}")
    c4.metric("Regime", analysis["regime"])
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Call wall", f"{analysis['call_wall']}")
    c2.metric("Put wall", f"{analysis['put_wall']}")
    c3.metric("Max pain", f"{analysis['max_pain']}")
    c4.metric("Lean", analysis["lean"], analysis["strength"])
    st.caption(
        f"Expected move (1s): {analysis['band_1s']}   "
        f"(2s): {analysis['band_2s']}   "
        f"Votes: {analysis['votes']}")

    st.subheader("Open Interest by Strike")
    strikes = [r["strike"] for r in chain["rows"]]
    call_oi = [r["call_oi"] for r in chain["rows"]]
    put_oi = [r["put_oi"] for r in chain["rows"]]
    fig = go.Figure()
    fig.add_bar(x=strikes, y=call_oi, name="Call OI",
                marker_color="firebrick", opacity=0.75)
    fig.add_bar(x=strikes, y=[-p for p in put_oi], name="Put OI",
                marker_color="seagreen", opacity=0.75)
    fig.add_vline(x=analysis["spot"], line_dash="dash",
                  line_color="black", annotation_text="Spot")
    fig.update_layout(height=340, barmode="relative",
                      margin=dict(l=20, r=20, t=20, b=20),
                      legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Raw option chain (X-Ray view)"):
        rows = [{
            "Call OI": r["call_oi"], "Call DOI": r["call_doi"],
            "Call IV": r["call_iv"], "Call LTP": r["call_ltp"],
            "Strike": r["strike"], "Put LTP": r["put_ltp"],
            "Put IV": r["put_iv"], "Put DOI": r["put_doi"],
            "Put OI": r["put_oi"],
        } for r in chain["rows"]]
        st.dataframe(rows, use_container_width=True,
                     hide_index=True, height=300)

    st.subheader("View-to-Strategy Finder")
    results = finder.find(view, chain, top_n=3)
    if not results:
        st.warning("No strategies match. Try relaxing constraints.")
        return

    for i, r in enumerate(results, 1):
        with st.container(border=True):
            cols = st.columns([3, 1])
            with cols[0]:
                legs = " / ".join(
                    f"{'+' if d > 0 else '-'} {k.upper()} {strike} "
                    f"({'Buy' if d > 0 else 'Sell'})"
                    for k, d, strike in r["legs"])
                st.markdown(f"### #{i} {r['name']}")
                st.caption(legs)
            with cols[1]:
                st.metric("Fit", f"{r['fit']['total']:.0f}")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Net premium", f"{r['net_premium']:+.0f}")
            c2.metric("Max profit", r["risk"]["max_profit_label"])
            c3.metric("Max loss", r["risk"]["max_loss_label"])
            c4.metric("POP (model)",
                      f"{r['risk']['pop_model'] * 100:.0f}%")
            with st.expander("Fit Score breakdown"):
                st.json(r["fit"]["breakdown"])

    top = results[0]
    st.subheader(f"Risk Analyzer - {top['name']}")
    S = top["risk"]["spot_range"]
    pnl = top["risk"]["pnl"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=S, y=pnl, mode="lines", name="P&L",
        line=dict(color="steelblue", width=3)))
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    fig.add_vline(x=analysis["spot"], line_dash="dot",
                  line_color="black", annotation_text="Spot")
    fig.update_layout(title="Payoff at expiry (per unit)",
                      height=340, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### What-if scenario grid (per unit)")
    grid = risk.scenario_grid(top["strategy"], chain)
    z = [row for _, row in grid]
    y = [f"{ss * 100:+.0f}% spot" for ss, _ in grid]
    x = ["IV -5", "IV 0", "IV +5"]
    fig = go.Figure(data=go.Heatmap(
        z=z, x=x, y=y, colorscale="RdYlGn",
        text=z, texttemplate="%{text}"))
    fig.update_layout(height=260, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("AI Lens")
    ne = NarrativeEngine(use_llm=True)
    narrative = ne.regime_summary({
        "lean": analysis["lean"],
        "strength": analysis["strength"],
        "iv_percentile": int(analysis["iv_percentile"]),
        "confidence": analysis["confidence"],
        "flip": (f"a close beyond {analysis['call_wall']} "
                 f"or {analysis['put_wall']}"),
    })
    st.info(narrative["text"])
    st.caption(
        f"Source: {narrative['source']} - "
        f"Confidence: {narrative['confidence']}")
