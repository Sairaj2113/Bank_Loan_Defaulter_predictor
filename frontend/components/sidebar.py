from __future__ import annotations

import streamlit as st

_SIDEBAR_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap');

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f8fbff 0%, #eef6ff 100%) !important;
    border-right: 1px solid #d8e5f4 !important;
}

[data-testid="stSidebar"][aria-expanded="false"] {
    min-width: 54px !important;
    max-width: 54px !important;
    width: 54px !important;
    transform: none !important;
    overflow: visible !important;
}

[data-testid="stSidebar"]::before {
    content: "";
    display: block;
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: linear-gradient(90deg, #38bdf8 0%, #14b8a6 50%, #60a5fa 100%);
}

[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarContent"] {
    padding-left: 8px !important;
    padding-right: 8px !important;
    overflow: hidden !important;
}

[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarHeader"] {
    justify-content: center !important;
    height: 64px !important;
    margin-bottom: 0 !important;
}

[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stLogoSpacer"],
[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarLogo"],
[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarNav"],
[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarUserContent"] {
    display: none !important;
}

[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"] {
    visibility: visible !important;
}

[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarCollapseButton"] {
    display: flex !important;
    visibility: visible !important;
    align-items: center !important;
    justify-content: center !important;
    margin-left: 0 !important;
    width: 38px !important;
    height: 38px !important;
    border-radius: 12px !important;
    background: #ffffff !important;
    border: 1px solid #bfd4ee !important;
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.10) !important;
}

[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarCollapseButton"] button {
    width: 38px !important;
    height: 38px !important;
}

[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarCollapseButton"] svg {
    transform: rotate(180deg);
}

[data-testid="stSidebar"] .stRadio label {
    font-family: 'Manrope', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    color: #17345e !important;
    letter-spacing: 0.01em !important;
    padding: 7px 0 !important;
    transition: color 0.15s ease, transform 0.15s ease;
}

[data-testid="stSidebar"] .stRadio label:hover {
    color: #1d4ed8 !important;
}

[data-testid="stSidebar"] .stRadio [data-checked="true"] + div label,
[data-testid="stSidebar"] .stRadio [aria-checked="true"] + div {
    color: #1d4ed8 !important;
}

[data-testid="stSidebar"] .stButton > button {
    background: #ffffff !important;
    border: 1px solid #bfd4ee !important;
    color: #1d4ed8 !important;
    font-family: 'Manrope', sans-serif !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    width: 100% !important;
    margin-top: 20px !important;
    padding: 10px 12px !important;
    transition: all 0.2s ease !important;
    border-radius: 12px !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: #dbeafe !important;
    border-color: #93c5fd !important;
    color: #1e40af !important;
}

.sidebar-brand {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 1.35rem;
    color: #123a73;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    padding: 8px 0 4px 0;
    border-bottom: 1px solid #cfe0f5;
    margin-bottom: 6px;
}

.sidebar-sub {
    font-family: 'Manrope', sans-serif;
    font-size: 0.78rem;
    color: #3f587a;
    letter-spacing: 0.01em;
    margin-bottom: 18px;
}

.sidebar-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, #c8d8ee 20%, #c8d8ee 80%, transparent 100%);
    margin: 16px 0;
}
</style>
"""


def render_navigation() -> str:
    st.markdown(_SIDEBAR_CSS, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown('<div class="sidebar-brand">Loan Insight</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sidebar-sub">Customer reviews, predictions, and insights</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

        page = st.radio(
            "Navigation",
            ["Dashboard", "Customers", "Make Prediction", "Predictions", "Analytics", "How to Use"],
            label_visibility="collapsed",
        )

        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.rerun()

    return page
