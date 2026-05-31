from __future__ import annotations

import streamlit as st

_CARD_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700&family=Share+Tech+Mono&display=swap');

.risk-result-wrap {
    background: #0d1117;
    border: 1px solid #1f2937;
    border-top: 3px solid #f59e0b;
    border-radius: 4px;
    padding: 24px;
    margin: 16px 0;
    position: relative;
}

.risk-result-wrap::before {
    content: "RISK ASSESSMENT REPORT";
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.2em;
    color: #4b5563;
    position: absolute;
    top: -10px;
    left: 20px;
    background: #0d1117;
    padding: 0 6px;
}

.risk-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #6b7280;
    margin-bottom: 4px;
}

.risk-value-high {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.4rem;
    font-weight: 700;
    color: #ef4444;
    line-height: 1.1;
}

.risk-value-medium {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.4rem;
    font-weight: 700;
    color: #f59e0b;
    line-height: 1.1;
}

.risk-value-low {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.4rem;
    font-weight: 700;
    color: #22c55e;
    line-height: 1.1;
}

.risk-badge {
    display: inline-block;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 2px;
    margin-top: 4px;
}

.badge-high   { background: #450a0a; color: #ef4444; border: 1px solid #ef4444; }
.badge-medium { background: #451a03; color: #f59e0b; border: 1px solid #f59e0b; }
.badge-low    { background: #052e16; color: #22c55e; border: 1px solid #22c55e; }

.risk-bar-track {
    height: 8px;
    background: #1f2937;
    border-radius: 0;
    margin: 16px 0 10px 0;
    overflow: hidden;
    position: relative;
}

.risk-bar-fill-high   { height: 100%; background: linear-gradient(90deg, #7f1d1d, #ef4444); transition: width 0.6s ease; }
.risk-bar-fill-medium { height: 100%; background: linear-gradient(90deg, #78350f, #f59e0b); transition: width 0.6s ease; }
.risk-bar-fill-low    { height: 100%; background: linear-gradient(90deg, #14532d, #22c55e); transition: width 0.6s ease; }

.model-tag {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: #374151;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 8px;
}

.recommendation-box {
    margin-top: 16px;
    padding: 12px 16px;
    border-left: 3px solid #f59e0b;
    background: #111827;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
    color: #d1d5db;
    letter-spacing: 0.04em;
}

.recommendation-label {
    font-size: 0.65rem;
    letter-spacing: 0.14em;
    color: #f59e0b;
    text-transform: uppercase;
    margin-bottom: 4px;
}

.factors-header {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.14em;
    color: #6b7280;
    text-transform: uppercase;
    border-top: 1px solid #1f2937;
    padding-top: 16px;
    margin-top: 16px;
}

.factor-item {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
    color: #9ca3af;
    padding: 5px 0;
    border-bottom: 1px dotted #1f2937;
    letter-spacing: 0.02em;
}

.factor-item::before {
    content: "▸ ";
    color: #f59e0b;
}
</style>
"""


def _tier(probability: float, risk_category: str) -> str:
    cat = (risk_category or "").upper()
    if "HIGH" in cat or probability >= 0.60:
        return "high"
    elif "LOW" in cat or probability < 0.35:
        return "low"
    return "medium"


def render_prediction_result(result: dict, factors: list[str] | None = None) -> None:
    st.markdown(_CARD_CSS, unsafe_allow_html=True)
    factors = factors or []

    probability = float(result["probability_default"])
    risk_category = result["risk_category"]
    tier = _tier(probability, risk_category)
    pct = int(probability * 100)
    bar_class = f"risk-bar-fill-{tier}"
    val_class = f"risk-value-{tier}"
    badge_class = f"badge-{tier}"

    rec = result.get("recommendation", "REVIEW")
    model_ver = result.get("model_version", "unknown")

    factors_html = ""
    if factors:
        items_html = "".join(f'<div class="factor-item">{f}</div>' for f in factors)
        factors_html = f'<div class="factors-header">Top Risk Factors</div>{items_html}'

    html = f"""
    <div class="risk-result-wrap">
      <div style="display:flex;gap:48px;align-items:flex-start;flex-wrap:wrap;">
        <div>
          <div class="risk-label">Default Probability</div>
          <div class="{val_class}">{pct}%</div>
        </div>
        <div>
          <div class="risk-label">Risk Category</div>
          <div style="margin-top:6px;"><span class="risk-badge {badge_class}">{risk_category}</span></div>
        </div>
      </div>
      <div class="risk-bar-track">
        <div class="{bar_class}" style="width:{pct}%;"></div>
      </div>
      <div class="model-tag">Model · {model_ver}</div>
      <div class="recommendation-box">
        <div class="recommendation-label">Recommendation</div>
        {rec}
      </div>
      {factors_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)