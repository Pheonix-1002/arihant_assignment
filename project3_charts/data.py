"""OHLCV fetcher with mock fallback."""

import numpy as np
import pandas as pd

COLS = ["open", "high", "low", "close", "volume"]


def fetch(symbol="RELIANCE.NS", period="1y"):
    try:
        import yfinance as yf
        df = yf.download(symbol, period=period, interval="1d",
                         progress=False, auto_adjust=True)
        if df is not None and len(df) > 50:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df.rename(columns=str.lower)
            df = df[COLS].dropna()
            df.attrs["source"] = f"live (yfinance, {symbol})"
            return df
    except Exception:
        pass
    np.random.seed(42)
    n = 300
    rets = np.random.normal(0.0004, 0.014, n)
    close = 1400 * np.exp(np.cumsum(rets))
    high = close * (1 + np.abs(np.random.normal(0, 0.008, n)))
    low = close * (1 - np.abs(np.random.normal(0, 0.008, n)))
    open_ = close * (1 + np.random.normal(0, 0.004, n))
    volume = (np.random.lognormal(15, 0.4, n)).astype(int)
    idx = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=n)
    df = pd.DataFrame(
        {"open": open_, "high": high, "low": low,
         "close": close, "volume": volume}, index=idx)
    df.attrs["source"] = "MOCK (synthetic)"
    return df
