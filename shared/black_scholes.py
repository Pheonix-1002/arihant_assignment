"""Black-Scholes pricing and Greeks."""

import math


def _cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def price(S, K, T, r, sigma, kind="call"):
    """European option price. T in years."""
    if T <= 0:
        return max(0.0, S - K) if kind == "call" else max(0.0, K - S)
    if sigma <= 1e-9:
        fwd = S - K * math.exp(-r * T)
        return max(0.0, fwd) if kind == "call" else max(0.0, -fwd)
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if kind == "call":
        return S * _cdf(d1) - K * math.exp(-r * T) * _cdf(d2)
    return K * math.exp(-r * T) * _cdf(-d2) - S * _cdf(-d1)


def greeks(S, K, T, r, sigma, kind="call"):
    """Return delta, gamma, theta (per day), vega (per vol pt), rho (per pct)."""
    if T <= 0 or sigma <= 1e-9:
        return {"delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0, "rho": 0.0}
    sq = math.sqrt(T)
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * sq)
    d2 = d1 - sigma * sq
    delta = _cdf(d1) if kind == "call" else _cdf(d1) - 1.0
    gamma = _pdf(d1) / (S * sigma * sq)
    vega = S * _pdf(d1) * sq / 100.0
    if kind == "call":
        theta = (-S * _pdf(d1) * sigma / (2 * sq)
                 - r * K * math.exp(-r * T) * _cdf(d2)) / 365.0
        rho = K * T * math.exp(-r * T) * _cdf(d2) / 100.0
    else:
        theta = (-S * _pdf(d1) * sigma / (2 * sq)
                 + r * K * math.exp(-r * T) * _cdf(-d2)) / 365.0
        rho = -K * T * math.exp(-r * T) * _cdf(-d2) / 100.0
    return {"delta": delta, "gamma": gamma, "theta": theta,
            "vega": vega, "rho": rho}


def implied_vol(px, S, K, T, r, kind="call", tol=1e-6, max_iter=100):
    """Newton-Raphson with bisection fallback."""
    if T <= 0 or px <= 0:
        return 0.0
    lo, hi = 1e-3, 5.0
    mid = 0.3
    for _ in range(max_iter):
        p = price(S, K, T, r, mid, kind)
        if abs(p - px) < tol:
            return mid
        v = greeks(S, K, T, r, mid, kind)["vega"] * 100.0
        if abs(v) < 1e-8:
            break
        step = (p - px) / v
        new = mid - step
        if new <= lo or new >= hi:
            break
        mid = new
    lo, hi = 1e-3, 5.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        p = price(S, K, T, r, mid, kind)
        if abs(p - px) < tol:
            return mid
        if p < px:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)
