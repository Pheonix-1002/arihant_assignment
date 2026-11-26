"""Candlestick and support/resistance patterns."""


def candlesticks(df):
    pats = []
    for i in range(-5, 0):
        o, h, l, c = (df["open"].iloc[i], df["high"].iloc[i],
                      df["low"].iloc[i], df["close"].iloc[i])
        body = abs(c - o)
        rng = max(h - l, 1e-6)
        upper = h - max(o, c)
        lower = min(o, c) - l
        if body / rng < 0.15:
            pats.append(("Doji", i, "indecision"))
        if lower > 2 * body and upper < body:
            pats.append(("Hammer", i, "possible bottom"))
        if upper > 2 * body and lower < body:
            pats.append(("Shooting Star", i, "possible top"))
    return pats


def support_resistance(df, window=10):
    highs = df["high"].rolling(window, center=True).max()
    lows = df["low"].rolling(window, center=True).min()
    res = [float(x) for x in df["high"][df["high"] == highs].tail(3)]
    sup = [float(x) for x in df["low"][df["low"] == lows].tail(3)]
    return {
        "resistance": round(max(res), 2) if res else None,
        "support": round(min(sup), 2) if sup else None,
    }
