# sidebar.py  – fixed mobile hamburger
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


/* ════════════════════════════════════════════════════════════════════════════
   DESKTOP  (≥ 768 px)
   ════════════════════════════════════════════════════════════════════════════ */

@media (min-width: 768px) {

    /* Hide the top toolbar entirely on desktop — we use the sidebar arrow */
    [data-testid="stHeader"] {
        display: none !important;
    }

    [data-testid="stSidebar"][aria-expanded="false"] {
        min-width: 54px !important;
        max-width: 54px !important;
        width:     54px !important;
        transform: none !important;
        overflow:  visible !important;
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
        opacity: 1 !important;
        width: auto !important;
        height: auto !important;
        position: static !important;
        z-index: auto !important;
        overflow: visible !important;
    }

    [data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarCollapseButton"] {
        display: flex !important;
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

    /* Hide our custom mobile widgets on desktop */
    #mobile-hamburger-btn,
    #mobile-sidebar-backdrop {
        display: none !important;
    }
}


/* ════════════════════════════════════════════════════════════════════════════
   MOBILE  (< 768 px)
   ════════════════════════════════════════════════════════════════════════════ */

@media (max-width: 767px) {

    /* ── 1. Streamlit's top header bar
            Make it visible but style it to match our theme.
            This bar contains Streamlit's own hamburger/menu button.          */
    [data-testid="stHeader"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        z-index: 1200 !important;
        height: 3.25rem !important;
        min-height: 3.25rem !important;
        background: #ffffff !important;
        border-bottom: 1px solid #d8e5f4 !important;
        box-shadow: 0 2px 12px rgba(15, 23, 42, 0.08) !important;
        align-items: center !important;
        padding: 0 12px !important;
    }

    /* ── 2. The toolbar button row inside the header
            Make sure none of it is clipped or hidden.                        */
    [data-testid="stHeader"] > *,
    [data-testid="stHeader"] button,
    [data-testid="stHeader"] [data-testid="stToolbar"],
    [data-testid="stToolbarActions"] {
        visibility: visible !important;
        opacity: 1 !important;
        display: flex !important;
        pointer-events: auto !important;
    }

    /* ── 3. The specific "open sidebar" button that lives in the header.
            Both selector variants cover different Streamlit versions.        */
    [data-testid="stSidebarNavButton"],
    button[aria-label*="sidebar"],
    button[aria-label*="Sidebar"],
    button[kind="header"] {
        visibility: visible !important;
        opacity: 1 !important;
        display: flex !important;
        pointer-events: auto !important;
        width: 2.5rem !important;
        height: 2.5rem !important;
        min-width: 2.5rem !important;
        min-height: 2.5rem !important;
        border-radius: 10px !important;
        background: transparent !important;
        border: none !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
    }

    button[data-testid="stSidebarNavButton"]:hover,
    button[aria-label*="sidebar"]:hover {
        background: #dbeafe !important;
    }

    /* ── 4. The old collapse-button approach — hide it on mobile
            (the header bar's button is the canonical toggle here)            */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* ── 5. Sidebar overlay behaviour (unchanged from before) */
    [data-testid="stSidebar"] {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        height: 100dvh !important;
        width: 85vw !important;
        max-width: 340px !important;
        min-width: 280px !important;
        z-index: 1100 !important;
        transform: translateX(-100%) !important;
        transition: transform 0.28s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: none !important;
    }

    [data-testid="stSidebar"][aria-expanded="true"] {
        transform: translateX(0) !important;
        box-shadow: 4px 0 32px rgba(15, 23, 42, 0.18) !important;
    }

    /* ── 6. Push main content below the fixed header */
    .main .block-container {
        padding-top: 4.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* ── 7. Backdrop for closing sidebar on outside tap */
    #mobile-sidebar-backdrop {
        display: none;
        position: fixed !important;
        inset: 0 !important;
        z-index: 1050 !important;
        background: rgba(15, 23, 42, 0.35) !important;
        backdrop-filter: blur(2px) !important;
    }

    #mobile-sidebar-backdrop.is-open {
        display: block !important;
    }

    /* Hide custom hamburger on mobile — we use the native header button */
    #mobile-hamburger-btn {
        display: none !important;
    }
}
</style>

<!-- Backdrop overlay so tapping outside the sidebar closes it -->
<div id="mobile-sidebar-backdrop"></div>

<script>
(function () {
    var backdrop = null;

    function getSidebar() {
        return document.querySelector('[data-testid="stSidebar"]');
    }

    function isOpen() {
        var sb = getSidebar();
        return sb ? sb.getAttribute('aria-expanded') === 'true' : false;
    }

    function syncBackdrop() {
        if (!backdrop) return;
        if (isOpen()) {
            backdrop.classList.add('is-open');
        } else {
            backdrop.classList.remove('is-open');
        }
    }

    function closeIfOpen() {
        if (!isOpen()) return;
        /* Find and click whichever toggle button Streamlit rendered */
        var btn = (
            document.querySelector('button[data-testid="stSidebarNavButton"]') ||
            document.querySelector('[data-testid="stHeader"] button[aria-label*="sidebar"]') ||
            document.querySelector('[data-testid="stHeader"] button[aria-label*="Sidebar"]') ||
            document.querySelector('[data-testid="stHeader"] button[kind="header"]') ||
            document.querySelector('[data-testid="stSidebarCollapseButton"] button') ||
            document.querySelector('[data-testid="collapsedControl"] button')
        );
        if (btn) btn.click();
    }

    function init() {
        backdrop = document.getElementById('mobile-sidebar-backdrop');
        if (!backdrop) { setTimeout(init, 100); return; }

        backdrop.addEventListener('click', function () {
            closeIfOpen();
            setTimeout(syncBackdrop, 80);
        });

        /* Watch aria-expanded so backdrop tracks sidebar state */
        var observer = new MutationObserver(syncBackdrop);
        var sb = getSidebar();
        if (sb) observer.observe(sb, { attributes: true, attributeFilter: ['aria-expanded'] });

        /* Re-wire after Streamlit re-renders */
        new MutationObserver(function () {
            var sb2 = getSidebar();
            if (sb2) observer.observe(sb2, { attributes: true, attributeFilter: ['aria-expanded'] });
            syncBackdrop();
        }).observe(document.body, { childList: true, subtree: false });

        syncBackdrop();
    }

    document.readyState === 'loading'
        ? document.addEventListener('DOMContentLoaded', init)
        : init();
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

    return page