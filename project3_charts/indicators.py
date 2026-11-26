"""Indicators (RSI, MACD, MAs, Bollinger, ATR, ADX, Supertrend, VWAP)."""

import numpy as np
import pandas as pd


def sma(s, n):
    return s.rolling(n).mean()


def ema(s, n):
    return s.ewm(span=n, adjust=False).mean()


def rsi(close, n=14):
    d = close.diff()
    up = d.clip(lower=0).rolling(n).mean()
    dn = (-d.clip(upper=0)).rolling(n).mean()
    rs = up / dn.replace(0, np.nan)
    return 100 - 100 / (1 + rs)


def macd(close, fast=12, slow=26, sig=9):
    line = ema(close, fast) - ema(close, slow)
    signal = ema(line, sig)
    return line, signal, line - signal


def bollinger(close, n=20, k=2):
    m = sma(close, n)
    sd = close.rolling(n).std()
    return m + k * sd, m, m - k * sd


def atr(df, n=14):
    h, l, c = df["high"], df["low"], df["close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(),
                    (l - c.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()


def vwap(df):
    tp = (df["high"] + df["low"] + df["close"]) / 3
    return (tp * df["volume"]).cumsum() / df["volume"].cumsum()


def adx(df, n=14):
    h, l = df["high"], df["low"]
    up = h.diff()
    dn = -l.diff()
    plus = np.where((up > dn) & (up > 0), up, 0.0)
    minus = np.where((dn > up) & (dn > 0), dn, 0.0)
    tr = atr(df, n)
    plus_di = 100 * pd.Series(plus, index=df.index).rolling(n).mean() / tr
    minus_di = 100 * pd.Series(minus, index=df.index).rolling(n).mean() / tr
    dx = (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan) * 100
    return dx.rolling(n).mean(), plus_di, minus_di


def supertrend(df, n=10, mult=3.0):
    a = atr(df, n)
    hl2 = (df["high"] + df["low"]) / 2
    upper = hl2 + mult * a
    lower = hl2 - mult * a
    dir_ = pd.Series(1, index=df.index)
    for i in range(1, len(df)):
        if df["close"].iloc[i] > upper.iloc[i - 1]:
            dir_.iloc[i] = 1
        elif df["close"].iloc[i] < lower.iloc[i - 1]:
            dir_.iloc[i] = -1
        else:
            dir_.iloc[i] = dir_.iloc[i - 1]
    line = np.where(dir_ == 1, lower, upper)
    return pd.Series(line, index=df.index), dir_


def compute_all(df):
    out = df.copy()
    out["sma20"] = sma(out["close"], 20)
    out["sma50"] = sma(out["close"], 50)
    out["sma200"] = sma(out["close"], 200)
    out["rsi"] = rsi(out["close"])
    ml, ms, mh = macd(out["close"])
    out["macd"], out["macd_sig"], out["macd_hist"] = ml, ms, mh
    out["bb_upper"], out["bb_mid"], out["bb_lower"] = bollinger(out["close"])
    out["atr"] = atr(out)
    out["vwap"] = vwap(out)
    adx_v, pdi, mdi = adx(out)
    out["adx"], out["+di"], out["-di"] = adx_v, pdi, mdi
    st, st_dir = supertrend(out)
    out["supertrend"], out["st_dir"] = st, st_dir
    return out
