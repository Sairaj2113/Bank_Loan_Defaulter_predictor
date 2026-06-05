from __future__ import annotations

import streamlit as st

_CARD_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap');

.risk-result-wrap {
    background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
    border: 1px solid #d6e2f1;
    border-top: 4px solid #38bdf8;
    border-radius: 20px;
    padding: 24px;
    margin: 16px 0;
    position: relative;
    box-shadow: 0 18px 45px rgba(15, 23, 42, 0.06);
}

.risk-result-wrap::before {
    content: "LOAN DECISION SUMMARY";
    font-family: 'Manrope', sans-serif;
    font-size: 0.66rem;
    letter-spacing: 0.18em;
    color: #6b86a8;
    position: absolute;
    top: -10px;
    left: 20px;
    background: #ffffff;
    padding: 0 8px;
}

.risk-label {
    font-family: 'Manrope', sans-serif;
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #6b86a8;
    margin-bottom: 4px;
}

.risk-value-high,
.risk-value-medium,
.risk-value-low {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.5rem;
    font-weight: 700;
    line-height: 1.05;
}

.risk-value-high {
    color: #e85c70;
}

.risk-value-medium {
    color: #d97706;
}

.risk-value-low {
    color: #0f9f9a;
}

.risk-badge {
    display: inline-block;
    font-family: 'Manrope', sans-serif;
    font-size: 0.75rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    padding: 5px 12px;
    border-radius: 999px;
    margin-top: 4px;
}

.badge-high {
    background: #fff1f4;
    color: #c2415d;
    border: 1px solid #f5bcc6;
}

.badge-medium {
    background: #fff8ed;
    color: #b45309;
    border: 1px solid #f6d39b;
}

.badge-low {
    background: #ecfdf8;
    color: #0f766e;
    border: 1px solid #a7f3d0;
}

.risk-bar-track {
    height: 10px;
    background: #e5eef8;
    border-radius: 999px;
    margin: 16px 0 10px 0;
    overflow: hidden;
}

.risk-bar-fill-high {
    height: 100%;
    background: linear-gradient(90deg, #f59eb1, #e85c70);
    transition: width 0.6s ease;
}

.risk-bar-fill-medium {
    height: 100%;
    background: linear-gradient(90deg, #f6c27b, #d97706);
    transition: width 0.6s ease;
}

.risk-bar-fill-low {
    height: 100%;
    background: linear-gradient(90deg, #5eead4, #0f9f9a);
    transition: width 0.6s ease;
}

.recommendation-box {
    margin-top: 16px;
    padding: 14px 16px;
    border-left: 4px solid #38bdf8;
    background: #f4f8fd;
    border-radius: 14px;
    font-family: 'Manrope', sans-serif;
    font-size: 0.9rem;
    color: #334155;
    line-height: 1.55;
}

.recommendation-label {
    font-size: 0.68rem;
    letter-spacing: 0.14em;
    color: #1d4ed8;
    text-transform: uppercase;
    margin-bottom: 4px;
    font-weight: 700;
}

.factors-header {
    font-family: 'Manrope', sans-serif;
    font-size: 0.72rem;
    letter-spacing: 0.14em;
    color: #6b86a8;
    text-transform: uppercase;
    border-top: 1px solid #d6e2f1;
    padding-top: 16px;
    margin-top: 16px;
}

.factor-item {
    font-family: 'Manrope', sans-serif;
    font-size: 0.88rem;
    color: #4b5f7a;
    padding: 7px 0;
    border-bottom: 1px dotted #dbe6f3;
    letter-spacing: 0.01em;
}

.factor-item::before {
    content: "- ";
    color: #38bdf8;
    font-weight: 700;
}
</style>
"""


def _tier(probability: float, risk_category: str) -> str:
    category = (risk_category or "").upper()
    if "HIGH" in category or probability >= 0.60:
        return "high"
    if "LOW" in category or probability < 0.35:
        return "low"
    return "medium"


def render_prediction_result(result: dict, factors: list[str] | None = None) -> None:
    st.markdown(_CARD_CSS, unsafe_allow_html=True)
    factors = factors or []

    probability = float(result["probability_default"])
    risk_category = str(result["risk_category"])
    tier = _tier(probability, risk_category)
    pct = int(round(probability * 100))
    bar_class = f"risk-bar-fill-{tier}"
    val_class = f"risk-value-{tier}"
    badge_class = f"badge-{tier}"

    rec = result.get("recommendation", "REVIEW")

    factors_html = ""
    if factors:
        items_html = "".join(f'<div class="factor-item">{factor}</div>' for factor in factors)
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
      <div class="recommendation-box">
        <div class="recommendation-label">Recommendation</div>
        {rec}
      </div>
      {factors_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
