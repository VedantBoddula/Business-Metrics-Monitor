import os
import hmac
import textwrap

import streamlit as st
from dotenv import load_dotenv

load_dotenv(override=True)


# ---------------------------------------------------------------------------
# Design tokens
#   ink     #0E1A2B  left panel, primary button
#   canvas  #EDF0F5  page background
#   paper   #FFFFFF  form panel
#   line    #C9D2DF  input and divider borders
#   accent  #1F5FD6  focus and hover
#   alert   #F2A33A  the flagged anomaly (used once, on purpose)
# ---------------------------------------------------------------------------

LOGIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

:root {
    --ink: #0E1A2B;
    --ink-soft: #9FB0C8;
    --canvas: #EDF0F5;
    --paper: #FFFFFF;
    --line: #C9D2DF;
    --text: #142033;
    --muted: #5B6B82;
    --accent: #1F5FD6;
    --alert: #F2A33A;
}

html, body, .stApp {
    font-family: 'IBM Plex Sans', -apple-system, 'Segoe UI', Roboto, sans-serif;
}

/* Page chrome */
.stApp { background: var(--canvas); }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"],
[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
#MainMenu,
footer { display: none !important; }

.block-container {
    max-width: 1080px;
    padding: 1.5rem 1.5rem 2rem;
}

/* Shell: one rounded surface holding both panels */
.st-key-login_shell {
    margin-top: 5vh;
    gap: 0;
    border-radius: 16px;
    overflow: hidden;
    background: var(--paper);
    box-shadow: 0 1px 2px rgba(14, 26, 43, .06),
                0 16px 48px rgba(14, 26, 43, .12);
}
.st-key-login_shell [data-testid="stHorizontalBlock"] {
    gap: 0;
    align-items: stretch;
}

/* Left panel */
.st-key-login_shell [data-testid="stColumn"]:first-child,
.st-key-login_shell [data-testid="column"]:first-child {
    background: var(--ink);
    padding: 2.75rem 2.5rem;
}

/* Right panel */
.st-key-login_shell [data-testid="stColumn"]:last-child,
.st-key-login_shell [data-testid="column"]:last-child {
    background: var(--paper);
    padding: 3rem 3.25rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

/* Left panel content */
.brand-row {
    display: flex;
    align-items: center;
    gap: 10px;
    color: #F4F7FB;
    font-weight: 600;
    font-size: 1rem;
    margin-bottom: 2.5rem;
}
.brand-mark {
    width: 28px;
    height: 28px;
    border-radius: 7px;
    background: #1B2D49;
    border: 1px solid #2B4166;
    display: grid;
    place-items: center;
}
.hero-title,
h1.hero-title,
[data-testid="stMarkdownContainer"] h1.hero-title,
.st-key-login_shell [data-testid="column"]:first-child h1,
.st-key-login_shell [data-testid="stColumn"]:first-child h1 {
    color: #F4F7FB !important;
    -webkit-text-fill-color: #F4F7FB !important;
    font-size: clamp(1.6rem, 2.6vw, 2.1rem);
    font-weight: 600;
    line-height: 1.22;
    letter-spacing: -0.015em;
    margin: 0 0 0.75rem;
}
.hero-text {
    color: var(--ink-soft);
    font-size: 0.97rem;
    line-height: 1.6;
    margin: 0 0 1.75rem;
    max-width: 34ch;
}
.chart-wrap { margin: 0 0 1.75rem; }
.chart-wrap svg { width: 100%; height: auto; display: block; }
.points {
    list-style: none;
    margin: 0;
    padding: 0;
    color: #C9D5E6;
    font-size: 0.92rem;
    line-height: 1.5;
}
.points li {
    padding: 0.6rem 0;
    border-top: 1px solid #1F3250;
}
.points li:last-child { border-bottom: 1px solid #1F3250; }

/* Anomaly marker: the one animated element on the page */
.pulse-ring {
    transform-box: fill-box;
    transform-origin: center;
    animation: pulse 2.4s ease-out infinite;
}
@keyframes pulse {
    0%   { transform: scale(.6); opacity: .55; }
    100% { transform: scale(1.8); opacity: 0; }
}
@media (prefers-reduced-motion: reduce) {
    .pulse-ring { animation: none; opacity: .25; }
}

/* Right panel content */
.form-title {
    color: var(--text);
    font-size: 1.65rem;
    font-weight: 600;
    letter-spacing: -0.01em;
    margin: 0 0 0.4rem;
}
.form-sub {
    color: var(--muted);
    font-size: 0.95rem;
    line-height: 1.5;
    margin: 0 0 1.75rem;
}
.form-foot {
    color: var(--muted);
    font-size: 0.83rem;
    line-height: 1.5;
    margin-top: 1.5rem;
    padding-top: 1rem;
    border-top: 1px solid #E3E8F0;
}

/* Form fields */
[data-testid="stForm"] {
    border: 0 !important;
    padding: 0 !important;
    background: transparent !important;
}
div[data-testid="stTextInput"] { margin-bottom: 0.4rem; }
div[data-testid="stTextInput"] label p {
    color: var(--text) !important;
    font-size: 0.88rem;
    font-weight: 500;
}
div[data-testid="stTextInput"] div[data-baseweb="input"] {
    background: var(--paper) !important;
    border: 1px solid var(--line) !important;
    border-radius: 8px !important;
    min-height: 42px !important;
    transition: border-color .15s ease, box-shadow .15s ease;
}
div[data-testid="stTextInput"] div[data-baseweb="input"] > div {
    background: transparent !important;
}
div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(31, 95, 214, .18) !important;
}
div[data-testid="stTextInput"] input {
    color: var(--text) !important;
    -webkit-text-fill-color: var(--text) !important;
    background: transparent !important;
    font-size: 0.95rem;
}
div[data-testid="stTextInput"] input::placeholder {
    color: #8A98AD !important;
    -webkit-text-fill-color: #8A98AD !important;
}

/* Password Eye Button and Icon Ligature Guarantee */
div[data-testid="stTextInput"] button {
    color: var(--muted) !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 8px !important;
    cursor: pointer !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}
div[data-testid="stTextInput"] button:hover {
    color: var(--accent) !important;
}
div[data-testid="stTextInput"] button *,
div[data-testid="stTextInput"] button span,
div[data-testid="stTextInput"] button [class*="material-symbols"] {
    font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
    font-size: 20px !important;
    font-style: normal !important;
    letter-spacing: normal !important;
    line-height: 1 !important;
    text-transform: none !important;
    white-space: nowrap !important;
    word-wrap: normal !important;
    direction: ltr !important;
    -webkit-font-feature-settings: 'liga' 1 !important;
    font-feature-settings: 'liga' 1 !important;
    -webkit-font-smoothing: antialiased !important;
}

[data-testid="InputInstructions"] { display: none !important; }

/* Submit button */
div[data-testid="stFormSubmitButton"] {
    width: 100% !important;
    margin-top: 0.85rem !important;
}
div[data-testid="stFormSubmitButton"] button {
    width: 100% !important;
    min-height: 42px !important;
    height: 42px !important;
    border: 0 !important;
    border-radius: 8px !important;
    background: var(--ink) !important;
    transition: background-color .15s ease;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-sizing: border-box !important;
}
div[data-testid="stFormSubmitButton"] button p {
    color: #FFFFFF !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    margin: 0 !important;
    padding: 0 !important;
}
div[data-testid="stFormSubmitButton"] button:hover { background: var(--accent) !important; }
div[data-testid="stFormSubmitButton"] button:focus-visible {
    outline: 3px solid rgba(31, 95, 214, .35) !important;
    outline-offset: 2px !important;
}

/* Error / warning messages */
[data-testid="stAlert"] {
    border-radius: 8px;
    margin-top: 0.75rem;
}

/* Small screens: panels stack */
@media (max-width: 760px) {
    .block-container { padding: 0.75rem; }
    .st-key-login_shell { margin-top: 1vh; }
    .st-key-login_shell [data-testid="stColumn"]:first-child,
    .st-key-login_shell [data-testid="column"]:first-child {
        padding: 1.75rem 1.5rem;
    }
    .st-key-login_shell [data-testid="stColumn"]:last-child,
    .st-key-login_shell [data-testid="column"]:last-child {
        padding: 1.75rem 1.5rem 2rem;
    }
    .chart-wrap, .points { display: none; }
    .hero-text { margin-bottom: 0; }
}
</style>
"""

HERO_HTML = """
<div class="brand-row">
  <span class="brand-mark">
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path d="M1.5 11 5 7l3 2.5L14 3" stroke="#F4F7FB" stroke-width="1.6"
            stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  </span>
  Business Metrics Monitor
</div>
<h1 class="hero-title" style="color: #F4F7FB !important; -webkit-text-fill-color: #F4F7FB !important;">Catch unusual changes in your metrics early.</h1>
<p class="hero-text">
  Track key business numbers, see what moved outside the normal range,
  and send reports to your team.
</p>
<div class="chart-wrap">
  <svg viewBox="0 0 400 190" role="img"
       aria-label="Line chart of a metric with one spike flagged as unusual">
    <g stroke="#1F3250" stroke-width="1">
      <line x1="0" y1="40"  x2="400" y2="40"/>
      <line x1="0" y1="90"  x2="400" y2="90"/>
      <line x1="0" y1="140" x2="400" y2="140"/>
      <line x1="0" y1="180" x2="400" y2="180"/>
    </g>
    <path d="M0,104 L390,82 L390,120 L0,142 Z" fill="#1B2D49" opacity=".85"/>
    <path d="M0,120 L30,112 L60,118 L90,106 L120,112 L150,100 L180,108
             L210,98 L240,104 L270,34 L300,96 L330,102 L360,94 L390,100"
          fill="none" stroke="#7FA6F0" stroke-width="2"
          stroke-linejoin="round" stroke-linecap="round"/>
    <circle class="pulse-ring" cx="270" cy="34" r="11" fill="#F2A33A"/>
    <circle cx="270" cy="34" r="5" fill="#F2A33A"/>
    <text x="256" y="38" text-anchor="end" fill="#F2A33A"
          font-size="12" font-weight="600">Unusual spike</text>
    <text x="0" y="168" fill="#6F83A3" font-size="11">Shaded area: expected range</text>
  </svg>
</div>
<ul class="points">
  <li>See business metrics in one place</li>
  <li>Get unusual values flagged automatically</li>
  <li>Email reports whenever you need them</li>
</ul>
"""

FORM_HEADER_HTML = """
<h2 class="form-title">Sign in</h2>
<p class="form-sub">Use your admin account to open the dashboard.</p>
"""

FORM_FOOT_HTML = """
<div class="form-foot">Authorized administrators only.</div>
"""


def _html(markup: str) -> None:
    """Render HTML without Markdown treating indented lines as code."""
    st.markdown(textwrap.dedent(markup).strip(), unsafe_allow_html=True)


def _safe_equal(supplied: str, expected: str) -> bool:
    """Constant-time comparison that is safe for non-ASCII input."""
    if not expected:
        return False
    return hmac.compare_digest(
        supplied.encode("utf-8"), expected.encode("utf-8")
    )


def admin_login() -> bool:
    if st.session_state.get("authenticated", False):
        return True

    _html(LOGIN_CSS)

    with st.container(key="login_shell"):
        left, right = st.columns([1.05, 1], gap="small")

        with left:
            _html(HERO_HTML)

        with right:
            _html(FORM_HEADER_HTML)

            with st.form("admin_login_form", clear_on_submit=False):
                username = st.text_input(
                    "Username",
                    placeholder="Enter your username",
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password",
                )
                submitted = st.form_submit_button(
                    "Sign in",
                    use_container_width=True,
                )

            if submitted:
                admin_username = os.getenv("ADMIN_USERNAME", "")
                admin_password = os.getenv("ADMIN_PASSWORD", "")

                if not admin_username or not admin_password:
                    st.warning(
                        "Admin credentials are not set. Add ADMIN_USERNAME "
                        "and ADMIN_PASSWORD to your .env file."
                    )
                else:
                    valid_username = _safe_equal(username, admin_username)
                    valid_password = _safe_equal(password, admin_password)

                    if valid_username and valid_password:
                        st.session_state["authenticated"] = True
                        st.rerun()
                    else:
                        st.error(
                            "Username or password is incorrect. "
                            "Check both and try again."
                        )

            _html(FORM_FOOT_HTML)

    return st.session_state.get("authenticated", False)


LOGOUT_CSS = """
<style>
[data-testid="stAppDeployButton"] { display: none !important; }

.st-key-logout_bar {
    position: fixed;
    top: 16px;
    right: 155px;
    z-index: 999999;
    width: auto;
}
.st-key-logout_bar button {
    background: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 6px !important;
    min-height: 28px !important;
    height: 28px !important;
    padding: 0 12px !important;
    box-shadow: 0 1px 2px rgba(14, 26, 43, 0.04) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.15s ease !important;
}
.st-key-logout_bar button p,
.st-key-logout_bar button span,
.st-key-logout_bar button * {
    color: #0E1A2B !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1 !important;
}
.st-key-logout_bar button:hover {
    background: #FEF2F2 !important;
    border-color: #FCA5A5 !important;
}
.st-key-logout_bar button:hover p,
.st-key-logout_bar button:hover span,
.st-key-logout_bar button:hover * {
    color: #DC2626 !important;
}
.st-key-logout_bar button:focus-visible {
    outline: 2px solid rgba(220, 38, 38, .35) !important;
    outline-offset: 1px !important;
}
</style>
"""


def admin_logout() -> None:
    _html(LOGOUT_CSS)

    with st.container(key="logout_bar"):
        if st.button(
            "Sign out",
            key="admin_logout_topbar",
            type="secondary",
            help="Sign out of the admin dashboard",
        ):
            st.session_state["authenticated"] = False
            st.rerun()