"""Run: python -m project1_options.cli"""

from shared.narrative import NarrativeEngine
from . import data, chain_analyzer, finder, risk


def main():
    chain = data.build_chain()
    a = chain_analyzer.analyze(chain)
    print("=" * 64)
    print(f"NIFTY  {a['spot']:.0f}   DTE {chain['days_to_expiry']}")
    print("=" * 64)
    print(f"Regime: {a['regime']}   ATM IV: {a['atm_iv']}% "
          f"({a['iv_percentile']:.0f}th pct)   PCR: {a['pcr']} "
          f"(z {a['pcr_z']})")
    print(f"Call wall: {a['call_wall']}   Put wall: {a['put_wall']}   "
          f"Max pain: {a['max_pain']}")
    print(f"Lean: {a['lean']} ({a['strength']})   "
          f"Confidence: {a['confidence']}")
    print(f"Expected move (1s): {a['band_1s']}   (2s): {a['band_2s']}")
    print()
    view = {"direction": "bullish", "risk": "balanced",
            "defined_only": True, "max_loss": 10000}
    print(f"View: {view}")
    print("-" * 64)
    results = finder.find(view, chain, top_n=3)
    for i, r in enumerate(results, 1):
        legs = " / ".join(
            f"{'+' if d > 0 else '-'}1 "
            f"{k.upper()} {st} ({'B' if d > 0 else 'S'})"
            for k, d, st in r["legs"])
        rk = r["risk"]
        print(f"#{i} {r['name']:<20} Fit {r['fit']['total']:>5}")
        print(f"    Legs: {legs}")
        print(f"    Net premium: {r['net_premium']:+.0f}  "
              f"Max P: {rk['max_profit_label']}  "
              f"Max L: {rk['max_loss_label']}  "
              f"POP ~{rk['pop_model'] * 100:.0f}%")
        print(f"    BE: {rk['breakevens']}")
        print()
    if results:
        top = results[0]
        print("=" * 64)
        print(f"RISK ANALYZER - {top['name']}")
        print("=" * 64)
        print(f"Worst case: {top['risk']['max_loss_label']}")
        print("WHAT-IF P&L (per unit):")
        print("           IV -5    IV 0     IV +5")
        for ss, row in risk.scenario_grid(top["strategy"], chain):
            print(f"  Spot {ss * 100:+.0f}%  " +
                  "   ".join(f"{x:>7.0f}" for x in row))
        print()
        ne = NarrativeEngine(use_llm=True)
        narrative = ne.regime_summary({
            "lean": a["lean"], "strength": a["strength"],
            "iv_percentile": int(a["iv_percentile"]),
            "confidence": a["confidence"],
            "flip": f"a close beyond {a['call_wall']} or {a['put_wall']}",
        })
        print("AI LENS")
        print(f"  {narrative['text']}")
        print(f"  [source: {narrative['source']}, "
              f"confidence: {narrative['confidence']}]")


if __name__ == "__main__":
    main()
