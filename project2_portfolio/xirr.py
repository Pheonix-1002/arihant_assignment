"""XIRR via bisection."""


def xirr(cash_flows, guess=0.1):
    if not cash_flows:
        return 0.0
    d0 = min(d for d, _ in cash_flows)
    years = [(d - d0).days / 365.0 for d, _ in cash_flows]
    amounts = [a for _, a in cash_flows]
    def npv(r):
        return sum(a / (1 + r) ** t for a, t in zip(amounts, years))
    lo, hi = -0.99, 10.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        v = npv(mid)
        if abs(v) < 1e-6:
            return mid
        if v > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)
