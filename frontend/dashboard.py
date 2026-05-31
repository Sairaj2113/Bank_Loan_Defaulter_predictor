from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

DEMO_CLIENT = {
    "customer": {
        "customer_id": "demo-customer-001",
        "gender": "F",
        "owns_car": False,
        "owns_realty": False,
        "income_total": 90000.0,
        "education_type": "Higher education",
        "family_status": "Married",
        "housing_type": "House / apartment",
        "occupation_type": "Laborers",
        "cnt_children": 2,
        "family_members": 4,
    },
    "application": {
        "application_id": "demo-application-001",
        "credit_amount": 227520.0,
        "annuity_amount": 13189.5,
        "goods_price": 180000.0,
        "loan_type": "Cash loans",
    },
}


def call_prediction_api(payload: dict) -> dict:
    request = Request(
        f"{BACKEND_URL.rstrip('/')}/predict",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def load_demo_payload() -> dict:
    return json.loads(json.dumps(DEMO_CLIENT))


st.set_page_config(page_title="Loan Risk Dashboard", page_icon="🏦", layout="wide")

st.markdown(
    """
    <style>
      .hero {
        padding: 24px;
        border-radius: 20px;
        background: linear-gradient(135deg, #0f172a, #1e293b 60%, #334155);
        color: white;
        margin-bottom: 24px;
      }
      .hint {
        color: #64748b;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1 style="margin:0;">Loan Risk Assessment Dashboard</h1>
      <p style="margin:8px 0 0 0;">Hardcoded demo client with live prediction from the frozen LightGBM model.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption("Backend: " + BACKEND_URL)

with st.sidebar:
    st.subheader("Demo Flow")
    st.write("1. Edit the sample client.")
    st.write("2. Send it to FastAPI.")
    st.write("3. Read the predicted default risk.")
    if st.button("Restore demo client"):
        st.session_state.demo = load_demo_payload()
        st.rerun()

demo = st.session_state.get("demo", load_demo_payload())

left, right = st.columns([1.1, 0.9], gap="large")

with left:
    with st.form("loan_prediction_form"):
        st.subheader("Customer Data")
        customer = demo["customer"]
        application = demo["application"]

        customer_id = st.text_input("Customer ID", value=customer["customer_id"] or "")
        gender = st.selectbox("Gender", ["F", "M", "XNA"], index=["F", "M", "XNA"].index(customer["gender"]))
        owns_car = st.checkbox("Owns Car", value=bool(customer["owns_car"]))
        owns_realty = st.checkbox("Owns Realty", value=bool(customer["owns_realty"]))
        income_total = st.number_input("Income Total", min_value=1.0, value=float(customer["income_total"]), step=1000.0)
        education_type = st.selectbox(
            "Education Type",
            [
                "Secondary / secondary special",
                "Higher education",
                "Incomplete higher",
                "Lower secondary",
                "Academic degree",
            ],
            index=1,
        )
        family_status = st.selectbox(
            "Family Status",
            ["Married", "Single / not married", "Civil marriage", "Separated", "Widow"],
            index=0,
        )
        housing_type = st.selectbox(
            "Housing Type",
            ["House / apartment", "With parents", "Municipal apartment", "Rented apartment", "Office apartment"],
            index=0,
        )
        occupation_type = st.text_input("Occupation Type", value=customer["occupation_type"])
        cnt_children = st.number_input("Children", min_value=0, value=int(customer["cnt_children"]), step=1)
        family_members = st.number_input("Family Members", min_value=1, value=int(customer["family_members"]), step=1)

        st.subheader("Loan Application")
        application_id = st.text_input("Application ID", value=application["application_id"] or "")
        credit_amount = st.number_input("Credit Amount", min_value=1.0, value=float(application["credit_amount"]), step=1000.0)
        annuity_amount = st.number_input("Annuity Amount", min_value=1.0, value=float(application["annuity_amount"]), step=100.0)
        goods_price = st.number_input("Goods Price", min_value=1.0, value=float(application["goods_price"]), step=1000.0)
        loan_type = st.selectbox("Loan Type", ["Cash loans", "Revolving loans", "Consumer loans"], index=0)
        submitted = st.form_submit_button("Predict risk")

if submitted:
    payload = {
        "customer": {
            "customer_id": customer_id or None,
            "gender": gender,
            "owns_car": owns_car,
            "owns_realty": owns_realty,
            "income_total": income_total,
            "education_type": education_type,
            "family_status": family_status,
            "housing_type": housing_type,
            "occupation_type": occupation_type,
            "cnt_children": int(cnt_children),
            "family_members": int(family_members),
        },
        "application": {
            "application_id": application_id or None,
            "credit_amount": credit_amount,
            "annuity_amount": annuity_amount,
            "goods_price": goods_price,
            "loan_type": loan_type,
        },
    }
    st.session_state.demo = payload

    try:
        result = call_prediction_api(payload)
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        st.error(f"Prediction request failed: {exc}")
    else:
        st.subheader("Prediction Result")
        top_left, top_right = st.columns(2)
        with top_left:
            st.metric("Probability of default", f"{result['probability_default']:.3f}")
        with top_right:
            st.metric("Risk category", result["risk_category"])
        st.success(f"Recommendation: {result['recommendation']}")
        st.caption(f"Model version: {result['model_version']}")

with right:
    st.subheader("Demo Client Snapshot")
    st.json(demo)
    st.markdown(
        """
        <p class="hint">
        This demo uses a single hardcoded client shaped from the training data so you can verify the UI and model flow
        before PostgreSQL is added.
        </p>
        """,
        unsafe_allow_html=True,
    )
