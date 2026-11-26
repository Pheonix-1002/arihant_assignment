#!/usr/bin/env python3
"""
Complete AI Trading Suite generator - final version.

Usage
-----
    cd arihant_assignment
    python generate.py
    python -m streamlit run app.py     # UI
    python demo.py                     # CLI demos

Creates 38 files. Key features:
  * Gemini REST link API (urllib, no SDK)
  * Reads key from Streamlit secrets OR GEMINI_API_KEY env var
  * Template fallback when no key present (app still works)
  * All apply_fixes.py corrections integrated
  * .gitignore prevents secrets.toml from reaching GitHub
  * .streamlit/secrets.toml.example committed for reviewers
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent

FILES = {

# ══════════════════════════════════════════════════════════════════
# TOP LEVEL
# ══════════════════════════════════════════════════════════════════
".gitignore": r'''# Secrets - NEVER commit
.streamlit/secrets.toml
.streamlit/credentials.toml
.env
.env.local

# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/
env/
build/
dist/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
''',

"requirements.txt": r'''numpy>=1.24
pandas>=2.0
scipy>=1.10
streamlit>=1.30
plotly>=5.18
yfinance>=0.2.40
''',

"README.md": r'''# AI Trading Suite

Deterministic core + Streamlit UI for three AI product prototypes:

- Project 1 - AI Options Trading Assistant
- Project 2 - AI Investment Assistant
- Project 3 - AI Chart Intelligence

Numbers are computed by deterministic code (Black-Scholes, XIRR,
indicator math). The narrative layer calls Gemini via the REST
endpoint when a key is present, and falls back to template-based
explanations otherwise. No key required to run - all engines work
fully offline.

## Quick start (no key needed)

    pip install -r requirements.txt
    python -m streamlit run app.py

Opens http://localhost:8501 with all three projects. AI Lens lines
show `[source: template]` - this is the intended behavior.

## Enable live Gemini narratives (optional)

1. Get a free key at https://aistudio.google.com/apikey

2. Copy the example secrets file:

       .streamlit/secrets.toml.example  ->  .streamlit/secrets.toml

3. Paste your key into the new file:

       GEMINI_API_KEY = "AIza..."

4. Restart the app. AI Lens lines now show `[source: gemini]`.

For CLI demos (`python demo.py`), set the key as an environment
variable instead:

    # PowerShell
    $env:GEMINI_API_KEY="AIza..."

    # bash
    export GEMINI_API_KEY="AIza..."

## Deploy to Streamlit Community Cloud

1. Push the repo to GitHub (`.streamlit/secrets.toml` is gitignored,
   so your key never reaches GitHub)
2. Go to https://share.streamlit.io, connect the repo, main file = `app.py`
3. In "Advanced settings" -> "Secrets", paste:

       GEMINI_API_KEY = "AIza..."

4. Deploy. Public URL is generated automatically.

## Model

Default: `gemini-3.1-flash-lite`. Override via `GEMINI_MODEL`
environment variable, or edit `MODEL_ID` in `shared/narrative.py`.

If your API key does not have access to the default model, the
narrative line falls back to template mode and the response shows
`[source: template_fallback (HTTPError)]` - set a different model
via GEMINI_MODEL to fix.

## Architecture

    shared/                  Black-Scholes, Greeks, REST narrative engine
    project1_options/        Chain analyzer, strategies, Fit Score, risk
    project2_portfolio/      XIRR, allocation, health score, insights
    project3_charts/         Indicators, patterns, trend, confluence
    ui/                      Streamlit app
''',

"demo.py": r'''"""Run all three CLI demos sequentially."""

import subprocess
import sys


for mod in ["project1_options.cli",
            "project2_portfolio.cli",
            "project3_charts.cli"]:
    print(f"\n{'#' * 68}\n#  {mod}\n{'#' * 68}\n")
    r = subprocess.run([sys.executable, "-m", mod])
    if r.returncode != 0:
        print(f"[{mod}] exited with code {r.returncode}")
''',

"app.py": r'''"""Streamlit entry point. Run: python -m streamlit run app.py"""

import streamlit as st

st.set_page_config(
    page_title="AI Trading Suite",
    page_icon="\U0001F4C8",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui import home, project1, project2, project3

PAGES = {
    "Home": home,
    "Project 1 - Options Assistant": project1,
    "Project 2 - Portfolio Assistant": project2,
    "Project 3 - Chart Intelligence": project3,
}

with st.sidebar:
    st.title("AI Trading Suite")
    st.caption("Deepanshu Sharma - IIT Guwahati")
    st.divider()
    page = st.radio("Navigate", list(PAGES.keys()),
                    label_visibility="collapsed")
    st.divider()
    st.caption(
        "Deterministic engines compute every number. Narratives use "
        "Gemini via REST when a key is configured, template otherwise."
    )

PAGES[page].render()
''',

# ══════════════════════════════════════════════════════════════════
# STREAMLIT CONFIG
# ══════════════════════════════════════════════════════════════════
".streamlit/config.toml": r'''[theme]
primaryColor = "#2E75B6"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F2F4F7"
textColor = "#1F3A5F"
font = "sans serif"

[browser]
gatherUsageStats = false
''',

".streamlit/secrets.toml.example": r'''# Copy this file to `.streamlit/secrets.toml` and paste your real
# key. secrets.toml is gitignored, so it never reaches GitHub.
# Get a free key at https://aistudio.google.com/apikey

GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
''',

# ══════════════════════════════════════════════════════════════════
# SHARED
# ══════════════════════════════════════════════════════════════════
"shared/__init__.py": r'''"""Shared utilities for the AI Trading Suite."""
''',

"shared/black_scholes.py": r'''"""Black-Scholes pricing and Greeks."""

import math


def _cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def price(S, K, T, r, sigma, kind="call"):
    """European option price. T in years."""
    if T <= 0:
        return max(0.0, S - K) if kind == "call" else max(0.0, K - S)
    if sigma <= 1e-9:
        fwd = S - K * math.exp(-r * T)
        return max(0.0, fwd) if kind == "call" else max(0.0, -fwd)
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if kind == "call":
        return S * _cdf(d1) - K * math.exp(-r * T) * _cdf(d2)
    return K * math.exp(-r * T) * _cdf(-d2) - S * _cdf(-d1)


def greeks(S, K, T, r, sigma, kind="call"):
    """Return delta, gamma, theta (per day), vega (per vol pt), rho (per pct)."""
    if T <= 0 or sigma <= 1e-9:
        return {"delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0, "rho": 0.0}
    sq = math.sqrt(T)
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * sq)
    d2 = d1 - sigma * sq
    delta = _cdf(d1) if kind == "call" else _cdf(d1) - 1.0
    gamma = _pdf(d1) / (S * sigma * sq)
    vega = S * _pdf(d1) * sq / 100.0
    if kind == "call":
        theta = (-S * _pdf(d1) * sigma / (2 * sq)
                 - r * K * math.exp(-r * T) * _cdf(d2)) / 365.0
        rho = K * T * math.exp(-r * T) * _cdf(d2) / 100.0
    else:
        theta = (-S * _pdf(d1) * sigma / (2 * sq)
                 + r * K * math.exp(-r * T) * _cdf(-d2)) / 365.0
        rho = -K * T * math.exp(-r * T) * _cdf(-d2) / 100.0
    return {"delta": delta, "gamma": gamma, "theta": theta,
            "vega": vega, "rho": rho}


def implied_vol(px, S, K, T, r, kind="call", tol=1e-6, max_iter=100):
    """Newton-Raphson with bisection fallback."""
    if T <= 0 or px <= 0:
        return 0.0
    lo, hi = 1e-3, 5.0
    mid = 0.3
    for _ in range(max_iter):
        p = price(S, K, T, r, mid, kind)
        if abs(p - px) < tol:
            return mid
        v = greeks(S, K, T, r, mid, kind)["vega"] * 100.0
        if abs(v) < 1e-8:
            break
        step = (p - px) / v
        new = mid - step
        if new <= lo or new >= hi:
            break
        mid = new
    lo, hi = 1e-3, 5.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        p = price(S, K, T, r, mid, kind)
        if abs(p - px) < tol:
            return mid
        if p < px:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)
''',

"shared/narrative.py": r'''"""Narrative engine: template fallback + Gemini REST API.

Calls the Gemini generateContent endpoint directly via urllib.
No SDK dependency. Reads the API key from Streamlit secrets if
available (Streamlit Cloud / local secrets.toml), otherwise from
the GEMINI_API_KEY environment variable (CLI usage).
"""

import json
import os
import re
import urllib.error
import urllib.request


MODEL_ID = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")
API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

_SYSTEM = (
    "You are a financial explainer inside a decision-support tool. "
    "You receive a JSON object called `evidence` containing numbers "
    "already computed by a deterministic engine. Write ONE short "
    "paragraph (3-5 sentences) that explains what those numbers mean, "
    "in plain language, for a retail trader/investor in India. "
    "Rules: (1) never invent a number not present in `evidence`; "
    "(2) never give a buy/sell recommendation; (3) never predict a "
    "price or guarantee an outcome; (4) end with a single sentence "
    "beginning 'What would change this:'. "
    "Do not output JSON, markdown, or headings - just the paragraph."
)


def _load_api_key() -> str:
    """Streamlit secrets first, then env var. Returns '' if neither."""
    try:
        import streamlit as st
        if "GEMINI_API_KEY" in st.secrets:
            return str(st.secrets["GEMINI_API_KEY"]).strip()
    except Exception:
        pass
    return os.environ.get("GEMINI_API_KEY", "").strip()


class NarrativeEngine:
    def __init__(self, use_llm: bool = True, temperature: float = 0.2,
                 timeout: int = 30):
        self.api_key = _load_api_key()
        self.use_llm = use_llm and bool(self.api_key)
        self.temperature = temperature
        self.timeout = timeout
        self.model_id = MODEL_ID
        self.last_error = None

    def synthesize(self, template: str, evidence: dict,
                   style: str = "plain") -> dict:
        template_text = self._safe_format(template, evidence)

        if not self.use_llm:
            return self._result(template_text, evidence, style, "template")

        try:
            llm_text = self._call_gemini(evidence)
        except Exception as exc:
            self.last_error = f"{type(exc).__name__}: {exc}"
            return self._result(
                template_text, evidence, style,
                f"template_fallback ({type(exc).__name__})"
            )

        if not self._validate_numbers(llm_text, evidence):
            return self._result(
                template_text, evidence, style,
                "template_validator_fallback"
            )

        return self._result(llm_text.strip(), evidence, style, "gemini")

    def regime_summary(self, state: dict) -> dict:
        tmpl = (
            "Bias is {lean} ({strength} strength). ATM IV sits at the "
            "{iv_pct}th percentile. Confidence: {conf}. "
            "What would change this: {flip}."
        )
        return self.synthesize(tmpl, {
            "lean": state["lean"],
            "strength": state["strength"],
            "iv_pct": state["iv_percentile"],
            "conf": state["confidence"],
            "flip": state.get(
                "flip",
                "a close through the nearest OI wall on rising volume",
            ),
            "confidence": state["confidence"],
        })

    def _call_gemini(self, evidence: dict) -> str:
        url = (
            f"{API_BASE}/{self.model_id}:generateContent"
            f"?key={self.api_key}"
        )
        payload = {
            "systemInstruction": {"parts": [{"text": _SYSTEM}]},
            "contents": [{
                "parts": [{
                    "text": (
                        "Evidence JSON:\n"
                        + json.dumps(evidence, default=str, indent=2)
                    )
                }]
            }],
            "generationConfig": {
                "temperature": self.temperature,
                "maxOutputTokens": 400,
            },
        }
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as exc:
            raise RuntimeError(
                f"unexpected Gemini response: {data}"
            ) from exc
        if not text:
            raise RuntimeError("empty Gemini response")
        return text

    @staticmethod
    def _safe_format(template: str, evidence: dict) -> str:
        try:
            return template.format(**evidence)
        except (KeyError, IndexError):
            return template

    @staticmethod
    def _validate_numbers(text: str, evidence: dict) -> bool:
        allowed = set()
        for v in _flatten(evidence):
            try:
                f = float(v)
            except (TypeError, ValueError):
                continue
            allowed.add(f)
            if 0 < abs(f) < 1:
                allowed.add(f * 100)
            elif abs(f) >= 100:
                allowed.add(f / 100)
            allowed.add(round(f))
            allowed.add(round(f, 1))
            allowed.add(round(f, 2))
        if not allowed:
            return True
        for match in re.findall(r"-?\d+(?:\.\d+)?", text):
            try:
                num = float(match)
            except ValueError:
                continue
            tol = max(0.05, 0.005 * abs(num))
            if not any(abs(num - a) < tol for a in allowed):
                return False
        return True

    @staticmethod
    def _result(text, evidence, style, source):
        return {
            "text": text,
            "evidence": evidence,
            "confidence": evidence.get("confidence", "medium"),
            "style": style,
            "source": source,
        }


def _flatten(d):
    if isinstance(d, dict):
        for v in d.values():
            yield from _flatten(v)
    elif isinstance(d, (list, tuple)):
        for item in d:
            yield from _flatten(item)
    elif isinstance(d, str):
        for n in re.findall(r"-?\d+(?:\.\d+)?", d):
            yield n
    else:
        yield d
''',

# ══════════════════════════════════════════════════════════════════
# PROJECT 1
# ══════════════════════════════════════════════════════════════════
"project1_options/__init__.py": r'''"""Project 1: AI Options Trading Assistant."""
''',

"project1_options/data.py": r'''"""Synthetic NIFTY option chain with IV smile and OI distribution."""

import math
import os
import random
import numpy as np

from shared.black_scholes import price, greeks

SPOT = 24712.0
R = 0.065
LOT = int(os.environ.get("NIFTY_LOT", "75"))


def _iv_smile(strike, spot, base_iv=0.142, skew=-0.015, curv=0.0003):
    m = (strike - spot) / spot
    return max(0.08, base_iv + skew * m + curv * (m * 100) ** 2)


def _oi_weights(strikes, spot):
    out = []
    for k in strikes:
        d = abs(k - spot) / spot
        base = math.exp(-((d / 0.008) ** 2))
        roundness = 1.4 if k % 100 == 0 else (1.15 if k % 50 == 0 else 1.0)
        out.append(base * roundness)
    return out


def build_chain(days_to_expiry: int = 7, seed: int = 7):
    random.seed(seed)
    np.random.seed(seed)
    T = days_to_expiry / 365.0
    strikes = list(range(24200, 25201, 50))
    w = _oi_weights(strikes, SPOT)
    w = np.array(w) / sum(w)
    call_oi = (w * 1_800_000 + np.random.normal(0, 20000, len(w))).astype(int)
    put_oi = (w * 2_200_000 + np.random.normal(0, 20000, len(w))).astype(int)
    call_oi = np.clip(call_oi, 5000, None)
    put_oi = np.clip(put_oi, 5000, None)
    chain = []
    for i, K in enumerate(strikes):
        iv = _iv_smile(K, SPOT)
        c_px = price(SPOT, K, T, R, iv, "call")
        p_px = price(SPOT, K, T, R, iv, "put")
        c_g = greeks(SPOT, K, T, R, iv, "call")
        p_g = greeks(SPOT, K, T, R, iv, "put")
        sp = lambda px: max(1.0, px * 0.005)
        chain.append({
            "strike": K,
            "call_oi": int(call_oi[i]), "put_oi": int(put_oi[i]),
            "call_doi": int(np.random.normal(0, call_oi[i] * 0.08)),
            "put_doi": int(np.random.normal(0, put_oi[i] * 0.08)),
            "call_iv": round(iv * 100, 2), "put_iv": round(iv * 100, 2),
            "call_ltp": round(c_px, 2), "put_ltp": round(p_px, 2),
            "call_bid": round(c_px - sp(c_px), 2),
            "call_ask": round(c_px + sp(c_px), 2),
            "put_bid": round(p_px - sp(p_px), 2),
            "put_ask": round(p_px + sp(p_px), 2),
            "call_delta": round(c_g["delta"], 4),
            "call_gamma": round(c_g["gamma"], 6),
            "call_theta": round(c_g["theta"], 2),
            "call_vega": round(c_g["vega"], 2),
            "put_delta": round(p_g["delta"], 4),
            "put_gamma": round(p_g["gamma"], 6),
            "put_theta": round(p_g["theta"], 2),
            "put_vega": round(p_g["vega"], 2),
        })
    return {"spot": SPOT, "strikes": strikes, "rows": chain,
            "days_to_expiry": days_to_expiry, "r": R, "lot": LOT}
''',

"project1_options/chain_analyzer.py": r'''"""OI / IV / Greeks / PCR analysis with three-vote lean."""

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
''',

"project1_options/strategies.py": r'''"""Strategy library. Long options are defined-risk."""

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
''',

"project1_options/risk.py": r'''"""Payoff, breakevens, scenario grid, POP (seeded MC)."""

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
''',

"project1_options/fit_score.py": r'''"""Fit Score (0-100). Weights per PRD; risk appetite reweights."""


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
''',

"project1_options/finder.py": r'''"""View-to-Strategy Finder. Filters run BEFORE scoring."""

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
''',

"project1_options/cli.py": r'''"""Run: python -m project1_options.cli"""

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
''',

# ══════════════════════════════════════════════════════════════════
# PROJECT 2
# ══════════════════════════════════════════════════════════════════
"project2_portfolio/__init__.py": r'''"""Project 2: AI-Powered Investment Assistant."""
''',

"project2_portfolio/data.py": r'''"""Sample 15-holding portfolio with transactions."""

from datetime import date


HOLDINGS = [
    {"symbol": "HDFCBANK", "type": "stock", "sector": "Financials",
     "cost": 180000, "value": 214000,
     "txns": [(date(2023, 1, 15), -180000)]},
    {"symbol": "ICICIBANK", "type": "stock", "sector": "Financials",
     "cost": 120000, "value": 156000,
     "txns": [(date(2023, 3, 10), -120000)]},
    {"symbol": "KOTAKBANK", "type": "stock", "sector": "Financials",
     "cost": 90000, "value": 96000,
     "txns": [(date(2023, 6, 20), -90000)]},
    {"symbol": "RELIANCE", "type": "stock", "sector": "Energy",
     "cost": 210000, "value": 238000,
     "txns": [(date(2022, 11, 5), -210000)]},
    {"symbol": "TCS", "type": "stock", "sector": "IT",
     "cost": 160000, "value": 172000,
     "txns": [(date(2023, 2, 1), -160000)]},
    {"symbol": "INFY", "type": "stock", "sector": "IT",
     "cost": 140000, "value": 148000,
     "txns": [(date(2023, 4, 12), -140000)]},
    {"symbol": "HUL", "type": "stock", "sector": "FMCG",
     "cost": 85000, "value": 91000,
     "txns": [(date(2023, 7, 1), -85000)]},
    {"symbol": "ITC", "type": "stock", "sector": "FMCG",
     "cost": 70000, "value": 78000,
     "txns": [(date(2023, 8, 15), -70000)]},
    {"symbol": "AXISBANK", "type": "stock", "sector": "Financials",
     "cost": 100000, "value": 108000,
     "txns": [(date(2023, 9, 5), -100000)]},
    {"symbol": "MIRAE_EMRG", "type": "mf", "sector": "Diversified",
     "cost": 200000, "value": 232000,
     "txns": [(date(2022, 6, 1), -50000), (date(2022, 12, 1), -50000),
              (date(2023, 6, 1), -50000), (date(2023, 12, 1), -50000)]},
    {"symbol": "PPFAS_FLEXI", "type": "mf", "sector": "Diversified",
     "cost": 150000, "value": 178000,
     "txns": [(date(2022, 4, 1), -50000), (date(2023, 4, 1), -50000),
              (date(2024, 4, 1), -50000)]},
    {"symbol": "HDFC_INDEX", "type": "mf", "sector": "Index",
     "cost": 120000, "value": 128000,
     "txns": [(date(2023, 1, 10), -40000), (date(2024, 1, 10), -80000)]},
    {"symbol": "SBI_SMALLCAP", "type": "mf", "sector": "Small-cap",
     "cost": 80000, "value": 96000,
     "txns": [(date(2023, 5, 20), -80000)]},
    {"symbol": "GOLDBEES", "type": "etf", "sector": "Commodities",
     "cost": 60000, "value": 72000,
     "txns": [(date(2023, 3, 1), -60000)]},
    {"symbol": "NIFTYBEES", "type": "etf", "sector": "Index",
     "cost": 100000, "value": 118000,
     "txns": [(date(2023, 2, 1), -100000)]},
]

FUND_STOCKS = {
    "MIRAE_EMRG": {"HDFCBANK", "ICICIBANK", "RELIANCE", "INFY",
                   "TCS", "AXISBANK", "KOTAKBANK"},
    "PPFAS_FLEXI": {"HDFCBANK", "ICICIBANK", "RELIANCE", "TCS",
                    "HUL", "ITC"},
    "HDFC_INDEX": {"HDFCBANK", "ICICIBANK", "RELIANCE", "TCS",
                   "INFY", "HUL", "ITC", "AXISBANK", "KOTAKBANK"},
    "SBI_SMALLCAP": {"ABC_CHEM", "XYZ_TECH", "PQR_PHARMA"},
}
''',

"project2_portfolio/xirr.py": r'''"""XIRR via bisection."""


def xirr(cash_flows, guess=0.1):
    if not cash_flows:
        return 0.0
    d0 = min(d for d, _ in cash_flows)
    years = [(d - d0).days / 365.0 for d, _ in cash_flows]
    amounts = [a for _, a in cash_flows]
    def npv(r):
        return sum(a / (1 + r) ** t for a, t in zip(amounts, years))
    lo, hi = -0.99, 10.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        v = npv(mid)
        if abs(v) < 1e-6:
            return mid
        if v > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)
''',

"project2_portfolio/analyzer.py": r'''"""Allocation, concentration, fund look-through, XIRR."""

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
''',

"project2_portfolio/health_score.py": r'''"""Portfolio Health Score."""

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
''',

"project2_portfolio/insights.py": r'''"""Ranked, deduplicated insight cards."""


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
''',

"project2_portfolio/cli.py": r'''"""Run: python -m project2_portfolio.cli"""

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
''',

# ══════════════════════════════════════════════════════════════════
# PROJECT 3
# ══════════════════════════════════════════════════════════════════
"project3_charts/__init__.py": r'''"""Project 3: AI Chart Intelligence."""
''',

"project3_charts/data.py": r'''"""OHLCV fetcher with mock fallback."""

import numpy as np
import pandas as pd

COLS = ["open", "high", "low", "close", "volume"]


def fetch(symbol="RELIANCE.NS", period="1y"):
    try:
        import yfinance as yf
        df = yf.download(symbol, period=period, interval="1d",
                         progress=False, auto_adjust=True)
        if df is not None and len(df) > 50:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df.rename(columns=str.lower)
            df = df[COLS].dropna()
            df.attrs["source"] = f"live (yfinance, {symbol})"
            return df
    except Exception:
        pass
    np.random.seed(42)
    n = 300
    rets = np.random.normal(0.0004, 0.014, n)
    close = 1400 * np.exp(np.cumsum(rets))
    high = close * (1 + np.abs(np.random.normal(0, 0.008, n)))
    low = close * (1 - np.abs(np.random.normal(0, 0.008, n)))
    open_ = close * (1 + np.random.normal(0, 0.004, n))
    volume = (np.random.lognormal(15, 0.4, n)).astype(int)
    idx = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=n)
    df = pd.DataFrame(
        {"open": open_, "high": high, "low": low,
         "close": close, "volume": volume}, index=idx)
    df.attrs["source"] = "MOCK (synthetic)"
    return df
''',

"project3_charts/indicators.py": r'''"""Indicators (RSI, MACD, MAs, Bollinger, ATR, ADX, Supertrend, VWAP)."""

import numpy as np
import pandas as pd


def sma(s, n):
    return s.rolling(n).mean()


def ema(s, n):
    return s.ewm(span=n, adjust=False).mean()


def rsi(close, n=14):
    d = close.diff()
    up = d.clip(lower=0).rolling(n).mean()
    dn = (-d.clip(upper=0)).rolling(n).mean()
    rs = up / dn.replace(0, np.nan)
    return 100 - 100 / (1 + rs)


def macd(close, fast=12, slow=26, sig=9):
    line = ema(close, fast) - ema(close, slow)
    signal = ema(line, sig)
    return line, signal, line - signal


def bollinger(close, n=20, k=2):
    m = sma(close, n)
    sd = close.rolling(n).std()
    return m + k * sd, m, m - k * sd


def atr(df, n=14):
    h, l, c = df["high"], df["low"], df["close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(),
                    (l - c.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()


def vwap(df):
    tp = (df["high"] + df["low"] + df["close"]) / 3
    return (tp * df["volume"]).cumsum() / df["volume"].cumsum()


def adx(df, n=14):
    h, l = df["high"], df["low"]
    up = h.diff()
    dn = -l.diff()
    plus = np.where((up > dn) & (up > 0), up, 0.0)
    minus = np.where((dn > up) & (dn > 0), dn, 0.0)
    tr = atr(df, n)
    plus_di = 100 * pd.Series(plus, index=df.index).rolling(n).mean() / tr
    minus_di = 100 * pd.Series(minus, index=df.index).rolling(n).mean() / tr
    dx = (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan) * 100
    return dx.rolling(n).mean(), plus_di, minus_di


def supertrend(df, n=10, mult=3.0):
    a = atr(df, n)
    hl2 = (df["high"] + df["low"]) / 2
    upper = hl2 + mult * a
    lower = hl2 - mult * a
    dir_ = pd.Series(1, index=df.index)
    for i in range(1, len(df)):
        if df["close"].iloc[i] > upper.iloc[i - 1]:
            dir_.iloc[i] = 1
        elif df["close"].iloc[i] < lower.iloc[i - 1]:
            dir_.iloc[i] = -1
        else:
            dir_.iloc[i] = dir_.iloc[i - 1]
    line = np.where(dir_ == 1, lower, upper)
    return pd.Series(line, index=df.index), dir_


def compute_all(df):
    out = df.copy()
    out["sma20"] = sma(out["close"], 20)
    out["sma50"] = sma(out["close"], 50)
    out["sma200"] = sma(out["close"], 200)
    out["rsi"] = rsi(out["close"])
    ml, ms, mh = macd(out["close"])
    out["macd"], out["macd_sig"], out["macd_hist"] = ml, ms, mh
    out["bb_upper"], out["bb_mid"], out["bb_lower"] = bollinger(out["close"])
    out["atr"] = atr(out)
    out["vwap"] = vwap(out)
    adx_v, pdi, mdi = adx(out)
    out["adx"], out["+di"], out["-di"] = adx_v, pdi, mdi
    st, st_dir = supertrend(out)
    out["supertrend"], out["st_dir"] = st, st_dir
    return out
''',

"project3_charts/trend.py": r'''"""Symmetric trend classifier."""


def classify(df):
    last = df.iloc[-1]
    bull = sum([
        bool(last["close"] > last["sma20"]),
        bool(last["sma20"] > last["sma50"]),
        bool(last["sma50"] > last["sma200"]),
        bool(last["st_dir"] == 1),
        bool(last["adx"] > 25 and last["+di"] > last["-di"]),
    ])
    bear = sum([
        bool(last["close"] < last["sma20"]),
        bool(last["sma20"] < last["sma50"]),
        bool(last["sma50"] < last["sma200"]),
        bool(last["st_dir"] == -1),
        bool(last["adx"] > 25 and last["-di"] > last["+di"]),
    ])
    net = bull - bear
    if net >= 4:
        return "Bullish", "high"
    if net >= 2:
        return "Bullish", "medium"
    if net <= -4:
        return "Bearish", "high"
    if net <= -2:
        return "Bearish", "medium"
    return "Sideways", "low"
''',

"project3_charts/patterns.py": r'''"""Candlestick and support/resistance patterns."""


def candlesticks(df):
    pats = []
    for i in range(-5, 0):
        o, h, l, c = (df["open"].iloc[i], df["high"].iloc[i],
                      df["low"].iloc[i], df["close"].iloc[i])
        body = abs(c - o)
        rng = max(h - l, 1e-6)
        upper = h - max(o, c)
        lower = min(o, c) - l
        if body / rng < 0.15:
            pats.append(("Doji", i, "indecision"))
        if lower > 2 * body and upper < body:
            pats.append(("Hammer", i, "possible bottom"))
        if upper > 2 * body and lower < body:
            pats.append(("Shooting Star", i, "possible top"))
    return pats


def support_resistance(df, window=10):
    highs = df["high"].rolling(window, center=True).max()
    lows = df["low"].rolling(window, center=True).min()
    res = [float(x) for x in df["high"][df["high"] == highs].tail(3)]
    sup = [float(x) for x in df["low"][df["low"] == lows].tail(3)]
    return {
        "resistance": round(max(res), 2) if res else None,
        "support": round(min(sup), 2) if sup else None,
    }
''',

"project3_charts/confluence.py": r'''"""5-group confluence with same-direction agreement."""


def _sign(x):
    return (x > 0) - (x < 0)


def evaluate(df):
    last = df.iloc[-1]
    groups = {}
    t = 0
    if last["close"] > last["sma50"]:
        t += 1
    if last["st_dir"] == 1:
        t += 1
    if last["adx"] > 25:
        t += 1
    groups["trend"] = 1 if t >= 2 else (-1 if t == 0 else 0)
    m = 0
    if last["rsi"] > 50:
        m += 1
    if last["macd_hist"] > 0:
        m += 1
    groups["momentum"] = 1 if m == 2 else (-1 if m == 0 else 0)
    p = 0
    vol_avg = df["volume"].rolling(20).mean().iloc[-1]
    if last["volume"] > vol_avg:
        p += 1
    if last["close"] > last["vwap"]:
        p += 1
    groups["participation"] = 1 if p == 2 else (-1 if p == 0 else 0)
    width = max(last["bb_upper"] - last["bb_lower"], 1e-6)
    b = (last["close"] - last["bb_lower"]) / width
    groups["location"] = 1 if b > 0.6 else (-1 if b < 0.4 else 0)
    bw = (df["bb_upper"] - df["bb_lower"]) / df["bb_mid"]
    bw_avg = bw.rolling(20).mean().iloc[-1]
    if bw.iloc[-1] > bw_avg:
        groups["volatility"] = 1 if last["close"] > last["bb_mid"] else -1
    else:
        groups["volatility"] = 0
    direction = sum(groups.values())
    sign = _sign(direction)
    agreement = sum(1 for v in groups.values()
                    if sign != 0 and v == sign)
    bias = ("Bullish" if direction > 1
            else "Bearish" if direction < -1 else "Mixed")
    strength = ("high" if agreement >= 4
                else "medium" if agreement >= 3 else "low")
    return {
        "bias": bias, "strength": strength, "agreement": agreement,
        "groups": groups,
        "conflicts": [k for k, v in groups.items()
                      if sign != 0 and v == -sign],
    }
''',

"project3_charts/cli.py": r'''"""Run: python -m project3_charts.cli"""

from shared.narrative import NarrativeEngine
from . import data, indicators, trend, patterns, confluence


def main():
    df = data.fetch()
    src = df.attrs.get("source", "unknown")
    df = indicators.compute_all(df)
    t = trend.classify(df)
    c = confluence.evaluate(df)
    pr = patterns.support_resistance(df)
    cs = patterns.candlesticks(df)
    last = df.iloc[-1]
    print("=" * 64)
    print(f"AI CHART SUMMARY - {df.index[-1].date()}")
    print(f"Data source: {src}")
    print("=" * 64)
    print(f"Close: {last['close']:.2f}   "
          f"Trend: {t[0]} ({t[1]} strength)")
    print(f"Confluence: {c['agreement']}/5   Bias: {c['bias']}")
    print(f"Groups: {c['groups']}")
    print(f"Support: {pr['support']}   Resistance: {pr['resistance']}")
    print(f"RSI: {last['rsi']:.1f}   "
          f"MACD hist: {last['macd_hist']:+.3f}   "
          f"ADX: {last['adx']:.1f}   "
          f"Supertrend: {'up' if last['st_dir'] == 1 else 'down'}")
    vol_ratio = last["volume"] / df["volume"].rolling(20).mean().iloc[-1]
    print(f"Volume vs 20d: {vol_ratio:.2f}x")
    print(f"Candlestick (last 5): {cs}")
    if c["conflicts"]:
        print(f"Conflicts: {', '.join(c['conflicts'])}")
    print()
    ne = NarrativeEngine(use_llm=True)
    narrative = ne.synthesize(
        "Bias is {bias} ({strength}). Trend groups aligned: "
        "{agree} of 5. Key resistance: {res}. Support: {sup}. "
        "Invalidation: close below {sup}.",
        {
            "bias": c["bias"], "strength": c["strength"],
            "agree": c["agreement"], "res": pr["resistance"],
            "sup": pr["support"], "confidence": c["strength"],
        },
    )
    print("AI LENS")
    print(f"  {narrative['text']}")
    print(f"  [source: {narrative['source']}]")


if __name__ == "__main__":
    main()
''',

# ══════════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════════
"ui/__init__.py": r'''"""Streamlit UI."""
''',

"ui/home.py": r'''"""Landing page."""

import streamlit as st


def render():
    st.title("AI Trading Suite")
    st.subheader("Three AI product prototypes - deterministic core")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### Project 1")
        st.markdown("**AI Options Trading Assistant**")
        st.caption("Chain - View-to-Strategy - Fit Score - Risk Analyzer")
    with c2:
        st.markdown("### Project 2")
        st.markdown("**AI Investment Assistant**")
        st.caption("XIRR - allocation - overlap - Health Score")
    with c3:
        st.markdown("### Project 3")
        st.markdown("**AI Chart Intelligence**")
        st.caption("Indicators - patterns - trend - confluence engine")

    st.divider()
    st.markdown("## How to use")
    st.markdown(
        "1. Use the **sidebar** to navigate between the three projects.\n"
        "2. Interactive inputs everywhere - market view, risk appetite, "
        "symbols, indicator overlays.\n"
        "3. All numbers are computed by deterministic engines "
        "(Black-Scholes, XIRR, indicator math).\n"
        "4. The **AI Lens** shows narrative plus source and confidence."
    )
    st.divider()
    st.info(
        "Deterministic engines run fully offline. When a Gemini API "
        "key is configured (via .streamlit/secrets.toml), the AI Lens "
        "calls the Gemini REST endpoint for narrative prose."
    )
''',

"ui/project1.py": r'''"""Project 1 UI."""

import streamlit as st
import plotly.graph_objects as go

from project1_options import data, chain_analyzer, finder, risk
from shared.narrative import NarrativeEngine


@st.cache_data(show_spinner=False)
def get_chain():
    return data.build_chain()


def render():
    st.title("Project 1 - AI Options Trading Assistant")
    chain = get_chain()
    analysis = chain_analyzer.analyze(chain)

    with st.sidebar:
        st.subheader("Your view")
        direction = st.selectbox(
            "Direction", ["bullish", "bearish", "neutral", "volatile"])
        risk_app = st.selectbox(
            "Risk appetite",
            ["conservative", "balanced", "aggressive"], index=1)
        max_loss = st.number_input(
            "Max loss budget (Rs)",
            min_value=1000, max_value=100000, value=10000, step=1000)
        defined_only = st.checkbox("Defined-risk only", value=True)

    view = {"direction": direction, "risk": risk_app,
            "defined_only": defined_only, "max_loss": int(max_loss)}

    st.subheader("Market Regime")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Spot", f"{analysis['spot']:.0f}")
    c2.metric("ATM IV", f"{analysis['atm_iv']:.1f}%",
              f"{analysis['iv_percentile']:.0f}th pctile")
    c3.metric("PCR", f"{analysis['pcr']:.2f}",
              f"z = {analysis['pcr_z']:.2f}")
    c4.metric("Regime", analysis["regime"])
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Call wall", f"{analysis['call_wall']}")
    c2.metric("Put wall", f"{analysis['put_wall']}")
    c3.metric("Max pain", f"{analysis['max_pain']}")
    c4.metric("Lean", analysis["lean"], analysis["strength"])
    st.caption(
        f"Expected move (1s): {analysis['band_1s']}   "
        f"(2s): {analysis['band_2s']}   "
        f"Votes: {analysis['votes']}")

    st.subheader("Open Interest by Strike")
    strikes = [r["strike"] for r in chain["rows"]]
    call_oi = [r["call_oi"] for r in chain["rows"]]
    put_oi = [r["put_oi"] for r in chain["rows"]]
    fig = go.Figure()
    fig.add_bar(x=strikes, y=call_oi, name="Call OI",
                marker_color="firebrick", opacity=0.75)
    fig.add_bar(x=strikes, y=[-p for p in put_oi], name="Put OI",
                marker_color="seagreen", opacity=0.75)
    fig.add_vline(x=analysis["spot"], line_dash="dash",
                  line_color="black", annotation_text="Spot")
    fig.update_layout(height=340, barmode="relative",
                      margin=dict(l=20, r=20, t=20, b=20),
                      legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Raw option chain (X-Ray view)"):
        rows = [{
            "Call OI": r["call_oi"], "Call DOI": r["call_doi"],
            "Call IV": r["call_iv"], "Call LTP": r["call_ltp"],
            "Strike": r["strike"], "Put LTP": r["put_ltp"],
            "Put IV": r["put_iv"], "Put DOI": r["put_doi"],
            "Put OI": r["put_oi"],
        } for r in chain["rows"]]
        st.dataframe(rows, use_container_width=True,
                     hide_index=True, height=300)

    st.subheader("View-to-Strategy Finder")
    results = finder.find(view, chain, top_n=3)
    if not results:
        st.warning("No strategies match. Try relaxing constraints.")
        return

    for i, r in enumerate(results, 1):
        with st.container(border=True):
            cols = st.columns([3, 1])
            with cols[0]:
                legs = " / ".join(
                    f"{'+' if d > 0 else '-'} {k.upper()} {strike} "
                    f"({'Buy' if d > 0 else 'Sell'})"
                    for k, d, strike in r["legs"])
                st.markdown(f"### #{i} {r['name']}")
                st.caption(legs)
            with cols[1]:
                st.metric("Fit", f"{r['fit']['total']:.0f}")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Net premium", f"{r['net_premium']:+.0f}")
            c2.metric("Max profit", r["risk"]["max_profit_label"])
            c3.metric("Max loss", r["risk"]["max_loss_label"])
            c4.metric("POP (model)",
                      f"{r['risk']['pop_model'] * 100:.0f}%")
            with st.expander("Fit Score breakdown"):
                st.json(r["fit"]["breakdown"])

    top = results[0]
    st.subheader(f"Risk Analyzer - {top['name']}")
    S = top["risk"]["spot_range"]
    pnl = top["risk"]["pnl"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=S, y=pnl, mode="lines", name="P&L",
        line=dict(color="steelblue", width=3)))
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    fig.add_vline(x=analysis["spot"], line_dash="dot",
                  line_color="black", annotation_text="Spot")
    fig.update_layout(title="Payoff at expiry (per unit)",
                      height=340, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### What-if scenario grid (per unit)")
    grid = risk.scenario_grid(top["strategy"], chain)
    z = [row for _, row in grid]
    y = [f"{ss * 100:+.0f}% spot" for ss, _ in grid]
    x = ["IV -5", "IV 0", "IV +5"]
    fig = go.Figure(data=go.Heatmap(
        z=z, x=x, y=y, colorscale="RdYlGn",
        text=z, texttemplate="%{text}"))
    fig.update_layout(height=260, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("AI Lens")
    ne = NarrativeEngine(use_llm=True)
    narrative = ne.regime_summary({
        "lean": analysis["lean"],
        "strength": analysis["strength"],
        "iv_percentile": int(analysis["iv_percentile"]),
        "confidence": analysis["confidence"],
        "flip": (f"a close beyond {analysis['call_wall']} "
                 f"or {analysis['put_wall']}"),
    })
    st.info(narrative["text"])
    st.caption(
        f"Source: {narrative['source']} - "
        f"Confidence: {narrative['confidence']}")
''',

"ui/project2.py": r'''"""Project 2 UI."""

import streamlit as st
import plotly.graph_objects as go

from project2_portfolio import analyzer, health_score, insights
from shared.narrative import NarrativeEngine


def render():
    st.title("Project 2 - AI Investment Assistant")
    a = analyzer.analyze()
    h = health_score.score(a)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total value", f"Rs {a['total']:,.0f}")
    c2.metric("Portfolio XIRR", f"{a['portfolio_xirr']:.2f}%", a["as_of"])
    c3.metric("HHI", f"{a['hhi']:.3f}")
    c4.metric("Health Score", f"{h['total']:.0f}/100", h["weakest"])

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Health Score breakdown")
        keys = list(h["breakdown"].keys())
        vals = list(h["breakdown"].values())
        colors = ["#2E75B6" if k != h["weakest"] else "#C0392B"
                  for k in keys]
        fig = go.Figure()
        fig.add_bar(x=keys, y=vals, marker_color=colors,
                    text=[f"{v:.0f}" for v in vals], textposition="auto")
        fig.update_layout(yaxis_range=[0, 100], height=340,
                          margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
        if h.get("placeholders"):
            st.caption("Placeholders: " + ", ".join(h["placeholders"]))
    with col2:
        st.subheader("Sector allocation")
        sectors = a["sectors"]
        fig = go.Figure(data=go.Pie(
            labels=list(sectors.keys()),
            values=list(sectors.values()), hole=0.4))
        fig.update_layout(height=340, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top holdings (direct vs look-through)")
    c1, c2 = st.columns(2)
    with c1:
        st.caption("Direct")
        st.table([{"Symbol": sym, "Weight": f"{w * 100:.1f}%",
                   "XIRR": f"{a['per_xirr'].get(sym, 0):.2f}%"}
                  for sym, w in a["top3"]])
    with c2:
        st.caption("Look-through")
        st.table([{"Symbol": sym, "Weight": f"{w * 100:.1f}%"}
                  for sym, w in (a.get("eff_top3") or [])])

    st.subheader("Insights")
    for card in insights.generate(a, h):
        with st.container(border=True):
            st.markdown(f"**{card['title']}** - priority {card['priority']}")
            st.caption(f"Why: {card['why']}")
            st.caption(f"Action: {card['action']}")

    st.subheader("AI Lens")
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
        })
    st.info(narrative["text"])
    st.caption(f"Source: {narrative['source']}")
''',

"ui/project3.py": r'''"""Project 3 UI."""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from project3_charts import data, indicators, trend, patterns, confluence
from shared.narrative import NarrativeEngine


@st.cache_data(ttl=600, show_spinner="Loading OHLCV data...")
def load_data(symbol: str, period: str):
    return data.fetch(symbol=symbol, period=period)


def render():
    st.title("Project 3 - AI Chart Intelligence")

    with st.sidebar:
        st.subheader("Chart settings")
        symbol = st.text_input("Symbol", value="RELIANCE.NS",
                               help="e.g. RELIANCE.NS, TCS.NS")
        period = st.selectbox("Period", ["1y", "2y", "6mo"], index=0)
        show_ma = st.checkbox("Moving averages", value=True)
        show_bb = st.checkbox("Bollinger Bands", value=False)
        show_st = st.checkbox("Supertrend", value=False)
        show_vwap = st.checkbox("VWAP", value=False)

    try:
        df = load_data(symbol, period)
    except Exception as e:
        st.error(f"Could not load {symbol}: {e}")
        return
    if df is None or len(df) < 30:
        st.error("Insufficient data.")
        return

    src = df.attrs.get("source", "unknown")
    df = indicators.compute_all(df)
    t = trend.classify(df)
    c = confluence.evaluate(df)
    pr = patterns.support_resistance(df)
    cs = patterns.candlesticks(df)
    last = df.iloc[-1]
    st.caption(f"Data source: {src}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Close", f"{last['close']:.2f}")
    c2.metric("Trend", t[0], f"{t[1]} strength")
    c3.metric("Confluence", f"{c['agreement']}/5", c["bias"])
    c4.metric("RSI", f"{last['rsi']:.1f}")

    st.subheader("Price chart")
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=("Price", "Volume", "RSI"))
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["open"], high=df["high"],
        low=df["low"], close=df["close"], name="Price"),
        row=1, col=1)
    if show_ma:
        for n, color in [(20, "orange"), (50, "blue"), (200, "purple")]:
            fig.add_trace(go.Scatter(
                x=df.index, y=df[f"sma{n}"], name=f"SMA{n}",
                line=dict(color=color, width=1)), row=1, col=1)
    if show_bb:
        fig.add_trace(go.Scatter(x=df.index, y=df["bb_upper"],
                                 name="BB upper",
                                 line=dict(color="rgba(150,150,150,0.6)")),
                      row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["bb_lower"],
                                 name="BB lower",
                                 line=dict(color="rgba(150,150,150,0.6)")),
                      row=1, col=1)
    if show_st:
        fig.add_trace(go.Scatter(x=df.index, y=df["supertrend"],
                                 name="Supertrend",
                                 line=dict(color="green", width=1.5)),
                      row=1, col=1)
    if show_vwap:
        fig.add_trace(go.Scatter(x=df.index, y=df["vwap"], name="VWAP",
                                 line=dict(color="darkorange", dash="dot")),
                      row=1, col=1)
    if pr["support"]:
        fig.add_hline(y=pr["support"], line_dash="dash", line_color="green",
                      annotation_text=f"Support {pr['support']}",
                      row=1, col=1)
    if pr["resistance"]:
        fig.add_hline(y=pr["resistance"], line_dash="dash",
                      line_color="red",
                      annotation_text=f"Resistance {pr['resistance']}",
                      row=1, col=1)
    colors = ["green" if c_ >= o_ else "red"
              for o_, c_ in zip(df["open"], df["close"])]
    fig.add_trace(go.Bar(x=df.index, y=df["volume"], name="Volume",
                         marker_color=colors, showlegend=False),
                  row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["rsi"], name="RSI",
                             line=dict(color="purple", width=1.5)),
                  row=3, col=1)
    fig.add_hline(y=70, line_dash="dot", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="green", row=3, col=1)
    fig.update_layout(height=760, xaxis_rangeslider_visible=False,
                      margin=dict(l=20, r=20, t=40, b=20),
                      legend=dict(orientation="h", y=1.06, x=0))
    fig.update_yaxes(range=[0, 100], row=3, col=1)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Confluence engine")
    col1, col2 = st.columns(2)
    with col1:
        g = c["groups"]
        vals = [1 if v > 0 else -1 if v < 0 else 0 for v in g.values()]
        colors = ["seagreen" if v > 0 else "firebrick" if v < 0 else "gray"
                  for v in vals]
        texts = ["+" if v > 0 else "-" if v < 0 else "0" for v in vals]
        fig = go.Figure(go.Bar(x=list(g.keys()), y=vals,
                               marker_color=colors,
                               text=texts, textposition="auto"))
        fig.update_layout(
            title=f"Bias: {c['bias']} ({c['strength']})",
            yaxis=dict(tickmode="array", tickvals=[-1, 0, 1],
                       ticktext=["Bearish", "Neutral", "Bullish"]),
            yaxis_range=[-1.4, 1.4], height=300,
            margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("**Indicator snapshot**")
        st.markdown(f"- **RSI(14):** {last['rsi']:.1f}")
        st.markdown(f"- **MACD hist:** {last['macd_hist']:+.3f}")
        st.markdown(f"- **ADX:** {last['adx']:.1f}")
        st.markdown(f"- **Supertrend:** "
                    f"{'up' if last['st_dir'] == 1 else 'down'}")
        vol_ratio = (last["volume"]
                     / df["volume"].rolling(20).mean().iloc[-1])
        st.markdown(f"- **Volume vs 20d:** {vol_ratio:.2f}x")
        if pr["support"]:
            st.markdown(f"- **Support:** {pr['support']}")
        if pr["resistance"]:
            st.markdown(f"- **Resistance:** {pr['resistance']}")

    if cs:
        st.subheader("Candlestick patterns (last 5 bars)")
        st.table([{"Pattern": p[0],
                   "Bar": str(df.index[p[1]].date()),
                   "Meaning": p[2]} for p in cs])
    else:
        st.caption("No candlestick patterns detected.")

    st.subheader("AI Lens")
    ne = NarrativeEngine(use_llm=True)
    narrative = ne.synthesize(
        "Bias is {bias} ({strength}). Trend groups aligned: "
        "{agree} of 5. Key resistance: {res}. Support: {sup}. "
        "Invalidation: close below {sup}.",
        {
            "bias": c["bias"], "strength": c["strength"],
            "agree": c["agreement"], "res": pr["resistance"],
            "sup": pr["support"], "confidence": c["strength"],
        })
    st.info(narrative["text"])
    st.caption(f"Source: {narrative['source']}")
''',
}


def main():
    created = 0
    for path_str, content in FILES.items():
        path = ROOT / path_str
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content.encode("utf-8"))
        print(f"  wrote {path.relative_to(ROOT)}")
        created += 1

    print()
    print(f"Created {created} files under {ROOT}")
    print()
    print("Next steps:")
    print("  1. pip install -r requirements.txt")
    print("  2. python -m streamlit run app.py     # works WITHOUT key")
    print("  3. python demo.py                     # CLI demos")
    print()
    print("To enable Gemini (optional):")
    print("  Copy .streamlit/secrets.toml.example -> .streamlit/secrets.toml")
    print("  Paste your key inside. That file is gitignored.")
    print()
    print("For GitHub + Streamlit Cloud:")
    print("  git add . && git status   # confirm secrets.toml is NOT listed")
    print("  git commit && git push")
    print("  Paste key in Streamlit Cloud dashboard -> Advanced -> Secrets")


if __name__ == "__main__":
    main()