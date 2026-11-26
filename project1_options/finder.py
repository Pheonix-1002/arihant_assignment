"""View-to-Strategy Finder. Filters run BEFORE scoring."""

from . import strategies, fit_score, risk, chain_analyzer


def find(view: dict, chain: dict, top_n: int = 3) -> list:
    analysis = chain_analyzer.analyze(chain)
    strikes = [r["strike"] for r in chain["rows"]]
    budget = view.get("max_loss")
    candidates = []
    for name in strategies.LIBRARY:
        s = strategies.build(name, chain["spot"], strikes)
        if s is None:
            continue
        r = risk.summary(s, chain)
        if view.get("defined_only") and r["unbounded_loss"]:
            continue
        if budget:
            if r["unbounded_loss"]:
                continue
            if abs(r["max_loss"]) * chain["lot"] > budget:
                continue
        f = fit_score.score(s, chain, view, analysis, r)
        candidates.append({
            "name": s.name,
            "legs": [(l.kind, l.direction, l.strike) for l in s.legs],
            "net_premium": fit_score.net_premium(s, chain),
            "fit": f, "risk": r, "strategy": s, "analysis": analysis,
        })
    candidates.sort(key=lambda c: -c["fit"]["total"])
    return candidates[:top_n]
