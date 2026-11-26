"""5-group confluence with same-direction agreement."""


def _sign(x):
    return (x > 0) - (x < 0)


def evaluate(df):
    last = df.iloc[-1]
    groups = {}
    t = 0
    if last["close"] > last["sma50"]:
        t += 1
    if last["st_dir"] == 1:
        t += 1
    if last["adx"] > 25:
        t += 1
    groups["trend"] = 1 if t >= 2 else (-1 if t == 0 else 0)
    m = 0
    if last["rsi"] > 50:
        m += 1
    if last["macd_hist"] > 0:
        m += 1
    groups["momentum"] = 1 if m == 2 else (-1 if m == 0 else 0)
    p = 0
    vol_avg = df["volume"].rolling(20).mean().iloc[-1]
    if last["volume"] > vol_avg:
        p += 1
    if last["close"] > last["vwap"]:
        p += 1
    groups["participation"] = 1 if p == 2 else (-1 if p == 0 else 0)
    width = max(last["bb_upper"] - last["bb_lower"], 1e-6)
    b = (last["close"] - last["bb_lower"]) / width
    groups["location"] = 1 if b > 0.6 else (-1 if b < 0.4 else 0)
    bw = (df["bb_upper"] - df["bb_lower"]) / df["bb_mid"]
    bw_avg = bw.rolling(20).mean().iloc[-1]
    if bw.iloc[-1] > bw_avg:
        groups["volatility"] = 1 if last["close"] > last["bb_mid"] else -1
    else:
        groups["volatility"] = 0
    direction = sum(groups.values())
    sign = _sign(direction)
    agreement = sum(1 for v in groups.values()
                    if sign != 0 and v == sign)
    bias = ("Bullish" if direction > 1
            else "Bearish" if direction < -1 else "Mixed")
    strength = ("high" if agreement >= 4
                else "medium" if agreement >= 3 else "low")
    return {
        "bias": bias, "strength": strength, "agreement": agreement,
        "groups": groups,
        "conflicts": [k for k, v in groups.items()
                      if sign != 0 and v == -sign],
    }
