"""Allocation, concentration, fund look-through, XIRR."""

from datetime import date

from .xirr import xirr
from .data import HOLDINGS, FUND_STOCKS

AS_OF = date(2025, 6, 30)


def analyze():
    total = sum(h["value"] for h in HOLDINGS)
    weights = {h["symbol"]: h["value"] / total for h in HOLDINGS}
    sectors = {}
    for h in HOLDINGS:
        sectors[h["sector"]] = sectors.get(h["sector"], 0) + h["value"]
    sector_w = {k: v / total for k, v in sectors.items()}
    stocks = [h for h in HOLDINGS if h["type"] == "stock"]
    stock_total = sum(h["value"] for h in stocks) or 1.0
    eq_sec = {}
    for h in stocks:
        eq_sec[h["sector"]] = eq_sec.get(h["sector"], 0) + h["value"]
    equity_sectors = {k: v / stock_total for k, v in eq_sec.items()}
    hhi = sum(w * w for w in weights.values())
    lt = {}
    for h in HOLDINGS:
        if h["type"] == "stock":
            lt[h["symbol"]] = lt.get(h["symbol"], 0) + h["value"]
        elif h["type"] == "mf":
            names = FUND_STOCKS.get(h["symbol"], set())
            for s in names:
                lt[s] = lt.get(s, 0) + h["value"] / len(names)
    lt_total = sum(lt.values()) or 1.0
    eff_weights = {k: v / lt_total for k, v in lt.items()}
    eff_top3 = sorted(eff_weights.items(), key=lambda kv: -kv[1])[:3]
    per_xirr = {}
    total_flows = []
    for h in HOLDINGS:
        cf = list(h["txns"]) + [(AS_OF, h["value"])]
        per_xirr[h["symbol"]] = round(xirr(cf) * 100, 2)
        total_flows.extend(h["txns"])
    total_flows.append((AS_OF, total))
    portfolio_xirr = round(xirr(total_flows) * 100, 2)
    overlaps = []
    funds = [k for k, v in FUND_STOCKS.items() if v]
    for i in range(len(funds)):
        for j in range(i + 1, len(funds)):
            a = FUND_STOCKS[funds[i]]
            b = FUND_STOCKS[funds[j]]
            if not a or not b:
                continue
            ov = len(a & b) / min(len(a), len(b))
            if ov >= 0.4:
                overlaps.append((funds[i], funds[j], round(ov, 2)))
    top3 = sorted(weights.items(), key=lambda kv: -kv[1])[:3]
    return {
        "total": total, "weights": weights, "sectors": sector_w,
        "equity_sectors": equity_sectors,
        "eff_weights": eff_weights, "eff_top3": eff_top3,
        "hhi": round(hhi, 3), "per_xirr": per_xirr,
        "portfolio_xirr": portfolio_xirr, "overlaps": overlaps,
        "top3": top3, "as_of": AS_OF.isoformat(),
    }
