"""Portfolio Health Score."""

REFERENCE_XIRR = 12.0


def _clip(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, x))


def score(analysis):
    hhi = analysis["hhi"]
    eq_sec = analysis.get("equity_sectors", {})
    eff = analysis.get("eff_weights", analysis["weights"])
    eff_n = 1.0 / hhi if hhi > 0 else 1.0
    n_score = _clip(eff_n / 10.0 * 100)
    top_sector = max(eq_sec.values()) if eq_sec else 0.0
    sec_score = _clip(100 - max(0.0, top_sector - 0.30) * 250)
    div_score = 0.6 * n_score + 0.4 * sec_score
    top_w = max(eff.values())
    conc_score = _clip(100 - (top_w - 0.10) * 400)
    perf_score = _clip(50 + (analysis["portfolio_xirr"]
                             - REFERENCE_XIRR) * 5)
    qual_score = 72
    cost_score = 78
    comps = {
        "diversification": round(div_score, 0),
        "concentration": round(conc_score, 0),
        "holding_quality": qual_score,
        "performance": round(perf_score, 0),
        "cost_efficiency": cost_score,
    }
    weights = {
        "diversification": 0.25, "concentration": 0.25,
        "holding_quality": 0.20, "performance": 0.20,
        "cost_efficiency": 0.10,
    }
    total = sum(weights[k] * comps[k] for k in comps)
    weakest = min(comps, key=comps.get)
    return {"total": round(total, 0), "breakdown": comps,
            "weakest": weakest, "weights": weights,
            "placeholders": ["holding_quality", "cost_efficiency"]}
