from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from frontend.components.customer_table import render_customer_table
from frontend.components.prediction_card import render_prediction_result
from frontend.components.sidebar import render_navigation
from frontend.utils.api_client import (
    get_customer, get_customers, get_db_health,
    get_health, get_model_info, get_predictions, predict_customer,
)

APP_USERNAME = "bankadmin"
APP_PASSWORD = "admin123"

# ─── Industrial colour palette ────────────────────────────────────────────────
STEEL   = "#0d1117"
PLATE   = "#111827"
GIRDER  = "#1f2937"
RIVET   = "#374151"
GHOST   = "#6b7280"
SILVER  = "#9ca3af"
LIGHT   = "#d1d5db"
AMBER   = "#f59e0b"
AMBER_D = "#78350f"
RED     = "#ef4444"
GREEN   = "#22c55e"
VIOLET  = "#a78bfa"

_GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Share+Tech+Mono&family=Barlow:wght@300;400;600&display=swap');

/* Base */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0d1117 !important;
    color: #d1d5db !important;
    font-family: 'Barlow', sans-serif !important;
}

[data-testid="stHeader"] { background: #0a0a0a !important; border-bottom: 1px solid #1f2937 !important; }

/* Hero banner */
.hero-banner {
    background: #0a0a0a;
    border: 1px solid #1f2937;
    border-top: 3px solid #f59e0b;
    border-radius: 4px;
    padding: 24px 32px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.hero-banner::after {
    content: "";
    position: absolute;
    top: 0; right: 0; bottom: 0;
    width: 220px;
    background: repeating-linear-gradient(
        -45deg,
        transparent, transparent 8px,
        rgba(245,158,11,0.04) 8px, rgba(245,158,11,0.04) 10px
    );
    pointer-events: none;
}
.hero-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.9rem;
    font-weight: 700;
    color: #f5f5f5;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin: 0 0 4px 0;
}
.hero-title span { color: #f59e0b; }
.hero-sub {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    color: #6b7280;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}
.hero-status {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.1em;
    color: #22c55e;
    background: #052e16;
    border: 1px solid #166534;
    border-radius: 2px;
    padding: 3px 10px;
    margin-top: 10px;
}

/* KPI cards */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
    margin-bottom: 24px;
}
.kpi-card {
    background: #0a0a0a;
    border: 1px solid #1f2937;
    border-bottom: 2px solid #f59e0b;
    border-radius: 4px;
    padding: 16px 18px;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: #f59e0b;
    opacity: 0.3;
}
.kpi-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #6b7280;
    margin-bottom: 6px;
}
.kpi-value {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.9rem;
    font-weight: 700;
    color: #f5f5f5;
    line-height: 1;
}
.kpi-value.amber { color: #f59e0b; }
.kpi-value.red   { color: #ef4444; }
.kpi-value.green { color: #22c55e; }

/* Section headers */
.section-head {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #9ca3af;
    border-left: 3px solid #f59e0b;
    padding-left: 10px;
    margin: 20px 0 12px 0;
}

/* Divider */
.ind-divider {
    height: 1px;
    background: repeating-linear-gradient(
        90deg,
        #1f2937 0px, #1f2937 8px,
        transparent 8px, transparent 14px
    );
    margin: 28px 0;
}

/* Streamlit overrides */
div[data-testid="metric-container"] {
    background: #0a0a0a !important;
    border: 1px solid #1f2937 !important;
    border-bottom: 2px solid #f59e0b !important;
    border-radius: 4px !important;
    padding: 14px 18px !important;
}
div[data-testid="metric-container"] label {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.62rem !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    color: #6b7280 !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    color: #f5f5f5 !important;
}

/* Input overrides */
.stTextInput input, .stNumberInput input, .stSelectbox select,
[data-baseweb="select"] div, [data-baseweb="input"] input {
    background: #0d1117 !important;
    border: 1px solid #374151 !important;
    color: #d1d5db !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.82rem !important;
    border-radius: 3px !important;
}

/* Button overrides */
.stButton > button {
    background: #f59e0b !important;
    color: #0a0a0a !important;
    border: none !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    border-radius: 3px !important;
    padding: 8px 20px !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover {
    background: #d97706 !important;
    box-shadow: 0 0 18px rgba(245,158,11,0.35) !important;
}

/* Form submit button */
.stFormSubmitButton > button {
    background: #f59e0b !important;
    color: #0a0a0a !important;
    border: none !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    width: 100% !important;
    padding: 10px !important;
}

/* Info / warning / error */
.stAlert {
    border-radius: 3px !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.78rem !important;
}

/* Caption */
.stCaption {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.68rem !important;
    color: #4b5563 !important;
    letter-spacing: 0.08em !important;
}

/* Login screen */
.login-plate {
    max-width: 440px;
    margin: 80px auto;
    background: #0a0a0a;
    border: 1px solid #1f2937;
    border-top: 3px solid #f59e0b;
    border-radius: 4px;
    padding: 40px 40px 32px 40px;
    position: relative;
}
.login-plate::before {
    content: "SECURE ACCESS TERMINAL";
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.22em;
    color: #4b5563;
    position: absolute;
    top: -9px;
    left: 20px;
    background: #0a0a0a;
    padding: 0 8px;
}
.login-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #f5f5f5;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 0 0 4px 0;
}
.login-title span { color: #f59e0b; }
.login-sub {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.68rem;
    color: #6b7280;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 28px;
}
</style>
"""


# ─── Matplotlib industrial theme ──────────────────────────────────────────────
def _apply_chart_theme() -> None:
    mpl.rcParams.update({
        "figure.facecolor": PLATE,
        "axes.facecolor":   STEEL,
        "axes.edgecolor":   GIRDER,
        "axes.labelcolor":  GHOST,
        "axes.titlecolor":  SILVER,
        "axes.titlesize":   11,
        "axes.titleweight": "bold",
        "axes.spines.top":  False,
        "axes.spines.right":False,
        "xtick.color":      GHOST,
        "ytick.color":      GHOST,
        "text.color":       SILVER,
        "grid.color":       GIRDER,
        "grid.linestyle":   "--",
        "font.family":      "monospace",
        "figure.dpi":       110,
    })


# ─── Helpers ──────────────────────────────────────────────────────────────────
def build_risk_factors(customer: dict, application: dict, probability: float) -> list[str]:
    factors: list[str] = []
    income         = float(customer.get("income_total", 0) or 0)
    credit         = float(application.get("credit_amount", 0) or 0)
    annuity        = float(application.get("annuity_amount", 0) or 0)
    family_members = int(customer.get("family_members", 1) or 1)
    owns_assets    = bool(customer.get("owns_car")) or bool(customer.get("owns_realty"))

    if income and credit / income > 3:
        factors.append("High credit amount relative to income")
    if income and annuity / income > 0.3:
        factors.append("High monthly repayment burden")
    if income < 120_000:
        factors.append("Low household income")
    if family_members >= 4:
        factors.append("Large household size")
    if not owns_assets:
        factors.append("No car or realty ownership")
    if probability >= 0.7:
        factors.append("Model confidence is strongly negative")
    elif probability >= 0.35:
        factors.append("Moderate risk profile")
    else:
        factors.append("Stable repayment profile")

    return factors[:4]


def safe_frame(items: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(items) if items else pd.DataFrame()


def fetch_all_predictions(max_rows: int = 1000) -> pd.DataFrame:
    collected: list[dict] = []
    page_size = 100
    for offset in range(0, max_rows, page_size):
        response = get_predictions(limit=page_size, offset=offset)
        items    = response.get("items", [])
        if not items:
            break
        collected.extend(items)
        if len(items) < page_size:
            break
    return safe_frame(collected)


# ─── KPI cards ────────────────────────────────────────────────────────────────
def render_kpi_cards(customers: dict, predictions: dict) -> None:
    cf = safe_frame(customers.get("items", []))
    pf = safe_frame(predictions.get("items", []))

    total_customers  = int(customers.get("total", 0) or 0)
    total_predictions = int(predictions.get("total", 0) or 0)
    avg_income = pd.to_numeric(cf.get("income_total", pd.Series(dtype=float)), errors="coerce").mean()
    avg_income = float(0 if pd.isna(avg_income) else avg_income)
    avg_prob = pd.to_numeric(pf.get("probability_default", pd.Series(dtype=float)), errors="coerce").mean()
    avg_prob = float(0 if pd.isna(avg_prob) else avg_prob)
    high_risk = int((pf.get("risk_category", pd.Series(dtype=str)) == "HIGH_RISK").sum()) if not pf.empty else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Total Customers", f"{total_customers:,}")
    with c2:
        st.metric("Total Predictions", f"{total_predictions:,}")
    with c3:
        st.metric("Average Income", f"₹{avg_income:,.0f}")
    with c4:
        st.metric("Avg Default Prob.", f"{avg_prob * 100:.1f}%")
    with c5:
        st.metric("High Risk Cases", f"{high_risk:,}")


def render_model_overview(model_info: dict, predictions: dict) -> None:
    prediction_frame = safe_frame(predictions.get("items", []))
    avg_prob = pd.to_numeric(prediction_frame.get("probability_default", pd.Series(dtype=float)), errors="coerce").mean()
    avg_prob = float(0 if pd.isna(avg_prob) else avg_prob)
    high_risk = int((prediction_frame.get("risk_category", pd.Series(dtype=str)) == "HIGH_RISK").sum()) if not prediction_frame.empty else 0
    low_risk = int((prediction_frame.get("risk_category", pd.Series(dtype=str)) == "LOW_RISK").sum()) if not prediction_frame.empty else 0
    model_name = model_info.get("model_name", "LightGBM")
    model_version = model_info.get("model_version", "unknown")
    validation_auc = model_info.get("validation_auc", "N/A")
    feature_count = model_info.get("feature_count", "N/A")

    st.markdown('<div class="section-head">Model Information & Analytics</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Model Name", str(model_name))
    with c2:
        st.metric("Version", str(model_version))
    with c3:
        st.metric("Validation AUC", f"{validation_auc:.3f}" if isinstance(validation_auc, (int, float)) else str(validation_auc))
    with c4:
        st.metric("Feature Count", str(feature_count))

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Average Default Probability", f"{avg_prob * 100:.1f}%")
    with c2:
        st.metric("Low Risk Cases", f"{low_risk:,}")
    with c3:
        st.metric("High Risk Cases", f"{high_risk:,}")

    st.caption("Model score summary is computed from the current stored prediction pool.")


def render_workflow_panel() -> None:
    st.info(
        """
        **Workflow**
        1. Open **Make Prediction** and select a customer from PostgreSQL.
        2. Enter the loan values: credit amount, annuity amount, goods price, and loan type.
        3. Click **Calculate Risk** to call FastAPI and run the model.
        4. The prediction is saved in PostgreSQL and shown in **Predictions** and **Analytics**.
        5. The dashboard reflects live model and risk statistics.
        """
    )


def render_how_to_use_page() -> None:
    st.markdown('<div class="section-head">How to Use</div>', unsafe_allow_html=True)
    st.info(
        """
        **Step-by-step**
        1. Open **Make Prediction** from the sidebar.
        2. Choose a customer from the customer list.
        3. Fill in the loan amount, repayment amount, goods price, and loan type.
        4. Press **Calculate Risk** to generate the default probability.
        5. Review the risk badge, recommendation, and stored prediction history.
        """
    )
    render_workflow_panel()


def render_model_information_page(predictions: dict) -> None:
    st.markdown('<div class="section-head">Model Information</div>', unsafe_allow_html=True)
    try:
        model_info = get_model_info()
    except Exception as exc:
        st.error(f"Unable to load model information: {exc}")
        model_info = {}

    render_model_overview(model_info, predictions)

    st.markdown('<div class="ind-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-head">Model Notes</div>', unsafe_allow_html=True)
    st.info(
        """
        This app uses the trained LightGBM pipeline loaded from the backend model artifact.
        The analytics below are computed from the predictions already stored in PostgreSQL.
        """
    )


# ─── Charts ───────────────────────────────────────────────────────────────────
def render_bar(frame: pd.DataFrame, column: str, title: str, color: str = AMBER) -> None:
    _apply_chart_theme()
    if frame.empty or column not in frame.columns:
        st.info(f"No data for {title.lower()}.")
        return
    counts = frame[column].fillna("Unknown").astype(str).value_counts().head(8)
    fig, ax = plt.subplots(figsize=(7, 3.8))
    bars = counts.sort_values().plot(kind="barh", ax=ax, color=color)
    ax.set_title(title, pad=10)
    ax.set_xlabel("Count")
    ax.tick_params(axis="y", labelsize=8)
    ax.grid(axis="x", alpha=0.15)
    # accent spine
    for spine in ax.spines.values():
        spine.set_edgecolor(GIRDER)
    ax.spines["left"].set_edgecolor(color)
    ax.spines["left"].set_linewidth(2)
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)


def render_histogram(frame: pd.DataFrame, column: str, title: str, color: str = "#14b8a6") -> None:
    _apply_chart_theme()
    if frame.empty or column not in frame.columns:
        st.info(f"No data for {title.lower()}.")
        return
    values = pd.to_numeric(frame[column], errors="coerce").dropna()
    if values.empty:
        st.info(f"No numeric values for {title.lower()}.")
        return
    fig, ax = plt.subplots(figsize=(7, 3.8))
    ax.hist(values, bins=18, color=color, edgecolor=STEEL, alpha=0.88, linewidth=0.6)
    ax.set_title(title, pad=10)
    ax.set_xlabel(column.replace("_", " ").title())
    ax.set_ylabel("Frequency")
    ax.grid(axis="y", alpha=0.15)
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
    fig, ax = plt.subplots(figsize=(5, 3.8))
    wedge_colors = [GREEN, AMBER, RED]
    wedges, texts, autotexts = ax.pie(
        counts,
        labels=counts.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=wedge_colors[: len(counts)],
        wedgeprops={"edgecolor": STEEL, "linewidth": 2},
    )
    for t in texts:
        t.set_fontsize(8)
        t.set_color(SILVER)
    for at in autotexts:
        at.set_fontsize(8)
        at.set_color(STEEL)
        at.set_fontweight("bold")
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
        return
    fig, ax = plt.subplots(figsize=(7, 3.8))
    ax.fill_between(range(1, len(values) + 1), values * 100, alpha=0.12, color=VIOLET)
    ax.plot(range(1, len(values) + 1), values * 100, linewidth=2, color=VIOLET, marker="o", markersize=3)
    ax.axhline(y=50, color=RED, linewidth=0.8, linestyle="--", alpha=0.5, label="50% threshold")
    ax.set_title("Prediction Probability Trend", pad=10)
    ax.set_xlabel("Prediction Index")
    ax.set_ylabel("Default Probability (%)")
    ax.set_ylim(0, max(100, float(values.max() * 100) + 5))
    ax.legend(fontsize=7, framealpha=0, labelcolor=GHOST)
    ax.grid(alpha=0.12)
    ax.spines["left"].set_edgecolor(VIOLET)
    ax.spines["left"].set_linewidth(2)
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)


# ─── Login ────────────────────────────────────────────────────────────────────
def login_screen() -> None:
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)
    st.markdown(
        """
        <div class="login-plate">
          <div class="login-title">Bank <span>Risk</span></div>
          <div class="login-sub">Loan Assessment System · v2.4</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.form("login_form"):
        username  = st.text_input("Username")
        password  = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Authenticate")

    if submitted:
        if username == APP_USERNAME and password == APP_PASSWORD:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Access denied — invalid credentials.")


# ─── Pages ────────────────────────────────────────────────────────────────────
def render_dashboard_page(customers: dict, predictions: dict) -> None:
    customer_frame    = safe_frame(customers.get("items", []))
    prediction_frame  = safe_frame(predictions.get("items", []))

    render_kpi_cards(customers, predictions)

    st.markdown('<div class="ind-divider"></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-head">Gender Distribution</div>', unsafe_allow_html=True)
        render_bar(customer_frame, "gender", "Customer Gender Mix", color=AMBER)
    with c2:
        st.markdown('<div class="section-head">Income Spread</div>', unsafe_allow_html=True)
        render_histogram(customer_frame, "income_total", "Income Distribution", color="#14b8a6")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-head">Education Mix</div>', unsafe_allow_html=True)
        render_bar(customer_frame, "education_type", "Education Type", color="#f97316")
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
        st.dataframe(prediction_frame, use_container_width=True, hide_index=True)
    else:
        st.info("No predictions stored yet.")


def render_customers_page(customers: dict) -> str | None:
    st.markdown('<div class="section-head">Customer Search</div>', unsafe_allow_html=True)
    search   = st.text_input("Search by Customer ID or Attribute", value="")
    st.caption("Queries filter live from PostgreSQL.")
    filtered = get_customers(query=search or None, limit=100, offset=0)
    render_customer_table(filtered.get("items", []))

    items = filtered.get("items", [])
    if not items:
        return None

    selected = st.selectbox(
        "Select customer for detailed view",
        [str(item["customer_id"]) for item in items],
    )
    return selected


def render_customer_detail_page(customer_id: str | None) -> None:
    choices = get_customers(limit=100, offset=0).get("items", [])
    if not choices:
        st.warning("No customer rows found. Seed the customers table first.")
        return

    if customer_id is None:
        customer_id = str(choices[0]["customer_id"])

    selected = get_customer(customer_id)
    customer = selected["customer"]

    left, right = st.columns([1, 1])

    with left:
        st.markdown('<div class="section-head">Customer Profile</div>', unsafe_allow_html=True)
        st.json(customer)
        st.markdown('<div class="section-head">Recent Applications</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(selected.get("recent_applications", [])), use_container_width=True, hide_index=True)
        st.markdown('<div class="section-head">Previous Predictions</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(selected.get("recent_predictions", [])), use_container_width=True, hide_index=True)

    with right:
        st.markdown('<div class="section-head">Make Prediction</div>', unsafe_allow_html=True)
        defaults = {
            "credit_amount":  227_520.0,
            "annuity_amount":  13_189.5,
            "goods_price":    180_000.0,
            "loan_type":      "Cash loans",
        }
        with st.form("risk_form"):
            credit_amount  = st.number_input("Credit Amount",  min_value=1.0, value=defaults["credit_amount"],  step=1000.0)
            annuity_amount = st.number_input("Annuity Amount", min_value=1.0, value=defaults["annuity_amount"], step=100.0)
            goods_price    = st.number_input("Goods Price",    min_value=1.0, value=defaults["goods_price"],    step=1000.0)
            loan_type      = st.selectbox("Loan Type", ["Cash loans", "Revolving loans", "Consumer loans"])
            calculate      = st.form_submit_button("Calculate Risk")

        if calculate:
            payload = {
                "credit_amount":  credit_amount,
                "annuity_amount": annuity_amount,
                "goods_price":    goods_price,
                "loan_type":      loan_type,
            }
            result  = predict_customer(customer_id, payload)
            factors = build_risk_factors(customer, payload, float(result["probability_default"]))
            render_prediction_result(result, factors)


def render_predictions_page() -> None:
    st.markdown('<div class="section-head">All Stored Predictions</div>', unsafe_allow_html=True)
    predictions = get_predictions(limit=100, offset=0)
    items = predictions.get("items", [])
    if not items:
        st.info("No predictions stored yet.")
        return
    st.dataframe(pd.DataFrame(items), use_container_width=True, hide_index=True)


def render_analytics_page() -> None:
    st.markdown('<div class="section-head">Prediction Analytics</div>', unsafe_allow_html=True)
    predictions = fetch_all_predictions()
    if predictions.empty:
        st.info("Run a few risk checks first to populate analytics.")
        return

    counts   = predictions["risk_category"].fillna("UNKNOWN").value_counts().rename_axis("risk_category").reset_index(name="count")
    avg_prob = pd.to_numeric(predictions["probability_default"], errors="coerce").mean()
    avg_prob = float(0 if pd.isna(avg_prob) else avg_prob)
    high_risk = int((predictions["risk_category"] == "HIGH_RISK").sum())

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Average Default Probability", f"{avg_prob * 100:.1f}%")
    with c2:
        st.metric("High Risk Cases", high_risk)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-head">Risk Category Distribution</div>', unsafe_allow_html=True)
        render_prediction_distribution(predictions)
    with c2:
        st.markdown('<div class="section-head">Probability Histogram</div>', unsafe_allow_html=True)
        render_histogram(predictions, "probability_default", "Default Probability Distribution", color=RED)


# ─── Entry point ──────────────────────────────────────────────────────────────
def main() -> None:
    st.set_page_config(
        page_title="Loan Risk Assessment",
        page_icon="⬡",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)

    if not st.session_state.get("authenticated"):
        login_screen()
        return

    # Hero banner
    st.markdown(
        """
        <div class="hero-banner">
          <div class="hero-title">Bank <span>Loan</span> Risk Engine</div>
          <div class="hero-sub">FastAPI · PostgreSQL · ML Prediction Pipeline</div>
          <div class="hero-status">● System Nominal</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        health = get_health()
        db_health = get_db_health()
        api_status = health.get("status", "unknown")
        db_status = db_health.get("status", "unknown")
        st.caption(f"API: {api_status}  ·  DB: {db_status}")
    except Exception:
        st.caption("API health check failed — backend may be offline.")

    page = render_navigation()

    try:
        customers = get_customers(limit=100, offset=0)
        predictions = get_predictions(limit=100, offset=0)
    except Exception as exc:
        st.error(f"Unable to reach the backend API: {exc}")
        return

    if page == "Dashboard":
        render_dashboard_page(customers, predictions)
    elif page == "Customers":
        render_customers_page(customers)
    elif page == "Make Prediction":
        selected = render_customers_page(customers)
        st.markdown('<div class="ind-divider"></div>', unsafe_allow_html=True)
        render_customer_detail_page(selected)
    elif page == "Predictions":
        render_predictions_page()
    elif page == "Analytics":
        render_analytics_page()
    elif page == "How to Use":
        render_how_to_use_page()
    elif page == "Model Information":
        render_model_information_page(predictions)


if __name__ == "__main__":
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.username = ""
    main()
