"""Project 3 UI."""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from project3_charts import data, indicators, trend, patterns, confluence
from shared.narrative import NarrativeEngine


@st.cache_data(ttl=600, show_spinner="Loading OHLCV data...")
def load_data(symbol: str, period: str):
    return data.fetch(symbol=symbol, period=period)


def render():
    st.title("Project 3 - AI Chart Intelligence")

    with st.sidebar:
        st.subheader("Chart settings")
        symbol = st.text_input("Symbol", value="RELIANCE.NS",
                               help="e.g. RELIANCE.NS, TCS.NS")
        period = st.selectbox("Period", ["1y", "2y", "6mo"], index=0)
        show_ma = st.checkbox("Moving averages", value=True)
        show_bb = st.checkbox("Bollinger Bands", value=False)
        show_st = st.checkbox("Supertrend", value=False)
        show_vwap = st.checkbox("VWAP", value=False)

    try:
        df = load_data(symbol, period)
    except Exception as e:
        st.error(f"Could not load {symbol}: {e}")
        return
    if df is None or len(df) < 30:
        st.error("Insufficient data.")
        return

    src = df.attrs.get("source", "unknown")
    df = indicators.compute_all(df)
    t = trend.classify(df)
    c = confluence.evaluate(df)
    pr = patterns.support_resistance(df)
    cs = patterns.candlesticks(df)
    last = df.iloc[-1]
    st.caption(f"Data source: {src}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Close", f"{last['close']:.2f}")
    c2.metric("Trend", t[0], f"{t[1]} strength")
    c3.metric("Confluence", f"{c['agreement']}/5", c["bias"])
    c4.metric("RSI", f"{last['rsi']:.1f}")

    st.subheader("Price chart")
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=("Price", "Volume", "RSI"))
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["open"], high=df["high"],
        low=df["low"], close=df["close"], name="Price"),
        row=1, col=1)
    if show_ma:
        for n, color in [(20, "orange"), (50, "blue"), (200, "purple")]:
            fig.add_trace(go.Scatter(
                x=df.index, y=df[f"sma{n}"], name=f"SMA{n}",
                line=dict(color=color, width=1)), row=1, col=1)
    if show_bb:
        fig.add_trace(go.Scatter(x=df.index, y=df["bb_upper"],
                                 name="BB upper",
                                 line=dict(color="rgba(150,150,150,0.6)")),
                      row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["bb_lower"],
                                 name="BB lower",
                                 line=dict(color="rgba(150,150,150,0.6)")),
                      row=1, col=1)
    if show_st:
        fig.add_trace(go.Scatter(x=df.index, y=df["supertrend"],
                                 name="Supertrend",
                                 line=dict(color="green", width=1.5)),
                      row=1, col=1)
    if show_vwap:
        fig.add_trace(go.Scatter(x=df.index, y=df["vwap"], name="VWAP",
                                 line=dict(color="darkorange", dash="dot")),
                      row=1, col=1)
    if pr["support"]:
        fig.add_hline(y=pr["support"], line_dash="dash", line_color="green",
                      annotation_text=f"Support {pr['support']}",
                      row=1, col=1)
    if pr["resistance"]:
        fig.add_hline(y=pr["resistance"], line_dash="dash",
                      line_color="red",
                      annotation_text=f"Resistance {pr['resistance']}",
                      row=1, col=1)
    colors = ["green" if c_ >= o_ else "red"
              for o_, c_ in zip(df["open"], df["close"])]
    fig.add_trace(go.Bar(x=df.index, y=df["volume"], name="Volume",
                         marker_color=colors, showlegend=False),
                  row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["rsi"], name="RSI",
                             line=dict(color="purple", width=1.5)),
                  row=3, col=1)
    fig.add_hline(y=70, line_dash="dot", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="green", row=3, col=1)
    fig.update_layout(height=760, xaxis_rangeslider_visible=False,
                      margin=dict(l=20, r=20, t=40, b=20),
                      legend=dict(orientation="h", y=1.06, x=0))
    fig.update_yaxes(range=[0, 100], row=3, col=1)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Confluence engine")
    col1, col2 = st.columns(2)
    with col1:
        g = c["groups"]
        vals = [1 if v > 0 else -1 if v < 0 else 0 for v in g.values()]
        colors = ["seagreen" if v > 0 else "firebrick" if v < 0 else "gray"
                  for v in vals]
        texts = ["+" if v > 0 else "-" if v < 0 else "0" for v in vals]
        fig = go.Figure(go.Bar(x=list(g.keys()), y=vals,
                               marker_color=colors,
                               text=texts, textposition="auto"))
        fig.update_layout(
            title=f"Bias: {c['bias']} ({c['strength']})",
            yaxis=dict(tickmode="array", tickvals=[-1, 0, 1],
                       ticktext=["Bearish", "Neutral", "Bullish"]),
            yaxis_range=[-1.4, 1.4], height=300,
            margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("**Indicator snapshot**")
        st.markdown(f"- **RSI(14):** {last['rsi']:.1f}")
        st.markdown(f"- **MACD hist:** {last['macd_hist']:+.3f}")
        st.markdown(f"- **ADX:** {last['adx']:.1f}")
        st.markdown(f"- **Supertrend:** "
                    f"{'up' if last['st_dir'] == 1 else 'down'}")
        vol_ratio = (last["volume"]
                     / df["volume"].rolling(20).mean().iloc[-1])
        st.markdown(f"- **Volume vs 20d:** {vol_ratio:.2f}x")
        if pr["support"]:
            st.markdown(f"- **Support:** {pr['support']}")
        if pr["resistance"]:
            st.markdown(f"- **Resistance:** {pr['resistance']}")

    if cs:
        st.subheader("Candlestick patterns (last 5 bars)")
        st.table([{"Pattern": p[0],
                   "Bar": str(df.index[p[1]].date()),
                   "Meaning": p[2]} for p in cs])
    else:
        st.caption("No candlestick patterns detected.")

    st.subheader("AI Lens")
    ne = NarrativeEngine(use_llm=True)
    narrative = ne.synthesize(
        "Bias is {bias} ({strength}). Trend groups aligned: "
        "{agree} of 5. Key resistance: {res}. Support: {sup}. "
        "Invalidation: close below {sup}.",
        {
            "bias": c["bias"], "strength": c["strength"],
            "agree": c["agreement"], "res": pr["resistance"],
            "sup": pr["support"], "confidence": c["strength"],
        })
    st.info(narrative["text"])
    st.caption(f"Source: {narrative['source']}")
