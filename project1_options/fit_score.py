"""Fit Score (0-100). Weights per PRD; risk appetite reweights."""


def net_premium(strategy, chain):
    px_map = {r["strike"]: r for r in chain["rows"]}
    total = 0.0
    for leg in strategy.legs:
        r = px_map[leg.strike]
        px = r["call_ltp"] if leg.kind == "call" else r["put_ltp"]
        total += -leg.direction * px * leg.qty
    return round(total, 2)


def score(strategy, chain, view: dict, analysis: dict,
          risk_summary: dict = None) -> dict:
    weights = _weights(view.get("risk", "balanced"))
    comps = {
        "view_alignment": _view_align(strategy, view, analysis),
        "vol_alignment": _vol_align(strategy, view, analysis),
        "risk_fit": _risk_fit(strategy, view, chain, risk_summary),
        "reward_prob": _reward_prob(risk_summary),
        "execution": _execution(strategy, chain),
    }
    total = sum(weights[k] * comps[k] for k in comps)
    return {"total": round(total, 1),
            "breakdown": {k: round(v, 1) for k, v in comps.items()},
            "weights": weights}


def _weights(appetite):
    if appetite == "conservative":
        return {"view_alignment": 0.25, "vol_alignment": 0.15,
                "risk_fit": 0.40, "reward_prob": 0.10, "execution": 0.10}
    if appetite == "aggressive":
        return {"view_alignment": 0.35, "vol_alignment": 0.25,
                "risk_fit": 0.15, "reward_prob": 0.15, "execution": 0.10}
    return {"view_alignment": 0.30, "vol_alignment": 0.20,
            "risk_fit": 0.25, "reward_prob": 0.15, "execution": 0.10}


def _view_align(strategy, view, analysis):
    want = view.get("direction", "neutral")
    tags = set(strategy.tags)
    if want == "bullish":
        return 90 if ("bullish" in tags or "neutral-bullish" in tags) else 30
    if want == "bearish":
        return 90 if "bearish" in tags else 30
    if want == "neutral":
        return 90 if "neutral" in tags or "neutral-bullish" in tags else 40
    if want == "volatile":
        return 90 if "volatile" in tags else 40
    return 50


def _vol_align(strategy, view, analysis):
    regime = analysis["regime"]
    is_credit = "credit" in strategy.tags
    if regime == "Elevated":
        return 90 if is_credit else 40
    if regime == "Normal-High":
        return 75 if is_credit else 55
    if regime == "Low":
        return 40 if is_credit else 85
    return 65


def _risk_fit(strategy, view, chain, r):
    if r is None:
        return 85 if strategy.defined_risk else 40
    if r["unbounded_loss"]:
        return 10 if view.get("risk") == "conservative" else 35
    budget = view.get("max_loss")
    if not budget:
        return 85
    loss = abs(r["max_loss"]) * chain["lot"]
    util = loss / budget
    return max(0.0, min(100.0, 100 - 60 * min(util, 1.5)))


def _reward_prob(r):
    if r is None:
        return 70
    loss = abs(r["max_loss"])
    if r["unbounded_profit"] or loss == 0:
        rr = 3.0
    else:
        rr = max(0.0, r["max_profit"]) / loss
    return 0.5 * (r["pop_model"] * 100) + 0.5 * (min(rr, 3.0) / 3.0 * 100)


def _execution(strategy, chain):
    n = len(strategy.legs)
    return max(20, 95 - 8 * (n - 1))
