# AI Trading Suite

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
