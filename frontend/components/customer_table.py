from __future__ import annotations

import pandas as pd
import streamlit as st

_TABLE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

[data-testid="stDataFrame"] {
    border: 1px solid #1f2937 !important;
    border-radius: 4px !important;
    overflow: hidden !important;
}

[data-testid="stDataFrame"] table {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.78rem !important;
    background: #0d1117 !important;
}

[data-testid="stDataFrame"] thead th {
    background: #111827 !important;
    color: #f59e0b !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border-bottom: 2px solid #f59e0b !important;
    padding: 10px 14px !important;
}

[data-testid="stDataFrame"] tbody tr:nth-child(even) {
    background: #0d1117 !important;
}

[data-testid="stDataFrame"] tbody tr:nth-child(odd) {
    background: #111827 !important;
}

[data-testid="stDataFrame"] tbody tr:hover td {
    background: #1c2434 !important;
    color: #f59e0b !important;
}

[data-testid="stDataFrame"] tbody td {
    color: #9ca3af !important;
    border-bottom: 1px solid #1f2937 !important;
    padding: 8px 14px !important;
}
</style>
"""


def customers_dataframe(items: list[dict]) -> pd.DataFrame:
    if not items:
        return pd.DataFrame(columns=["customer_id", "gender", "income_total", "occupation_type", "created_at"])

    frame = pd.DataFrame(items)
    columns = [c for c in ["customer_id", "gender", "income_total", "occupation_type", "created_at"] if c in frame.columns]
    frame = frame[columns].copy()
    if "income_total" in frame.columns:
        frame["income_total"] = frame["income_total"].round(2)
    return frame


def render_customer_table(items: list[dict]) -> None:
    st.markdown(_TABLE_CSS, unsafe_allow_html=True)
    frame = customers_dataframe(items)
    st.dataframe(frame, use_container_width=True, hide_index=True)