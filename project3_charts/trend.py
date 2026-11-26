"""Symmetric trend classifier."""


def classify(df):
    last = df.iloc[-1]
    bull = sum([
        bool(last["close"] > last["sma20"]),
        bool(last["sma20"] > last["sma50"]),
        bool(last["sma50"] > last["sma200"]),
        bool(last["st_dir"] == 1),
        bool(last["adx"] > 25 and last["+di"] > last["-di"]),
    ])
    bear = sum([
        bool(last["close"] < last["sma20"]),
        bool(last["sma20"] < last["sma50"]),
        bool(last["sma50"] < last["sma200"]),
        bool(last["st_dir"] == -1),
        bool(last["adx"] > 25 and last["-di"] > last["+di"]),
    ])
    net = bull - bear
    if net >= 4:
        return "Bullish", "high"
    if net >= 2:
        return "Bullish", "medium"
    if net <= -4:
        return "Bearish", "high"
    if net <= -2:
        return "Bearish", "medium"
    return "Sideways", "low"
