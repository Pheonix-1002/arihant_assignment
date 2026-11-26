"""Ranked, deduplicated insight cards."""


def generate(analysis, health):
    cards = []
    top_sym, top_w = analysis["top3"][0]
    if top_w > 0.15:
        cards.append({
            "priority": 10,
            "title": f"{top_sym} is {top_w * 100:.0f}% of your portfolio",
            "why": "Single-holding weight above 15% raises "
                   "idiosyncratic risk.",
            "action": "Consider trimming or adding complementary assets.",
        })
    eff = analysis.get("eff_top3") or []
    if eff and eff[0][1] > 0.15:
        sym, w = eff[0]
        cards.append({
            "priority": 9,
            "title": (f"Look-through exposure to {sym} is "
                      f"{w * 100:.0f}% of equity"),
            "why": "Direct holdings and funds both own it.",
            "action": "Check fund constituents before adding more.",
        })
    eq = analysis.get("equity_sectors", {})
    if eq:
        top_sec = max(eq, key=eq.get)
        if eq[top_sec] > 0.35:
            cards.append({
                "priority": 8,
                "title": (f"{top_sec} is {eq[top_sec] * 100:.0f}% of "
                          f"direct stock holdings"),
                "why": "Sector concentration amplifies drawdowns.",
                "action": "Rebalance across at least 3 sectors.",
            })
    for a, b, ov in analysis["overlaps"][:2]:
        cards.append({
            "priority": 7,
            "title": f"Funds {a} and {b} overlap {ov * 100:.0f}%",
            "why": "Overlap gives the appearance of diversification.",
            "action": "Consider consolidating or replacing one fund.",
        })
    weakest = health["weakest"]
    note = (" (placeholder score)" if weakest in health.get("placeholders", [])
            else "")
    cards.append({
        "priority": 5,
        "title": (f"Weakest area: {weakest} "
                  f"({health['breakdown'][weakest]}/100){note}"),
        "why": "Improving the lowest component has the highest impact.",
        "action": "Review holdings in this dimension.",
    })
    cards.sort(key=lambda c: -c["priority"])
    return cards
