from __future__ import annotations

import pandas as pd
import streamlit as st

_TABLE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600&display=swap');

[data-testid="stDataFrame"] {
    border: 1px solid #d7e3f3 !important;
    border-radius: 16px !important;
    overflow: hidden !important;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05) !important;
}

[data-testid="stDataFrame"] table {
    font-family: 'Manrope', sans-serif !important;
    font-size: 0.86rem !important;
    background: #ffffff !important;
}

[data-testid="stDataFrame"] thead th {
    background: linear-gradient(135deg, #eff6ff 0%, #eefcf9 100%) !important;
    color: #2453a7 !important;
    font-size: 0.73rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid #cddff2 !important;
    padding: 12px 14px !important;
}

[data-testid="stDataFrame"] tbody tr:nth-child(even) {
    background: #f8fbff !important;
}

[data-testid="stDataFrame"] tbody tr:nth-child(odd) {
    background: #ffffff !important;
}

[data-testid="stDataFrame"] tbody tr:hover td {
    background: #edf5ff !important;
    color: #1f3d75 !important;
}

[data-testid="stDataFrame"] tbody td {
    color: #364152 !important;
    border-bottom: 1px solid #e7eef8 !important;
    padding: 9px 14px !important;
}
</style>
"""


def _stringify(value: object, fallback: str = "Unknown") -> str:
    if value is None:
        return fallback
    text_value = str(value).strip()
    return text_value if text_value else fallback


def _format_currency(value: object) -> str:
    try:
        return f"Rs. {float(value):,.0f}"
    except (TypeError, ValueError):
        return "Rs. 0"


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


def customer_display_label(item: dict) -> str:
    parts = [
        _stringify(item.get("family_status"), "Family status unknown"),
        _stringify(item.get("occupation_type"), "Occupation unknown"),
        _stringify(item.get("education_type"), "Education unknown"),
    ]
    return " | ".join(parts)


def customer_summary_frame(item: dict) -> pd.DataFrame:
    rows = [
        ("Gender", _stringify(item.get("gender"))),
        ("Education", _stringify(item.get("education_type"))),
        ("Family status", _stringify(item.get("family_status"))),
        ("Housing", _stringify(item.get("housing_type"))),
        ("Occupation", _stringify(item.get("occupation_type"))),
        ("Income", _format_currency(item.get("income_total"))),
        ("Children", int(item.get("cnt_children", 0) or 0)),
        ("Family members", int(item.get("family_members", 0) or 0)),
        ("Assets", _asset_label(item)),
    ]
    return pd.DataFrame(rows, columns=["Field", "Value"])


def customers_dataframe(items: list[dict]) -> pd.DataFrame:
    if not items:
        return pd.DataFrame(
            columns=[
                "Customer profile",
                "Gender",
                "Education",
                "Family status",
                "Housing",
                "Occupation",
                "Income",
                "Children",
                "Family members",
                "Assets",
            ]
        )

    rows = []
    for item in items:
        rows.append(
            {
                "Customer profile": customer_display_label(item),
                "Gender": _stringify(item.get("gender")),
                "Education": _stringify(item.get("education_type")),
                "Family status": _stringify(item.get("family_status")),
                "Housing": _stringify(item.get("housing_type")),
                "Occupation": _stringify(item.get("occupation_type")),
                "Income": _format_currency(item.get("income_total")),
                "Children": int(item.get("cnt_children", 0) or 0),
                "Family members": int(item.get("family_members", 0) or 0),
                "Assets": _asset_label(item),
            }
        )
    return pd.DataFrame(rows)


def render_customer_table(items: list[dict]) -> None:
    st.markdown(_TABLE_CSS, unsafe_allow_html=True)
    frame = customers_dataframe(items)
    st.dataframe(frame, use_container_width=True, hide_index=True)
