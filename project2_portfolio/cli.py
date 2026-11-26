"""Run: python -m project2_portfolio.cli"""

from shared.narrative import NarrativeEngine
from . import analyzer, health_score, insights


def main():
    a = analyzer.analyze()
    h = health_score.score(a)
    print("=" * 64)
    print(f"PORTFOLIO  Total Rs {a['total']:,.0f}   "
          f"XIRR {a['portfolio_xirr']}%   HHI {a['hhi']}   "
          f"AS OF {a['as_of']}")
    print("=" * 64)
    print(f"HEALTH SCORE  {h['total']:.0f}/100   "
          f"(weakest: {h['weakest']})")
    print("Breakdown:")
    for k, v in h["breakdown"].items():
        tag = ("  [placeholder]" if k in h["placeholders"] else "")
        print(f"  {k:<20} {v:>5.0f}   weight "
              f"{h['weights'][k] * 100:.0f}%{tag}")
    print()
    print("Top holdings:")
    for sym, w in a["top3"]:
        print(f"  {sym:<15} {w * 100:>5.1f}%   "
              f"XIRR {a['per_xirr'].get(sym, 0):>6.2f}%")
    print()
    if a.get("eff_top3"):
        print("Look-through top 3:")
        for sym, w in a["eff_top3"]:
            print(f"  {sym:<15} {w * 100:>5.1f}%")
        print()
    print("INSIGHTS")
    for c in insights.generate(a, h):
        print(f"[{c['priority']:>2}] {c['title']}")
        print(f"     Why: {c['why']}")
        print(f"     Act: {c['action']}")
        print()
    ne = NarrativeEngine(use_llm=True)
    narrative = ne.synthesize(
        "Your portfolio totals {total} with XIRR of {xirr} percent. "
        "Health score is {health} out of 100. The weakest component "
        "is {weak} at {weakval}.",
        {
            "total": f"{a['total']:,.0f}",
            "xirr": a["portfolio_xirr"],
            "health": h["total"],
            "weak": h["weakest"],
            "weakval": h["breakdown"][h["weakest"]],
            "confidence": "medium",
        },
    )
    print("AI LENS")
    print(f"  {narrative['text']}")
    print(f"  [source: {narrative['source']}]")


if __name__ == "__main__":
    main()
