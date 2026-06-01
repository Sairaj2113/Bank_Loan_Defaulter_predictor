from __future__ import annotations

import streamlit as st

_SIDEBAR_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Share+Tech+Mono&display=swap');

[data-testid="stSidebar"] {
    background: #0a0a0a !important;
    border-right: 2px solid #f59e0b !important;
}

[data-testid="stSidebar"]::before {
    content: "";
    display: block;
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: repeating-linear-gradient(
        90deg,
        #f59e0b 0px, #f59e0b 12px,
        transparent 12px, transparent 18px
    );
}

[data-testid="stSidebar"] .stRadio label {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.82rem !important;
    color: #9ca3af !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    padding: 6px 0 !important;
    transition: color 0.15s ease;
}

[data-testid="stSidebar"] .stRadio label:hover {
    color: #f59e0b !important;
}

[data-testid="stSidebar"] .stRadio [data-checked="true"] + div label,
[data-testid="stSidebar"] .stRadio [aria-checked="true"] + div {
    color: #f59e0b !important;
}

[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: 1px solid #ef4444 !important;
    color: #ef4444 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    width: 100% !important;
    margin-top: 20px !important;
    padding: 8px 12px !important;
    transition: all 0.2s ease !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: #ef4444 !important;
    color: #0a0a0a !important;
}

.sidebar-brand {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    font-size: 1.3rem;
    color: #f59e0b;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 8px 0 4px 0;
    border-bottom: 1px solid #1f2937;
    margin-bottom: 6px;
}

.sidebar-sub {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.68rem;
    color: #4b5563;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 18px;
}

.sidebar-divider {
    height: 1px;
    background: repeating-linear-gradient(
        90deg,
        #1f2937 0px, #1f2937 6px,
        transparent 6px, transparent 10px
    );
    margin: 16px 0;
}
</style>
"""


def render_navigation() -> str:
    st.markdown(_SIDEBAR_CSS, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown('<div class="sidebar-brand">⬡ RiskEngine</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-sub">Streamlit · FastAPI · PostgreSQL</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

        page = st.radio(
            "Navigation",
            ["Dashboard", "Customers", "Make Prediction", "Predictions", "Analytics", "How to Use", "Model Information"],
            label_visibility="collapsed",
        )

        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

        if st.button("⏻  Logout"):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.rerun()

    return page
