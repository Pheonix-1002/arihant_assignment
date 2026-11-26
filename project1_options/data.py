"""Synthetic NIFTY option chain with IV smile and OI distribution."""

import math
import os
import random
import numpy as np

from shared.black_scholes import price, greeks

SPOT = 24712.0
R = 0.065
LOT = int(os.environ.get("NIFTY_LOT", "75"))


def _iv_smile(strike, spot, base_iv=0.142, skew=-0.015, curv=0.0003):
    m = (strike - spot) / spot
    return max(0.08, base_iv + skew * m + curv * (m * 100) ** 2)


def _oi_weights(strikes, spot):
    out = []
    for k in strikes:
        d = abs(k - spot) / spot
        base = math.exp(-((d / 0.008) ** 2))
        roundness = 1.4 if k % 100 == 0 else (1.15 if k % 50 == 0 else 1.0)
        out.append(base * roundness)
    return out


def build_chain(days_to_expiry: int = 7, seed: int = 7):
    random.seed(seed)
    np.random.seed(seed)
    T = days_to_expiry / 365.0
    strikes = list(range(24200, 25201, 50))
    w = _oi_weights(strikes, SPOT)
    w = np.array(w) / sum(w)
    call_oi = (w * 1_800_000 + np.random.normal(0, 20000, len(w))).astype(int)
    put_oi = (w * 2_200_000 + np.random.normal(0, 20000, len(w))).astype(int)
    call_oi = np.clip(call_oi, 5000, None)
    put_oi = np.clip(put_oi, 5000, None)
    chain = []
    for i, K in enumerate(strikes):
        iv = _iv_smile(K, SPOT)
        c_px = price(SPOT, K, T, R, iv, "call")
        p_px = price(SPOT, K, T, R, iv, "put")
        c_g = greeks(SPOT, K, T, R, iv, "call")
        p_g = greeks(SPOT, K, T, R, iv, "put")
        sp = lambda px: max(1.0, px * 0.005)
        chain.append({
            "strike": K,
            "call_oi": int(call_oi[i]), "put_oi": int(put_oi[i]),
            "call_doi": int(np.random.normal(0, call_oi[i] * 0.08)),
            "put_doi": int(np.random.normal(0, put_oi[i] * 0.08)),
            "call_iv": round(iv * 100, 2), "put_iv": round(iv * 100, 2),
            "call_ltp": round(c_px, 2), "put_ltp": round(p_px, 2),
            "call_bid": round(c_px - sp(c_px), 2),
            "call_ask": round(c_px + sp(c_px), 2),
            "put_bid": round(p_px - sp(p_px), 2),
            "put_ask": round(p_px + sp(p_px), 2),
            "call_delta": round(c_g["delta"], 4),
            "call_gamma": round(c_g["gamma"], 6),
            "call_theta": round(c_g["theta"], 2),
            "call_vega": round(c_g["vega"], 2),
            "put_delta": round(p_g["delta"], 4),
            "put_gamma": round(p_g["gamma"], 6),
            "put_theta": round(p_g["theta"], 2),
            "put_vega": round(p_g["vega"], 2),
        })
    return {"spot": SPOT, "strikes": strikes, "rows": chain,
            "days_to_expiry": days_to_expiry, "r": R, "lot": LOT}
