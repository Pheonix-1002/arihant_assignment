"""Run: python -m project3_charts.cli"""

from shared.narrative import NarrativeEngine
from . import data, indicators, trend, patterns, confluence


def main():
    df = data.fetch()
    src = df.attrs.get("source", "unknown")
    df = indicators.compute_all(df)
    t = trend.classify(df)
    c = confluence.evaluate(df)
    pr = patterns.support_resistance(df)
    cs = patterns.candlesticks(df)
    last = df.iloc[-1]
    print("=" * 64)
    print(f"AI CHART SUMMARY - {df.index[-1].date()}")
    print(f"Data source: {src}")
    print("=" * 64)
    print(f"Close: {last['close']:.2f}   "
          f"Trend: {t[0]} ({t[1]} strength)")
    print(f"Confluence: {c['agreement']}/5   Bias: {c['bias']}")
    print(f"Groups: {c['groups']}")
    print(f"Support: {pr['support']}   Resistance: {pr['resistance']}")
    print(f"RSI: {last['rsi']:.1f}   "
          f"MACD hist: {last['macd_hist']:+.3f}   "
          f"ADX: {last['adx']:.1f}   "
          f"Supertrend: {'up' if last['st_dir'] == 1 else 'down'}")
    vol_ratio = last["volume"] / df["volume"].rolling(20).mean().iloc[-1]
    print(f"Volume vs 20d: {vol_ratio:.2f}x")
    print(f"Candlestick (last 5): {cs}")
    if c["conflicts"]:
        print(f"Conflicts: {', '.join(c['conflicts'])}")
    print()
    ne = NarrativeEngine(use_llm=True)
    narrative = ne.synthesize(
        "Bias is {bias} ({strength}). Trend groups aligned: "
        "{agree} of 5. Key resistance: {res}. Support: {sup}. "
        "Invalidation: close below {sup}.",
        {
            "bias": c["bias"], "strength": c["strength"],
            "agree": c["agreement"], "res": pr["resistance"],
            "sup": pr["support"], "confidence": c["strength"],
        },
    )
    print("AI LENS")
    print(f"  {narrative['text']}")
    print(f"  [source: {narrative['source']}]")


if __name__ == "__main__":
    main()
