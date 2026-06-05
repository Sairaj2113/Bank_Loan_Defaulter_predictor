from __future__ import annotations

import sys
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

PACKAGE_ROOT = Path(__file__).resolve().parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from components.customer_table import customer_display_label, render_customer_table
from components.prediction_card import render_prediction_result
from components.sidebar import render_navigation
from utils.api_client import get_customer, get_customers, get_predictions, predict_customer

APP_USERNAME = "bankadmin"
APP_PASSWORD = "admin123"

BG = "#f7fbff"
SURFACE = "#ffffff"
SURFACE_ALT = "#eef5ff"
BORDER = "#d7e3f3"
TEXT = "#213047"
MUTED = "#5c6f89"
PRIMARY = "#2f6fed"
PRIMARY_SOFT = "#dbeafe"
SECONDARY = "#14b8a6"
SECONDARY_SOFT = "#def7f3"
WARNING = "#f59e0b"
SUCCESS = "#0f9f9a"
RISK = "#e85c70"
VIOLET = "#7c8cff"
GOLD = "#f6b64c"

_GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at top left, rgba(47, 111, 237, 0.08), transparent 30%),
        radial-gradient(circle at bottom right, rgba(20, 184, 166, 0.08), transparent 28%),
        linear-gradient(180deg, #f8fbff 0%, #f2f7ff 100%) !important;
    color: #213047 !important;
    font-family: 'Manrope', sans-serif !important;
}

[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] h4,
[data-testid="stAppViewContainer"] h5,
[data-testid="stAppViewContainer"] h6,
[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] li,
[data-testid="stAppViewContainer"] label,
[data-testid="stAppViewContainer"] span,
[data-testid="stAppViewContainer"] div {
    color: #213047;
}

[data-testid="stHeader"] {
    background: rgba(248, 251, 255, 0.82) !important;
    backdrop-filter: blur(10px);
    border-bottom: 1px solid #d7e3f3 !important;
}

[data-testid="stToolbar"] {
    visibility: hidden;
}

.hero-banner {
    background: linear-gradient(135deg, #ffffff 0%, #eff7ff 54%, #eefcf9 100%);
    border: 1px solid #d7e3f3;
    border-radius: 24px;
    padding: 26px 30px;
    margin-bottom: 22px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 18px 45px rgba(15, 23, 42, 0.06);
}

.hero-banner::after {
    content: "";
    position: absolute;
    inset: 0;
    background:
        radial-gradient(circle at top right, rgba(56, 189, 248, 0.16), transparent 24%),
        radial-gradient(circle at bottom left, rgba(20, 184, 166, 0.12), transparent 26%);
    pointer-events: none;
}

.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.05rem;
    font-weight: 700;
    color: #16325c;
    letter-spacing: 0.01em;
    margin: 0 0 6px 0;
}

.hero-title span {
    color: #2f6fed;
}

.hero-sub {
    font-family: 'Manrope', sans-serif;
    font-size: 0.95rem;
    color: #56708f;
    line-height: 1.5;
    max-width: 760px;
}

.hero-status {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-family: 'Manrope', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #1d4ed8;
    background: #ecf5ff;
    border: 1px solid #bfd8ff;
    border-radius: 999px;
    padding: 7px 14px;
    margin-top: 14px;
}

.hero-status::before {
    content: "";
    width: 8px;
    height: 8px;
    border-radius: 999px;
    background: linear-gradient(135deg, #38bdf8, #14b8a6);
    box-shadow: 0 0 0 4px rgba(56, 189, 248, 0.12);
}

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 14px;
    margin-bottom: 22px;
}

.kpi-card {
    background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
    border: 1px solid #d7e3f3;
    border-radius: 20px;
    padding: 18px 18px 16px 18px;
    box-shadow: 0 12px 32px rgba(15, 23, 42, 0.05);
    position: relative;
    overflow: hidden;
}

.kpi-card::before {
    content: "";
    position: absolute;
    inset: 0 auto 0 0;
    width: 4px;
    background: linear-gradient(180deg, #38bdf8 0%, #14b8a6 100%);
}

.kpi-label {
    font-family: 'Manrope', sans-serif;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #6b86a8;
    margin-bottom: 8px;
}

.kpi-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #16325c;
    line-height: 1.05;
}

.kpi-note {
    margin-top: 6px;
    font-size: 0.85rem;
    color: #5d718d;
}

.section-head {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #36557d;
    border-left: 4px solid #38bdf8;
    padding-left: 12px;
    margin: 18px 0 12px 0;
}

.ind-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, #d7e3f3 16%, #d7e3f3 84%, transparent 100%);
    margin: 28px 0;
}

div[data-testid="metric-container"] {
    background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%) !important;
    border: 1px solid #d7e3f3 !important;
    border-radius: 18px !important;
    padding: 16px 18px !important;
    box-shadow: 0 12px 30px rgba(15, 23, 42, 0.05) !important;
}

div[data-testid="metric-container"] label {
    font-family: 'Manrope', sans-serif !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: #6b86a8 !important;
}

div[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    color: #5c6f89 !important;
    opacity: 1 !important;
}

div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    color: #16325c !important;
}

.stTextInput input,
.stNumberInput input,
.stSelectbox select,
[data-baseweb="select"] [role="combobox"],
[data-baseweb="input"] input {
    background: #ffffff !important;
    border: 1px solid #cfddee !important;
    color: #213047 !important;
    font-family: 'Manrope', sans-serif !important;
    border-radius: 14px !important;
}

.stSelectbox [data-baseweb="select"] {
    border: none !important;
    box-shadow: none !important;
}

.stSelectbox [data-baseweb="select"] > div {
    background: #ffffff !important;
    border: 1px solid #cfddee !important;
    border-radius: 14px !important;
    box-shadow: none !important;
}

.stSelectbox [data-baseweb="select"] svg {
    fill: #2f6fed !important;
    color: #2f6fed !important;
    opacity: 1 !important;
}

.stSelectbox [data-baseweb="select"] [role="combobox"] {
    background: #ffffff !important;
    border: 1px solid #cfddee !important;
    box-shadow: none !important;
}

.stSelectbox [data-baseweb="select"] [role="option"] {
    border: none !important;
    box-shadow: none !important;
}

.stTextInput input:focus,
.stNumberInput input:focus,
[data-baseweb="input"] input:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.14) !important;
}

.stButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #2f6fed 0%, #14b8a6 100%) !important;
    color: #ffffff !important;
    border: none !important;
    font-family: 'Manrope', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    border-radius: 14px !important;
    padding: 10px 18px !important;
    box-shadow: 0 12px 30px rgba(47, 111, 237, 0.18) !important;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    filter: brightness(1.02);
    box-shadow: 0 16px 34px rgba(47, 111, 237, 0.22) !important;
}

.stAlert {
    border-radius: 16px !important;
    font-family: 'Manrope', sans-serif !important;
}

div[data-testid="stAlert"] {
    background: #f8fbff !important;
    border: 1px solid #d7e3f3 !important;
    color: #213047 !important;
}

div[data-testid="stAlert"] * {
    color: #213047 !important;
}

.stCaption {
    font-family: 'Manrope', sans-serif !important;
    color: #33465e !important;
}

.login-plate {
    max-width: 500px;
    margin: 78px auto 28px auto;
    background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
    border: 1px solid #d7e3f3;
    border-radius: 24px;
    padding: 38px 38px 30px 38px;
    position: relative;
    box-shadow: 0 20px 45px rgba(15, 23, 42, 0.06);
}

.login-plate::before {
    content: "SECURE ACCESS";
    font-family: 'Manrope', sans-serif;
    font-size: 0.66rem;
    letter-spacing: 0.2em;
    color: #6b86a8;
    position: absolute;
    top: -10px;
    left: 20px;
    background: #f8fbff;
    padding: 0 8px;
}

.login-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: #16325c;
    letter-spacing: 0.02em;
    margin: 0 0 6px 0;
}

.login-title span {
    color: #2f6fed;
}

.login-sub {
    font-family: 'Manrope', sans-serif;
    font-size: 0.9rem;
    color: #56708f;
    margin-bottom: 24px;
    line-height: 1.5;
}

.insight-card {
    background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
    border: 1px solid #d7e3f3;
    border-radius: 20px;
    padding: 18px;
    box-shadow: 0 12px 30px rgba(15, 23, 42, 0.05);
}

.insight-card h4 {
    font-family: 'Space Grotesk', sans-serif;
    margin: 0 0 8px 0;
    color: #16325c;
}

.insight-card p {
    margin: 0;
    color: #56708f;
    line-height: 1.55;
}
</style>
"""


def _apply_chart_theme() -> None:
    mpl.rcParams.update(
        {
            "figure.facecolor": BG,
            "axes.facecolor": SURFACE,
            "axes.edgecolor": BORDER,
            "axes.labelcolor": MUTED,
            "axes.titlecolor": TEXT,
            "axes.titlesize": 11,
            "axes.titleweight": "bold",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "text.color": TEXT,
            "grid.color": BORDER,
            "grid.linestyle": "--",
            "font.family": "DejaVu Sans",
            "figure.dpi": 110,
        }
    )


def _safe_text(value: object, fallback: str = "Unknown") -> str:
    if value is None:
        return fallback
    text_value = str(value).strip()
    return text_value if text_value else fallback


def _format_currency(value: object) -> str:
    try:
        return f"Rs. {float(value):,.0f}"
    except (TypeError, ValueError):
        return "Rs. 0"


def _format_percent(value: object) -> str:
    try:
        return f"{float(value) * 100:.1f}%"
    except (TypeError, ValueError):
        return "0.0%"


def _format_bool(value: object) -> str:
    return "Yes" if bool(value) else "No"


def _asset_label(item: dict) -> str:
    owns_car = bool(item.get("owns_car"))
    owns_realty = bool(item.get("owns_realty"))
    if owns_car and owns_realty:
        return "Car and home"
    if owns_car:
        return "Car"
    if owns_realty:
        return "Home"
    return "No registered assets"


def customer_detail_frame(customer: dict) -> pd.DataFrame:
    rows = [
        ("Customer ID", _safe_text(customer.get("customer_id"))),
        ("Gender", _safe_text(customer.get("gender"))),
        ("Education", _safe_text(customer.get("education_type"))),
        ("Family status", _safe_text(customer.get("family_status"))),
        ("Housing", _safe_text(customer.get("housing_type"))),
        ("Occupation", _safe_text(customer.get("occupation_type"))),
        ("Income", _format_currency(customer.get("income_total"))),
        ("Children", int(customer.get("cnt_children", 0) or 0)),
        ("Family members", int(customer.get("family_members", 0) or 0)),
        ("Owns car", _format_bool(customer.get("owns_car"))),
        ("Owns home", _format_bool(customer.get("owns_realty"))),
        ("Assets", _asset_label(customer)),
    ]
    return pd.DataFrame(rows, columns=["Field", "Value"])


def application_history_frame(items: list[dict]) -> pd.DataFrame:
    if not items:
        return pd.DataFrame(columns=["Application date", "Loan type", "Credit amount", "Annuity", "Goods price", "Status"])

    rows = []
    for item in items:
        rows.append(
            {
                "Application date": _safe_text(item.get("application_date")),
                "Loan type": _safe_text(item.get("loan_type")),
                "Credit amount": _format_currency(item.get("credit_amount")),
                "Annuity": _format_currency(item.get("annuity_amount")),
                "Goods price": _format_currency(item.get("goods_price")),
                "Status": _safe_text(item.get("status")),
            }
        )
    return pd.DataFrame(rows)


def prediction_history_frame(items: list[dict]) -> pd.DataFrame:
    if not items:
        return pd.DataFrame(columns=["Predicted at", "Risk", "Probability", "Loan type", "Credit amount"])

    rows = []
    for item in items:
        rows.append(
            {
                "Predicted at": _safe_text(item.get("predicted_at")),
                "Risk": _safe_text(item.get("risk_category")),
                "Probability": _format_percent(item.get("probability_default")),
                "Loan type": _safe_text(item.get("loan_type")),
                "Credit amount": _format_currency(item.get("credit_amount")),
            }
        )
    return pd.DataFrame(rows)


def prediction_list_frame(items: list[dict]) -> pd.DataFrame:
    if not items:
        return pd.DataFrame(columns=["Risk", "Probability", "Loan type", "Credit amount", "Predicted at"])

    rows = []
    for item in items:
        rows.append(
            {
                "Risk": _safe_text(item.get("risk_category")),
                "Probability": _format_percent(item.get("probability_default")),
                "Loan type": _safe_text(item.get("loan_type")),
                "Credit amount": _format_currency(item.get("credit_amount")),
                "Predicted at": _safe_text(item.get("predicted_at")),
            }
        )
    return pd.DataFrame(rows)


def safe_frame(items: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(items) if items else pd.DataFrame()


def fetch_all_predictions(max_rows: int = 1000) -> pd.DataFrame:
    collected: list[dict] = []
    page_size = 100
    for offset in range(0, max_rows, page_size):
        response = get_predictions(limit=page_size, offset=offset)
        items = response.get("items", [])
        if not items:
            break
        collected.extend(items)
        if len(items) < page_size:
            break
    return safe_frame(collected)


def build_risk_factors(customer: dict, application: dict, probability: float) -> list[str]:
    factors: list[str] = []
    income = float(customer.get("income_total", 0) or 0)
    credit = float(application.get("credit_amount", 0) or 0)
    annuity = float(application.get("annuity_amount", 0) or 0)
    family_members = int(customer.get("family_members", 1) or 1)
    owns_assets = bool(customer.get("owns_car")) or bool(customer.get("owns_realty"))

    if income and credit / income > 3:
        factors.append("Requested credit is high compared with household income")
    if income and annuity / income > 0.3:
        factors.append("Monthly repayment may feel heavy for this income range")
    if income < 120_000:
        factors.append("Household income is below the stronger-risk threshold")
    if family_members >= 4:
        factors.append("Larger household size can add repayment pressure")
    if not owns_assets:
        factors.append("No registered car or home ownership on file")
    if probability >= 0.7:
        factors.append("Current score leans toward higher default risk")
    elif probability >= 0.35:
        factors.append("Current score sits in a moderate risk zone")
    else:
        factors.append("Current score indicates a steadier repayment profile")

    return factors[:4]


def render_kpi_cards(customers: dict, predictions: dict) -> None:
    customer_frame = safe_frame(customers.get("items", []))
    prediction_frame = safe_frame(predictions.get("items", []))

    total_customers = int(customers.get("total", 0) or 0)
    total_predictions = int(predictions.get("total", 0) or 0)
    avg_income = pd.to_numeric(customer_frame.get("income_total", pd.Series(dtype=float)), errors="coerce").mean()
    avg_income = float(0 if pd.isna(avg_income) else avg_income)
    avg_prob = pd.to_numeric(prediction_frame.get("probability_default", pd.Series(dtype=float)), errors="coerce").mean()
    avg_prob = float(0 if pd.isna(avg_prob) else avg_prob)
    high_risk = int((prediction_frame.get("risk_category", pd.Series(dtype=str)) == "HIGH_RISK").sum()) if not prediction_frame.empty else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Customers Reviewed", f"{total_customers:,}")
    with c2:
        st.metric("Predictions Recorded", f"{total_predictions:,}")
    with c3:
        st.metric("Average Income", _format_currency(avg_income))
    with c4:
        st.metric("Average Risk", _format_percent(avg_prob))
    with c5:
        st.metric("High Risk Cases", f"{high_risk:,}")


def render_workflow_panel() -> None:
    st.info(
        """
        **Workflow**
        1. Open **Make Prediction** and pick a customer profile.
        2. Enter the loan amount, repayment amount, goods price, and loan type.
        3. Run the review to see the default probability and recommendation.
        4. Check the saved results on **Predictions** and **Analytics**.
        """
    )


def render_how_to_use_page() -> None:
    st.markdown('<div class="section-head">How to Use</div>', unsafe_allow_html=True)
    st.info(
        """
        **Step-by-step**
        1. Open **Make Prediction** from the sidebar.
        2. Choose a customer profile from the list.
        3. Fill in the loan amount, repayment amount, goods price, and loan type.
        4. Press **Calculate Risk** to generate the default probability.
        5. Review the summary card and the saved prediction history.
        """
    )
    render_workflow_panel()


def render_bar(frame: pd.DataFrame, column: str, title: str, color: str = PRIMARY) -> None:
    _apply_chart_theme()
    if frame.empty or column not in frame.columns:
        st.info(f"No data for {title.lower()}.")
        return

    counts = frame[column].fillna("Unknown").astype(str).value_counts().head(8)
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    counts.sort_values().plot(kind="barh", ax=ax, color=color)
    ax.set_title(title, pad=10)
    ax.set_xlabel("Count")
    ax.tick_params(axis="y", labelsize=8)
    ax.grid(axis="x", alpha=0.18)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
    ax.spines["left"].set_edgecolor(color)
    ax.spines["left"].set_linewidth(2)
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)


def render_histogram(frame: pd.DataFrame, column: str, title: str, color: str = SECONDARY) -> None:
    _apply_chart_theme()
    if frame.empty or column not in frame.columns:
        st.info(f"No data for {title.lower()}.")
        return

    values = pd.to_numeric(frame[column], errors="coerce").dropna()
    if values.empty:
        st.info(f"No numeric values for {title.lower()}.")
        return

    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    ax.hist(values, bins=18, color=color, edgecolor="#ffffff", alpha=0.9, linewidth=0.8)
    ax.set_title(title, pad=10)
    ax.set_xlabel(column.replace("_", " ").title())
    ax.set_ylabel("Frequency")
    ax.grid(axis="y", alpha=0.18)
    ax.spines["bottom"].set_edgecolor(color)
    ax.spines["bottom"].set_linewidth(2)
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)


def render_prediction_distribution(prediction_frame: pd.DataFrame) -> None:
    _apply_chart_theme()
    if prediction_frame.empty or "risk_category" not in prediction_frame.columns:
        st.info("No prediction data available yet.")
        return

    counts = prediction_frame["risk_category"].fillna("UNKNOWN").value_counts()
    fig, ax = plt.subplots(figsize=(5.4, 3.8))
    wedge_colors = ["#14b8a6", "#f59e0b", "#e85c70"]
    wedges, texts, autotexts = ax.pie(
        counts,
        labels=counts.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=wedge_colors[: len(counts)],
        wedgeprops={"edgecolor": "#ffffff", "linewidth": 2},
    )
    for text in texts:
        text.set_fontsize(8)
        text.set_color(TEXT)
    for text in autotexts:
        text.set_fontsize(8)
        text.set_color("#213047")
        text.set_fontweight("bold")
    ax.set_title("Risk Category Share", pad=10)
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)


def render_probability_trend(prediction_frame: pd.DataFrame) -> None:
    _apply_chart_theme()
    if prediction_frame.empty or "probability_default" not in prediction_frame.columns:
        st.info("No trend data yet.")
        return

    values = pd.to_numeric(prediction_frame["probability_default"], errors="coerce").dropna()
    if values.empty:
        st.info("No trend data yet.")
        return

    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    ax.fill_between(range(1, len(values) + 1), values * 100, alpha=0.12, color=VIOLET)
    ax.plot(range(1, len(values) + 1), values * 100, linewidth=2, color=VIOLET, marker="o", markersize=3)
    ax.axhline(y=50, color=RISK, linewidth=0.9, linestyle="--", alpha=0.55, label="50% threshold")
    ax.set_title("Prediction Probability Trend", pad=10)
    ax.set_xlabel("Prediction Index")
    ax.set_ylabel("Default Probability (%)")
    ax.set_ylim(0, max(100, float(values.max() * 100) + 5))
    ax.legend(fontsize=7, framealpha=0, labelcolor=MUTED)
    ax.grid(alpha=0.14)
    ax.spines["left"].set_edgecolor(VIOLET)
    ax.spines["left"].set_linewidth(2)
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)


def login_screen() -> None:
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)
    st.markdown(
        """
        <div class="login-plate">
          <div class="login-title">Bank <span>Loan</span> Insight</div>
          <div class="login-sub">Secure customer review workspace for loan checks and predictions.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Authenticate")

    if submitted:
        if username == APP_USERNAME and password == APP_PASSWORD:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Access denied. Invalid credentials.")


def render_dashboard_page(customers: dict, predictions: dict) -> None:
    customer_frame = safe_frame(customers.get("items", []))
    prediction_frame = safe_frame(predictions.get("items", []))

    render_kpi_cards(customers, predictions)

    st.markdown('<div class="ind-divider"></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-head">Household Mix</div>', unsafe_allow_html=True)
        render_bar(customer_frame, "gender", "Customer Gender Mix", color=PRIMARY)
    with c2:
        st.markdown('<div class="section-head">Income Spread</div>', unsafe_allow_html=True)
        render_histogram(customer_frame, "income_total", "Income Distribution", color=SECONDARY)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-head">Education Mix</div>', unsafe_allow_html=True)
        render_bar(customer_frame, "education_type", "Education Type", color=GOLD)
    with c2:
        st.markdown('<div class="section-head">Occupation Mix</div>', unsafe_allow_html=True)
        render_bar(customer_frame, "occupation_type", "Occupation Type", color=VIOLET)

    st.markdown('<div class="ind-divider"></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-head">Risk Breakdown</div>', unsafe_allow_html=True)
        render_prediction_distribution(prediction_frame)
    with c2:
        st.markdown('<div class="section-head">Probability Trend</div>', unsafe_allow_html=True)
        render_probability_trend(prediction_frame)

    st.markdown('<div class="ind-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-head">Customer Registry</div>', unsafe_allow_html=True)
    render_customer_table(customers.get("items", []))

    st.markdown('<div class="section-head">Recent Predictions</div>', unsafe_allow_html=True)
    if not prediction_frame.empty:
        st.dataframe(prediction_list_frame(prediction_frame.to_dict("records")), use_container_width=True, hide_index=True)
    else:
        st.info("No predictions stored yet.")


def render_customers_page(customers: dict) -> str | None:
    st.markdown('<div class="section-head">Customer Search</div>', unsafe_allow_html=True)
    search = st.text_input("Search customers", value="", placeholder="Search by gender, occupation, education, family, or housing")
    st.caption("Browse the customer profiles that match your search.")

    filtered = get_customers(query=search or None, limit=100, offset=0)
    render_customer_table(filtered.get("items", []))

    items = filtered.get("items", [])
    if not items:
        return None

    selected_index = st.selectbox(
        "Select a customer profile",
        options=list(range(len(items))),
        format_func=lambda index: customer_display_label(items[index]),
    )
    return str(items[int(selected_index)]["customer_id"])


def render_customer_detail_page(customer_id: str | None, predictions: dict | None = None) -> None:
    choices = get_customers(limit=100, offset=0).get("items", [])
    if not choices:
        st.warning("No customer rows found. Seed the customer list first.")
        return

    if customer_id is None:
        customer_id = str(choices[0]["customer_id"])

    selected = get_customer(customer_id)
    customer = selected["customer"]

    left, right = st.columns([1, 1.05])

    with left:
        st.markdown('<div class="section-head">Customer Profile</div>', unsafe_allow_html=True)
        st.dataframe(customer_detail_frame(customer), use_container_width=True, hide_index=True)

        st.markdown('<div class="section-head">Recent Applications</div>', unsafe_allow_html=True)
        application_frame = application_history_frame(selected.get("recent_applications", []))
        if application_frame.empty:
            st.info("No recent applications yet.")
        else:
            st.dataframe(application_frame, use_container_width=True, hide_index=True)

        st.markdown('<div class="section-head">Previous Predictions</div>', unsafe_allow_html=True)
        prediction_frame = prediction_history_frame(selected.get("recent_predictions", []))
        if prediction_frame.empty and predictions:
            prediction_frame = prediction_history_frame(
                [item for item in predictions.get("items", []) if str(item.get("customer_id")) == str(customer_id)]
            )
        if prediction_frame.empty:
            st.info("No previous predictions yet.")
        else:
            st.dataframe(prediction_frame, use_container_width=True, hide_index=True)

    with right:
        st.markdown('<div class="section-head">Make Prediction</div>', unsafe_allow_html=True)
        st.caption("Adjust the loan details to review the current customer profile.")
        defaults = {
            "credit_amount": 227_520.0,
            "annuity_amount": 13_189.5,
            "goods_price": 180_000.0,
            "loan_type": "Cash loans",
        }
        with st.form("risk_form"):
            credit_amount = st.number_input("Credit Amount", min_value=1.0, value=defaults["credit_amount"], step=1000.0)
            annuity_amount = st.number_input("Annuity Amount", min_value=1.0, value=defaults["annuity_amount"], step=100.0)
            goods_price = st.number_input("Goods Price", min_value=1.0, value=defaults["goods_price"], step=1000.0)
            loan_type = st.selectbox("Loan Type", ["Cash loans", "Revolving loans", "Consumer loans"])
            calculate = st.form_submit_button("Calculate Risk")

        if calculate:
            payload = {
                "credit_amount": credit_amount,
                "annuity_amount": annuity_amount,
                "goods_price": goods_price,
                "loan_type": loan_type,
            }
            result = predict_customer(customer_id, payload)
            factors = build_risk_factors(customer, payload, float(result["probability_default"]))
            render_prediction_result(result, factors)


def render_predictions_page() -> None:
    st.markdown('<div class="section-head">All Stored Predictions</div>', unsafe_allow_html=True)
    predictions = get_predictions(limit=100, offset=0)
    items = predictions.get("items", [])
    if not items:
        st.info("No predictions stored yet.")
        return
    st.dataframe(prediction_list_frame(items), use_container_width=True, hide_index=True)


def render_analytics_page() -> None:
    st.markdown('<div class="section-head">Prediction Analytics</div>', unsafe_allow_html=True)
    predictions = fetch_all_predictions()
    if predictions.empty:
        st.info("Run a few risk checks first to populate analytics.")
        return

    avg_prob = pd.to_numeric(predictions["probability_default"], errors="coerce").mean()
    avg_prob = float(0 if pd.isna(avg_prob) else avg_prob)
    high_risk = int((predictions["risk_category"] == "HIGH_RISK").sum())

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Average Default Probability", _format_percent(avg_prob))
    with c2:
        st.metric("High Risk Cases", f"{high_risk:,}")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-head">Risk Category Distribution</div>', unsafe_allow_html=True)
        render_prediction_distribution(predictions)
    with c2:
        st.markdown('<div class="section-head">Probability Histogram</div>', unsafe_allow_html=True)
        render_histogram(predictions, "probability_default", "Default Probability Distribution", color=RISK)


def main() -> None:
    st.set_page_config(
        page_title="Bank Loan Insight",
        page_icon="L",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)

    if not st.session_state.get("authenticated"):
        login_screen()
        return

    st.markdown(
        """
        <div class="hero-banner">
          <div class="hero-title">Bank <span>Loan</span> Insight</div>
          <div class="hero-sub">Personal customer reviews, loan checks, and prediction summaries in one calm, easy-to-read workspace.</div>
          <div class="hero-status">Live workspace ready</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = render_navigation()

    try:
        customers = get_customers(limit=100, offset=0)
        predictions = get_predictions(limit=100, offset=0)
    except Exception:
        st.error("We could not load the latest customer and prediction records right now.")
        return

    if page == "Dashboard":
        render_dashboard_page(customers, predictions)
    elif page == "Customers":
        render_customers_page(customers)
    elif page == "Make Prediction":
        selected = render_customers_page(customers)
        st.markdown('<div class="ind-divider"></div>', unsafe_allow_html=True)
        render_customer_detail_page(selected, predictions)
    elif page == "Predictions":
        render_predictions_page()
    elif page == "Analytics":
        render_analytics_page()
    elif page == "How to Use":
        render_how_to_use_page()


if __name__ == "__main__":
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.username = ""
    main()
