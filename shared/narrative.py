"""Narrative engine: template fallback + Gemini REST API.

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
