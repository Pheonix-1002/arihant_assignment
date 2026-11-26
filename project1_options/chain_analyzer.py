"""OI / IV / Greeks / PCR analysis with three-vote lean."""

import numpy as np


def analyze(chain: dict) -> dict:
    rows = chain["rows"]
    spot = chain["spot"]
    dte = chain.get("days_to_expiry", 7)
    strikes = np.array([r["strike"] for r in rows])
    call_oi = np.array([r["call_oi"] for r in rows])
    put_oi = np.array([r["put_oi"] for r in rows])
    call_doi = np.array([r["call_doi"] for r in rows])
    put_doi = np.array([r["put_doi"] for r in rows])
    ivs = np.array([r["call_iv"] for r in rows])
    total_put = put_oi.sum()
    total_call = call_oi.sum()
    pcr = float(total_put / total_call) if total_call else 1.0
    zscore = (pcr - 1.05) / 0.18
    call_wall_idx = int(np.argmax(np.where(strikes >= spot, call_oi, 0)))
    put_wall_idx = int(np.argmax(np.where(strikes <= spot, put_oi, 0)))
    call_wall = int(strikes[call_wall_idx])
    put_wall = int(strikes[put_wall_idx])
    atm_idx = int(np.argmin(np.abs(strikes - spot)))
    atm_iv = float(ivs[atm_idx])
    iv_percentile = float(min(99, max(1, (atm_iv - 10) / 10 * 100)))
    max_pain = _max_pain(strikes, call_oi, put_oi, spot)
    if iv_percentile >= 80:
        regime = "Elevated"
    elif iv_percentile >= 55:
        regime = "Normal-High"
    elif iv_percentile >= 30:
        regime = "Normal"
    else:
        regime = "Low"
    pcr_vote = 1 if zscore >= 0.5 else (-1 if zscore <= -0.5 else 0)
    net_doi = float(put_doi.sum() - call_doi.sum())
    denom = float(np.abs(put_doi).sum() + np.abs(call_doi).sum()) + 1.0
    ratio = net_doi / denom
    doi_vote = 1 if ratio > 0.05 else (-1 if ratio < -0.05 else 0)
    room_up = max(call_wall - spot, 1.0)
    room_dn = max(spot - put_wall, 1.0)
    wall_vote = 1 if room_up > 1.25 * room_dn else (
        -1 if room_dn > 1.25 * room_up else 0)
    votes = {"pcr": pcr_vote, "oi_change": doi_vote, "walls": wall_vote}
    total = sum(votes.values())
    sign = int(np.sign(total))
    aligned = sum(1 for v in votes.values() if sign != 0 and v == sign)
    if total >= 2:
        lean = "Bullish"
    elif total == 1:
        lean = "Neutral-Bullish"
    elif total == -1:
        lean = "Neutral-Bearish"
    elif total <= -2:
        lean = "Bearish"
    else:
        lean = "Neutral"
    strength = "high" if abs(total) >= 3 else (
        "medium" if abs(total) == 2 else "low")
    confidence = "High" if aligned >= 3 else (
        "Medium" if aligned == 2 else "Low")
    expected_move = spot * (atm_iv / 100.0) * np.sqrt(max(dte, 1) / 365.0)
    return {
        "spot": spot, "atm_iv": round(atm_iv, 2),
        "iv_percentile": round(iv_percentile, 0), "regime": regime,
        "pcr": round(pcr, 3), "pcr_z": round(float(zscore), 2),
        "call_wall": call_wall, "put_wall": put_wall,
        "max_pain": max_pain, "lean": lean, "strength": strength,
        "confidence": confidence, "signal_agreement": aligned,
        "votes": votes, "expected_move": round(float(expected_move), 1),
        "band_1s": (round(spot - expected_move, 0),
                    round(spot + expected_move, 0)),
        "band_2s": (round(spot - 2 * expected_move, 0),
                    round(spot + 2 * expected_move, 0)),
        "rows": rows,
    }


def _max_pain(strikes, call_oi, put_oi, spot):
    best_k, best_loss = spot, float("inf")
    for K in strikes:
        loss = float(sum(
            (call_oi[i] * max(0, K - strikes[i]))
            + (put_oi[i] * max(0, strikes[i] - K))
            for i in range(len(strikes))
        ))
        if loss < best_loss:
            best_loss, best_k = loss, K
    return int(best_k)
