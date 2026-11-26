"""Payoff, breakevens, scenario grid, POP (seeded MC)."""

import numpy as np

from shared.black_scholes import price


def _row(chain, strike):
    return next(x for x in chain["rows"] if x["strike"] == strike)


def _pnl_at(strategy, chain, S):
    S = np.atleast_1d(np.asarray(S, dtype=float))
    pnl = np.zeros_like(S)
    for leg in strategy.legs:
        r = _row(chain, leg.strike)
        prem = r["call_ltp"] if leg.kind == "call" else r["put_ltp"]
        if leg.kind == "call":
            intr = np.maximum(0.0, S - leg.strike)
        else:
            intr = np.maximum(0.0, leg.strike - S)
        pnl += leg.direction * leg.qty * (intr - prem)
    return pnl


def _atm_iv(chain):
    row = min(chain["rows"], key=lambda r: abs(r["strike"] - chain["spot"]))
    return row["call_iv"] / 100.0


def _breakevens(S, pnl):
    out = []
    for j in range(1, len(S)):
        p0, p1 = pnl[j - 1], pnl[j]
        if p0 == 0:
            out.append(round(float(S[j - 1]), 1))
        elif p0 * p1 < 0:
            x = S[j - 1] - p0 * (S[j] - S[j - 1]) / (p1 - p0)
            out.append(round(float(x), 1))
    return sorted(set(out))


def payoff_at_expiry(strategy, chain, spot_range=None):
    spot = chain["spot"]
    if spot_range is None:
        spot_range = np.linspace(spot * 0.92, spot * 1.08, 81)
    return spot_range, _pnl_at(strategy, chain, spot_range)


def summary(strategy, chain, seed: int = 42):
    spot = chain["spot"]
    lot = chain["lot"]
    wide = np.linspace(spot * 0.8, spot * 1.2, 1601)
    pnl_w = _pnl_at(strategy, chain, wide)
    tail = _pnl_at(strategy, chain, [0.0])[0]
    max_profit = float(max(pnl_w.max(), tail))
    max_loss = float(min(pnl_w.min(), tail))
    net_calls = sum(l.direction * l.qty
                    for l in strategy.legs if l.kind == "call")
    unbounded_loss = net_calls < 0
    unbounded_profit = net_calls > 0
    iv = _atm_iv(chain)
    T = chain["days_to_expiry"] / 365.0
    mu = np.log(spot) + (chain["r"] - 0.5 * iv ** 2) * T
    rng = np.random.default_rng(seed)
    S_end = np.exp(rng.normal(mu, iv * np.sqrt(T), 20000))
    pop = float((_pnl_at(strategy, chain, S_end) > 0).mean())
    S_plot, pnl_plot = payoff_at_expiry(strategy, chain)
    if unbounded_loss:
        stress = float(pnl_w.min())
        loss_label = (f"Unlimited (at -20%/+20%: Rs "
                      f"{abs(stress) * lot:,.0f}/lot)")
    else:
        loss_label = f"Rs {abs(max_loss) * lot:,.0f} / lot"
    profit_label = ("Unlimited" if unbounded_profit
                    else f"Rs {max_profit * lot:,.0f} / lot")
    return {
        "max_profit": round(max_profit, 0),
        "max_loss": round(max_loss, 0),
        "unbounded_loss": bool(unbounded_loss),
        "unbounded_profit": bool(unbounded_profit),
        "max_profit_label": profit_label,
        "max_loss_label": loss_label,
        "breakevens": _breakevens(wide, pnl_w),
        "pop_model": round(pop, 3),
        "spot_range": S_plot, "pnl": pnl_plot,
    }


def scenario_grid(strategy, chain,
                  spot_shocks=(-0.02, 0, 0.02),
                  iv_shocks=(-5, 0, 5)):
    spot = chain["spot"]
    T = chain["days_to_expiry"] / 365.0
    r = chain["r"]
    grid = []
    for ss in spot_shocks:
        row = []
        for vs in iv_shocks:
            pnl = 0.0
            S = spot * (1 + ss)
            for leg in strategy.legs:
                rr = _row(chain, leg.strike)
                iv_col = "call_iv" if leg.kind == "call" else "put_iv"
                new_iv = max(0.01, rr[iv_col] / 100.0 + vs / 100.0)
                new_px = price(S, leg.strike, T, r, new_iv, leg.kind)
                prem = rr["call_ltp"] if leg.kind == "call" else rr["put_ltp"]
                pnl += leg.direction * leg.qty * (new_px - prem)
            row.append(round(pnl, 0))
        grid.append((ss, row))
    return grid
