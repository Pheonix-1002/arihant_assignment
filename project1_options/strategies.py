"""Strategy library. Long options are defined-risk."""

from dataclasses import dataclass, field


@dataclass
class Leg:
    kind: str
    direction: int
    strike: int
    qty: int = 1


@dataclass
class Strategy:
    name: str
    legs: list
    defined_risk: bool
    notes: str = ""
    tags: list = field(default_factory=list)


def build(name: str, spot: float, strikes: list):
    s = min(strikes, key=lambda k: abs(k - spot))
    i = strikes.index(s)
    def k(off):
        return strikes[max(0, min(len(strikes) - 1, i + off))]
    if name == "long_call":
        return Strategy("Long Call", [Leg("call", +1, k(0))], True,
                        "Loss capped at premium; theta drag.",
                        ["bullish", "debit", "defined"])
    if name == "long_put":
        return Strategy("Long Put", [Leg("put", +1, k(0))], True,
                        "Loss capped at premium; theta drag.",
                        ["bearish", "debit", "defined"])
    if name == "bull_call_spread":
        return Strategy("Bull Call Spread",
                        [Leg("call", +1, k(0)), Leg("call", -1, k(2))],
                        True, "Capped upside; limited cost.",
                        ["bullish", "debit", "defined"])
    if name == "bear_put_spread":
        return Strategy("Bear Put Spread",
                        [Leg("put", +1, k(0)), Leg("put", -1, k(-2))],
                        True, "Capped downside.",
                        ["bearish", "debit", "defined"])
    if name == "bull_put_spread":
        return Strategy("Bull Put Spread",
                        [Leg("put", -1, k(-2)), Leg("put", +1, k(-4))],
                        True, "Credit received; capped risk.",
                        ["bullish", "credit", "defined"])
    if name == "bear_call_spread":
        return Strategy("Bear Call Spread",
                        [Leg("call", -1, k(2)), Leg("call", +1, k(4))],
                        True, "Credit received; capped risk.",
                        ["bearish", "credit", "defined"])
    if name == "iron_condor":
        return Strategy("Iron Condor",
                        [Leg("put", -1, k(-2)), Leg("put", +1, k(-4)),
                         Leg("call", -1, k(2)), Leg("call", +1, k(4))],
                        True, "Range-bound; four legs.",
                        ["neutral", "credit", "defined"])
    if name == "long_straddle":
        return Strategy("Long Straddle",
                        [Leg("call", +1, k(0)), Leg("put", +1, k(0))],
                        True, "Loss capped at premium; needs a big move.",
                        ["volatile", "debit", "defined"])
    if name == "short_strangle":
        return Strategy("Short Strangle",
                        [Leg("call", -1, k(2)), Leg("put", -1, k(-2))],
                        False, "Undefined risk; event danger.",
                        ["neutral", "credit", "undefined"])
    return None


LIBRARY = [
    "long_call", "long_put", "bull_call_spread", "bear_put_spread",
    "bull_put_spread", "bear_call_spread", "iron_condor",
    "long_straddle", "short_strangle",
]
