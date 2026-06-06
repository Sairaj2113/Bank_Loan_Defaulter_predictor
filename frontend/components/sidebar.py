# updating sidebar
from __future__ import annotations

import streamlit as st

_SIDEBAR_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap');

/* ─── SHARED BASE ─────────────────────────────────────────────────────────── */

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f8fbff 0%, #eef6ff 100%) !important;
    border-right: 1px solid #d8e5f4 !important;
}

[data-testid="stSidebar"]::before {
    content: "";
    display: block;
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: linear-gradient(90deg, #38bdf8 0%, #14b8a6 50%, #60a5fa 100%);
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


/* ─── DESKTOP  (>= 768 px) — keep the existing arrow-based behaviour ──────── */

@media (min-width: 768px) {

    [data-testid="stSidebar"][aria-expanded="false"] {
        min-width: 54px !important;
        max-width: 54px !important;
        width: 54px !important;
        transform: none !important;
        overflow: visible !important;
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

    /* Hide all sidebar body content when collapsed on desktop */
    [data-testid="stSidebar"][aria-expanded="false"] [data-testid="stLogoSpacer"],
    [data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarLogo"],
    [data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarNav"],
    [data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarUserContent"] {
        display: none !important;
    }

    /* Arrow-toggle button — always visible on desktop */
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
}


/* ─── MOBILE  (< 768 px) — hamburger overlay sidebar ─────────────────────── */

@media (max-width: 767px) {

    /* Sidebar slides in from the left as an overlay; hidden by default */
    [data-testid="stSidebar"] {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        height: 100dvh !important;
        width: 82vw !important;
        max-width: 300px !important;
        min-width: unset !important;
        z-index: 1100 !important;
        transform: translateX(-100%) !important;
        transition: transform 0.28s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: none !important;
    }

    /* When Streamlit expands the sidebar, slide it into view */
    [data-testid="stSidebar"][aria-expanded="true"] {
        transform: translateX(0) !important;
        box-shadow: 4px 0 32px rgba(15, 23, 42, 0.18) !important;
    }

    /* Dim backdrop rendered behind the open sidebar */
    [data-testid="stSidebar"][aria-expanded="true"]::after {
        content: "";
        position: fixed;
        inset: 0;
        left: 82vw;
        max-left: 300px;
        background: rgba(15, 23, 42, 0.35);
        backdrop-filter: blur(2px);
        z-index: -1;
    }

    /* Hide Streamlit's built-in arrow collapse button on mobile */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* Hamburger button — fixed to top-left of the page, always visible */
    #mobile-hamburger-btn {
        display: flex !important;
        position: fixed;
        top: 14px;
        left: 14px;
        z-index: 1200;
        width: 42px;
        height: 42px;
        border-radius: 12px;
        background: #ffffff;
        border: 1px solid #bfd4ee;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.12);
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: background 0.18s ease, box-shadow 0.18s ease;
        flex-direction: column;
        gap: 5px;
        padding: 10px;
    }

    #mobile-hamburger-btn:hover {
        background: #dbeafe;
        box-shadow: 0 6px 20px rgba(47, 111, 237, 0.18);
    }

    #mobile-hamburger-btn span {
        display: block;
        width: 20px;
        height: 2px;
        background: #1d4ed8;
        border-radius: 2px;
        transition: transform 0.22s ease, opacity 0.22s ease;
    }

    /* Animate hamburger → X when sidebar is open */
    #mobile-hamburger-btn.is-open span:nth-child(1) {
        transform: translateY(7px) rotate(45deg);
    }
    #mobile-hamburger-btn.is-open span:nth-child(2) {
        opacity: 0;
        transform: scaleX(0);
    }
    #mobile-hamburger-btn.is-open span:nth-child(3) {
        transform: translateY(-7px) rotate(-45deg);
    }

    /* Transparent full-screen close area when sidebar is open */
    #mobile-sidebar-backdrop {
        display: none;
        position: fixed;
        inset: 0;
        z-index: 1050;
        background: transparent;
    }

    #mobile-sidebar-backdrop.is-open {
        display: block;
    }
}

/* Hide hamburger on desktop */
@media (min-width: 768px) {
    #mobile-hamburger-btn {
        display: none !important;
    }
    #mobile-sidebar-backdrop {
        display: none !important;
    }
}
</style>

<!-- ── Mobile hamburger button (only visible on small screens via CSS) ──── -->
<div id="mobile-hamburger-btn" aria-label="Open navigation" role="button" tabindex="0">
    <span></span>
    <span></span>
    <span></span>
</div>

<!-- Transparent backdrop to catch outside-click closes -->
<div id="mobile-sidebar-backdrop"></div>

<script>
(function () {
    // Wait for Streamlit's DOM to stabilise
    function init() {
        var hamburger = document.getElementById('mobile-hamburger-btn');
        var backdrop  = document.getElementById('mobile-sidebar-backdrop');

        if (!hamburger || !backdrop) {
            setTimeout(init, 120);
            return;
        }

        function getSidebar() {
            return document.querySelector('[data-testid="stSidebar"]');
        }

        function isOpen() {
            var sb = getSidebar();
            return sb && sb.getAttribute('aria-expanded') === 'true';
        }

        function openSidebar() {
            // Trigger Streamlit's own collapse button to toggle state
            var btn = document.querySelector('[data-testid="stSidebarCollapseButton"] button')
                   || document.querySelector('[data-testid="collapsedControl"] button');
            if (btn) btn.click();
        }

        function syncUI() {
            if (isOpen()) {
                hamburger.classList.add('is-open');
                backdrop.classList.add('is-open');
            } else {
                hamburger.classList.remove('is-open');
                backdrop.classList.remove('is-open');
            }
        }

        // Hamburger click
        hamburger.addEventListener('click', function () {
            openSidebar();
            setTimeout(syncUI, 60);
        });

        // Keyboard accessibility
        hamburger.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                openSidebar();
                setTimeout(syncUI, 60);
            }
        });

        // Backdrop click closes sidebar
        backdrop.addEventListener('click', function () {
            if (isOpen()) {
                openSidebar(); // toggles it off
                setTimeout(syncUI, 60);
            }
        });

        // Keep hamburger icon in sync whenever Streamlit re-renders
        var observer = new MutationObserver(syncUI);
        var target = getSidebar();
        if (target) {
            observer.observe(target, { attributes: true, attributeFilter: ['aria-expanded'] });
        }

        // Initial sync
        syncUI();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
</script>
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